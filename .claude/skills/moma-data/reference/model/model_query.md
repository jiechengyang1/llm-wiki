# 通过数据模型 api 获取数据标准流程

> 基于 modelId + dimensions / measures / filter 等条件查询模型数据。
> 上游有 4 类集群（默认公共 / 金融 / 人力 / 高密），但**查询侧只分两条路径**：
> 仅 `secret` 走独立高密 Host，其余共用默认公共 Host —— 因此 `odin_cluster` 只有 `public` / `high_confidential` 两个取值。

## 指令

从资产命中时在同一条指令里带上 `asset_id`，传入后使用资产创建人的 ucid 发起查询：

```bash
moma moma-data api POST_moma-data_odin_model_query --json -d '{"modelId":12345,"asset_id":821,"odin_cluster":"public","query":{"dimensions":[{"columnId":101,"alias":"统计日期"},{"columnId":202,"alias":"新签单量"}],"measures":[],"page":{"pageNo":1,"pageSize":100}}}'
```

不是从资产来的模型查询不要传 `asset_id`：

```bash
moma moma-data api POST_moma-data_odin_model_query --json -d '{"modelId":12345,"query":{"dimensions":[{"columnId":101,"alias":"统计日期"},{"columnId":202,"alias":"新签单量"}],"measures":[],"page":{"pageNo":1,"pageSize":100}}}'
```

## 指令参数说明

-d modelId:           模型 ID (必传)
-d query:             查询参数对象 (必传)
-d query.dimensions:  维度列对象数组，元素形态 `{columnId:int, alias:string}` (选传)
-d query.measures:    指标/度量列对象数组，元素形态 `{columnId:int, alias:string, agg:string}`；**`agg` 在 measures 非空时必填**；默认会平移到 dimensions 取明细 (选传)
-d query.filter:      过滤条件，**嵌套节点树**，节点结构详见下文 (选传)
-d query.orderBy:     排序列表，元素 `{columnId:int, direction:"ASC"|"DESC"}` (选传)
-d query.page:        分页对象，含 `pageNo` / `pageSize`，默认 1 / 1000 (选传)
-d odin_cluster:      模型集群：`public`（默认）| `high_confidential` (选传)
-d asset_id:          资产 ID。从资产命中时必传，传入后使用资产创建人的 ucid 发起查询，避免因当前用户无直接访问权限导致失败；不是从资产来的查询不传

### `dimensions` / `measures` 元素结构

上游 ColumnRef 协议固定，列名解析以 `alias` 为准，**上游不识别 `columnCode` 这种自定义字段**：

| 字段        | 类型   | 必填           | 取值                                                                 |
|-------------|--------|----------------|----------------------------------------------------------------------|
| `columnId`  | long   | 是（与 code/name 三选一） | 来自 `model_columns` 返回的 `modelColumnId`（不是 `oColumnInfo.column_id`） |
| `alias`     | string | 否             | 结果集列别名，推荐取 `model_columns` 的 `modelColumnName`            |
| `agg`       | string | **measures 必填** | 聚合函数；可选值 `SUM` / `AVG` / `COUNT` / `COUNT_DISTINCT` / `MAX` / `MIN` / `NONE` |

⚠️ `dimensions` 没有 `agg`；`measures` 必须带 `agg`。

### 度量作为维度（默认行为）

上游 `measures[].agg` 为必填，强制聚合。当业务只需取明细、不希望聚合时，**标准做法是把所有 `measures` 平移到 `dimensions`，并保持 `measures: []`**。

- 原因：`measures` 非空即触发上游按 `agg` 做汇总；不填 `agg` 会直接报错。把 measure 平移到 `dimensions` 相当于按明细列展开而不做聚合。
- 仅当需要按某个聚合函数（`SUM/AVG/COUNT/...`）做汇总时，才显式保留 `measures` 并填好 `agg`。

### `filter` 嵌套过滤树（推荐）

`query.filter` 是一棵节点树，节点分两类：**分组节点**用 `logic` + `items`；**条件节点（叶子）** 用 `columnId` + `op` + `values`。
**根节点必须是分组节点**（`logic=AND/OR`），条件节点只能作为分组节点的子节点出现。

| 字段        | 类型               | 必填                       | 用途                                                                 |
|-------------|--------------------|----------------------------|----------------------------------------------------------------------|
| `logic`     | string             | 分组节点必填               | 分组节点取 `AND` / `OR`；条件节点填 `VALUE` 或留空                    |
| `items`     | array<FilterNode>  | 仅 `logic=AND/OR` 时使用   | 分组节点的子节点列表（条件节点上不要带）                              |
| `columnId`  | long               | **仅条件节点使用**         | 过滤列 Id（columnId / code / name 三选一，推荐 columnId）；分组节点上不要带 |
| `op`        | string             | 条件节点必填               | 操作符：`EQ` / `NQ` / `GT` / `LT` / `GE` / `LE` / `BETWEEN` / `INCLUDE` / `EXCLUDE` / `LIKE` |
| `values`    | array              | 条件节点必填               | 过滤值列表                                                            |

> 节点类型互斥：分组节点只带 `logic` + `items`；条件节点只带 `columnId` + `op` + `values`（可选 `logic="VALUE"`）。
> 字段混用（如分组节点上也写 `columnId`，或条件节点上也写 `items`）属于非法 schema。

`filter` 也可换为 `filters`（数组形态），两者二选一，推荐嵌套树。

### `odin_cluster` 说明

- **取值来源**：必须使用 `model_list` 返回的 `odinCluster` 派生字段，**严禁自行判断或猜测**。
- **上游 4 类 clusterType 已在 list 服务侧合并**：

  | 上游 clusterType            | list 返回的 odinCluster | 查询 Host                     |
  |-----------------------------|-------------------------|-------------------------------|
  | `default` / `finance` / `hfc` | `public`              | `ODIN_DATA_MODEL_QUERY_HOST`  |
  | `secret`                    | `high_confidential`     | `ODIN_DATA_MODEL_HC_QUERY_HOST` |

- **兼容**：直接传 `default` / `finance` / `hfc` / `secret` 后端也会归一化，但仍**推荐**透传 list 的 `odinCluster`。
- **高密约束**：`high_confidential` 需当前用户在高密白名单内；未配置 HC Host 或不在白名单时接口直接返回错误。
- 不传时默认 `public`。

ucId（行级权限）始终使用当前登录人；useUcId（数据使用权限）若传入 asset_id 则使用资产创建人，否则使用当前登录人，无需手动传入。

## 指令使用示例

### 明细取数（推荐 / 默认）：所有字段（含 measure）都放在 dimensions

```bash
# 假设 model_columns 返回：
#   modelColumnId=101 column_code=performance_city_abbr_name modelColumnName=城市
#   modelColumnId=202 column_code=new_sign_cnt              modelColumnName=新签单量
moma moma-data api POST_moma-data_odin_model_query --json -d '{
  "modelId": 12345,
  "query": {
    "dimensions": [
      {"columnId": 101, "alias": "城市"},
      {"columnId": 202, "alias": "新签单量"}
    ],
    "measures": [],
    "filter": {
      "logic": "AND",
      "items": [
        {"columnId": 101, "op": "INCLUDE", "values": ["武汉"]}
      ]
    },
    "page": {"pageNo": 1, "pageSize": 100}
  }
}'
```

### 聚合取数：measures 必须带 agg

```bash
moma moma-data api POST_moma-data_odin_model_query --json -d '{
  "modelId": 12345,
  "query": {
    "dimensions": [
      {"columnId": 101, "alias": "城市"}
    ],
    "measures": [
      {"columnId": 202, "alias": "新签单量合计", "agg": "SUM"}
    ],
    "orderBy": [
      {"columnId": 202, "direction": "DESC"}
    ],
    "page": {"pageNo": 1, "pageSize": 100}
  }
}'
```

### 嵌套 filter：AND/OR 组合多个条件

```bash
moma moma-data api POST_moma-data_odin_model_query --json -d '{
  "modelId": 12345,
  "query": {
    "dimensions": [{"columnId": 101, "alias": "城市"}],
    "measures":   [{"columnId": 202, "alias": "新签", "agg": "SUM"}],
    "filter": {
      "logic": "AND",
      "items": [
        {"columnId": 101, "op": "INCLUDE", "values": ["武汉", "杭州"]},
        {
          "logic": "OR",
          "items": [
            {"columnId": 303, "op": "GE", "values": ["2025-01-01"]},
            {"columnId": 303, "op": "EQ", "values": ["2024-12-31"]}
          ]
        }
      ]
    }
  }
}'
```

### 高密集群（odinCluster=high_confidential，需高密白名单）

```bash
moma moma-data api POST_moma-data_odin_model_query --json -d '{
  "modelId": 34567,
  "query": {
    "dimensions": [
      {"columnId": 901, "alias": "敏感维度"},
      {"columnId": 902, "alias": "敏感度量"}
    ],
    "measures": []
  },
  "odin_cluster": "high_confidential"
}'
```

## 返回数据说明

⚠️ **`data` 常常是"含单个元素的数组"**（上游 queryAuthModelData 的 data 多为 `[ { queryResult... } ]`），偶尔是对象。取数前先归一化取到 payload 元素，再走 `queryResult.result.data.list`。

成功示例（data 为数组）：

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": [
    {
      "queryResult": {
        "result": {
          "data": {
            "list": [
              {"城市": "武汉", "新签单量": "26395"},
              {"城市": "杭州", "新签单量": "18712"}
            ]
          }
        }
      },
      "errorDetail": null
    }
  ]
}
```

数据提取约定：

- 先归一化：`data` 是数组则取 `data[0]`，是对象则取 `data` 本身，记为 payload；
- 模型行级数据在 `payload.queryResult.result.data.list`，记为 `#{model_data}`；`payload.errorDetail` 非空即上游报错；
- 行内列名由请求中的 `alias` 决定（推荐使用 `modelColumnName`）；
- **常见错误取法**：直接写 `data.queryResult...`（漏了 data 是数组、没取 `[0]`）会取空。

错误示例：

```json
{
  "errno": -1,
  "errmsg": "模型数据查询失败 | errorDetail=...",
  "data": null
}
```

常见错误：

- `高密模型查询未配置 ODIN_DATA_MODEL_HC_QUERY_HOST`：管理员未配置高密 Host
- `当前用户无高密数据访问权限`：未通过 `require_high_confidential_hive_tool_access` 白名单
- `errorDetail=...`：上游模型执行报错（SQL 或权限问题），按 detail 排查；若提示指标缺少聚合函数，检查 `measures[].agg` 是否填了
