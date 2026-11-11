# 按资产 ID 列表批量获取数据资产

> 已知资产 ID 列表时，直接批量拉取对应资产详情，无需遍历全量可访问列表。
> 适用于：上下文中已缓存 asset_id、用户直接指定资产 ID 等场景。

## 指令

```bash
moma moma-data api GET_moma-data_cli_data-assets_by-ids --json -q "ids=101,202,303"
```

## 指令参数说明

Query 参数（-q key=v）：

  ids  资产 ID 列表，**逗号分隔**（必传）

> ⚠️ 注意：moma CLI 的 `-q` 存在已知问题，重复 `ids=X&ids=Y` 格式只会保留最后一个值，必须使用逗号分隔格式。

使用示例：

```bash
# 查询单个资产
moma moma-data api GET_moma-data_cli_data-assets_by-ids --json -q "ids=101"

# 批量查询多个资产（逗号分隔）
moma moma-data api GET_moma-data_cli_data-assets_by-ids --json -q "ids=101,202,303,404"
```

## 返回数据说明

返回按入参 `ids` 顺序排列的资产列表（不存在或已删除的 ID 会被自动跳过）。

示例数据：

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": [
    {
      "asset_type": "hive",
      "asset_id": 101,
      "name": "用户行为明细表",
      "description": "记录用户每日操作日志",
      "creator_ucid": "zhangsan",
      "detail": {
        "raw_sql": "SELECT user_id, action FROM dw.user_action WHERE dt='${dt}'",
        "odin_cluster": "standard"
      }
    },
    {
      "asset_type": "metric",
      "asset_id": 202,
      "name": "DAU",
      "description": "日活跃用户数",
      "creator_ucid": "lisi",
      "detail": {
        "targets": "metric_dau_001",
        "params": {"dateType": "month", "startDate": "2024-01-01", "endDate": "2024-06-30"}
      }
    },
    {
      "asset_type": "data_model",
      "asset_id": 303,
      "name": "房源成交模型",
      "description": "链接成交数据模型",
      "creator_ucid": "wangwu",
      "detail": {
        "model_id": 88,
        "model_name": "house_deal_model",
        "cluster_type": "presto",
        "query_params": {"city_id": 110000, "date_range": "last_30_days"}
      }
    },
    {
      "asset_type": "odin_fetch",
      "asset_id": 404,
      "name": "二手房成交看板",
      "description": "奥丁二手房周报数据",
      "creator_ucid": "zhaoliu",
      "detail": [
        {
          "request_id": "odin_req_aaa111",
          "date_params": {"dateType": "month", "offset": -1}
        }
      ]
    }
  ]
}
```

## detail 字段说明（按 asset_type）

每条资产公共字段：

| 字段           | 说明                                                      |
|----------------|-----------------------------------------------------------|
| `asset_type`   | 资产类型：`hive` / `metric` / `data_model` / `odin_fetch` / `excel` / `report_component` |
| `asset_id`     | 资产 ID                                                   |
| `name`         | 资产名称                                                  |
| `description`  | 资产描述                                                  |
| `creator_ucid` | 创建人 ucid                                               |
| `detail`       | 资产详情，结构因 `asset_type` 而异，见下方说明             |

### `hive` — 数据查询

| 字段           | 说明                                                                 |
|----------------|----------------------------------------------------------------------|
| `raw_sql`      | 保存的 SQL 语句，可直接用于 `POST /moma-data/hive/execute-sql` 执行  |
| `odin_cluster` | 集群类型：`standard`（默认）/ `high_confidential`（高密）            |

### `metric` — 指标魔方

| 字段      | 说明                                                                          |
|-----------|-------------------------------------------------------------------------------|
| `targets` | 指标 ID，逗号分隔，可直接用于 `POST /moma-data/index/query` 的 `targets` 入参 |
| `params`  | 查询参数 JSON，含 `dateType` / `startDate` / `endDate` / `dim` 等             |

### `data_model` — 数据模型

| 字段           | 说明                                                                              |
|----------------|-----------------------------------------------------------------------------------|
| `model_id`     | 数据模型 ID，可用于 `POST /moma-data/odin/model/query`                            |
| `model_name`   | 模型名称                                                                          |
| `cluster_type` | 上游集群类型：`default` / `finance` / `hfc` / `secret`，见 model_list 映射说明   |
| `query_params` | 上次查询时保存的参数 JSON，可作为复用起点                                          |

### `odin_fetch` — 奥丁取数

detail 为**数组**，每条取数配置包含：

| 字段          | 说明                                                                       |
|---------------|----------------------------------------------------------------------------|
| `request_id`  | 奥丁取数请求 UUID，可用于 `GET /moma-data/odin-fetch/preview` 预览数据     |
| `date_params` | 日期参数 JSON，如 `{"dateType":"month","offset":-1}`                       |

### `excel` — Excel/CSV 数据资产

数据来自用户上传的 xlsx/xls/csv 文件，同步后落到用户 supabase 的 `excel_{asset_id}` 表。**发布即同步**（`enabled=0` 是正常状态，只看 `sync_status`），同步失败会自动回退到草稿态。

| 字段                 | 说明                                                                              |
|----------------------|-----------------------------------------------------------------------------------|
| `file_name`          | 原始文件名                                                                        |
| `file_type`          | `xlsx` / `xls` / `csv`                                                            |
| `file_size`          | 文件字节数                                                                        |
| `sheet_name`         | Excel 的 sheet 名（csv 为 null）                                                  |
| `column_definitions` | 字段结构数组：`[{name, orig_name, type}]`；`name` 是入库列名（拼音化后的 ascii），`orig_name` 是原始列名（可能中文），`type` ∈ `str/int/float/bool` |
| `row_count`          | 解析时的总行数                                                                    |

## 使用建议

- 上下文中已有 `asset_id` 时（如上次对话已获取过资产列表），优先使用本接口精准拉取，避免重复拉全量列表。
- 不存在或已删除的 ID 会被静默跳过，返回列表长度可能小于入参 `ids` 数量。
- 返回顺序与入参 `ids` 顺序保持一致。

## report_component — 看板组件资产

按 [`report_component_query.md`](../report_component/report_component_query.md) 走固定版本的组件接口，不查源表或模型。
返回的 asset_id 是 data_asset 目录 ID，不能用 report_component 二级表 ID、report_id、component_id 或 source_asset_id 替代。
用户通过页面按钮获取的个人报告目录也允许读取组件契约，无需逐个分享；未获取目录且无已有分享时，本接口可能不返回该组件。目录可见不授予源资产访问权，实际组件查询仍实时校验当前访客的 Odin 报告权限和源资产行级规则。
detail 提供 version、query_api、query_body、columns、filters、row_permission、source_sync；可用时还提供 report_id/report_name/display。source_sync 仅供前端 @ 选择守卫使用，Agent 不基于它输出额外同步提示。
复用 query_body.asset_id/version，筛选只按 filters 配置；列表缺 detail 时先调用本接口，不从历史上下文猜版本。
