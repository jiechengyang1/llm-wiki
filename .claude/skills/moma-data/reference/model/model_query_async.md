# 通过数据模型异步下载 API 获取数据

> 与 [model_query](./model_query.md) 走同一份请求参数，但通过 Odin 异步下载接口
> (`asyncQueryAuthModelData`) 一次性拉完整数据集并做类型转换后返回。
>
> **行数上限按集群类型区分**：公共集群已扩容至 **10W 行**；高密集群维持 **5000 行**。
> `query.page.pageSize` 由服务端按集群自动覆盖，无需调用方传入。
>
> **如何判断模型属于哪个集群**：调用 [model_list](./model_list.md) 时，返回结果中每个模型
> 有 `odinCluster` 字段——值为 `high_confidential` 表示高密集群，其余（`public` 等）为公共集群。
> 调用本接口时将该值透传给 `odin_cluster` 参数即可，服务端自动选择对应行数上限和查询 Host。
> 高密集群超出 5000 行时请通过 filter/dimensions 缩小数据量。

## 何时用异步

- `pageSize > 100`（同步接口在大 pageSize 下有已知 bug，见"背景"）
- 需要一次性拉完整数据集（避免翻页错乱）
- 同步接口返回的字段出现值 `null` 但预期非空（大 pageSize 触发的字段丢失 bug）

## 何时不用（继续用 [model_query](./model_query.md)）

- 小数据量预览 / 前 N 行查看
- 需要实时响应（异步流程包含轮询，可能耗时几十秒到几分钟）

## 指令

从资产命中时在同一条异步指令里带 `asset_id`：

```bash
moma moma-data api POST_moma-data_odin_model_query-async --json -d '{
  "modelId": 12345,
  "asset_id": 821,
  "odin_cluster": "public",
  "query": {
    "dimensions": [
      {"columnId": 101, "alias": "统计日期"},
      {"columnId": 202, "alias": "新签单量"}
    ],
    "measures": []
  }
}'
```

不是从资产来的模型查询不传 `asset_id`：

```bash
moma moma-data api POST_moma-data_odin_model_query-async --json -d '{
  "modelId": 12345,
  "query": {
    "dimensions": [
      {"columnId": 101, "alias": "统计日期"},
      {"columnId": 202, "alias": "新签单量"}
    ],
    "measures": [],
    "filter": {
      "logic": "AND",
      "items": [
        {"columnId": 101, "op": "INCLUDE", "values": ["2025-08"]}
      ]
    }
  }
}'
```

> 也可以用 `moma moma-data model query --async ...`，两条路径等价。

## 指令参数说明

**与 [model_query](./model_query.md) 完全一致**——`modelId` / `query.dimensions` / `query.measures`
/ `query.filter` / `query.orderBy` / `odin_cluster` / `asset_id` 的语义、结构、约束都相同。
差异只有一点：

| 字段 | 异步接口行为 |
|---|---|
| `query.page.pageNo` | 服务端强制为 `1`，忽略入参 |
| `query.page.pageSize` | 服务端按 `odin_cluster` 覆盖：`high_confidential` → `5000`，其余 → `100000`，忽略入参 |

其它字段包括 `dimensions/measures` 平移规则、filter 嵌套树结构、cluster 归一化等，请查阅 `model_query.md`。

## 返回数据说明

**⚠️ 与同步接口的返回结构不同**——异步接口做过归一化，`data` 直接是对象（不再是"含单个元素的数组"），
且行数据已经按 Odin `mapping.data_type` 做过 Python 类型强转：字符串保留字符串，`bigint/int/long`
转 `int`，`double/decimal/float` 转 `float`，`bool` 转 bool，`date/datetime/timestamp` 保留字符串。

成功示例：

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": {
    "list": [
      {"统计日期": "2025-08-01", "新签单量": 26395},
      {"统计日期": "2025-08-02", "新签单量": 18712}
    ],
    "headers": ["统计日期", "新签单量"],
    "rowCount": 2,
    "columnCount": 2,
    "mapping": {
      "统计日期": {"column_id": 101, "column_name": "统计日期", "data_type": "string", ...},
      "新签单量": {"column_id": 202, "column_name": "新签单量", "data_type": "bigint", ...}
    },
    "taskId": 123456
  }
}
```

数据提取约定：

- 行数据直接在 `data.list`（**不需要**再走 `queryResult.result.data.list` 那一层）
- 列名由请求中的 `alias` 决定，取值已是正确的 Python 类型
- `data.rowCount` 是 Odin 侧写入 CSV 的行数，可用于校验；`data.taskId` 是 Odin 侧任务 ID，出问题时向 Odin 团队报单用
- 空结果时 `data.list=[]`，其它字段仍在

## 常见错误

- `任务环境不匹配，请联系管理员`：当前请求环境与任务归属环境不一致（通常是提交后
  切换了 cluster）。重新提交即可。
- `任务已过期或被清理（taskId=...）`：任务未在有效期内被查询状态，或已被清理。重新触发查询。
- `任务执行失败（taskId=...）: {errorCode}/{errorMessage}`：Odin 侧执行失败，按 errorCode 排查；
  常见原因是数据量超限或 SQL 执行超时。
- `任务执行超时（taskId=...，已等待 600秒）`：轮询超过 10 分钟仍未完成，通常是数据量过大 /
  Odin 侧队列拥堵，减少数据量或稍后重试。
- `结果下载失败: ...`：S3 短期签名下载环节失败，一般是网络抖动。业务侧已重试 2 次仍
  失败会抛出此错误，再次触发查询即可。

## 背景

Odin 数据模型底层是分布式查询，同步接口 `queryAuthModelData` 存在两处已知 bug：

1. 分页错乱：同一 query 分多页返回时，每页可能是同一批数据（无法可靠拉全量）
2. 大 pageSize 下 SQL 模式模型部分字段返回 `null`（观察到 pageSize >= 2000 触发）

异步下载接口 `asyncQueryAuthModelData` 服务端一次生成完整 CSV，天然规避以上问题。
