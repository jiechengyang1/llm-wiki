# 获取当前用户可访问的数据资产列表

> 返回当前用户**所有可访问**的数据资产（我创建的 + 被分享给我的 + 团队分享），按标签/无标签/团队三组返回。
> 用于 AI 取数前，先让用户确认要用哪条已保存的资产，或直接复用资产中保存的查询配置。

## 指令

```bash
moma moma-data api GET_moma-data_cli_data-assets_accessible --json
```

## 指令参数说明

Query 参数（-q key=v）：

  asset_type  资产类型过滤，可选值：`data_model` / `hive` / `metric` / `odin_fetch` / `excel` / `report_component`，不传返回全部 (选传)
  ucid        用户 UCID，CLI 模式下可通过此 query param 传入，也可由 header 自动注入 (选传)

使用示例：

```bash
# 查询全部类型
moma moma-data api GET_moma-data_cli_data-assets_accessible --json

# 只看 hive 查询类资产
moma moma-data api GET_moma-data_cli_data-assets_accessible --json -q "asset_type=hive"

# 只看指标魔方类资产
moma moma-data api GET_moma-data_cli_data-assets_accessible --json -q "asset_type=metric"
```

## 返回数据说明

示例数据：

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": {
    "by_tag": [
      {
        "ref": "tag:16",
        "tag": "业绩分析",
        "items": [
          {
            "ref": "asset:hive:12",
            "asset_type": "hive",
            "asset_id": 12,
            "name": "华东区门店月度业绩",
            "description": "统计华东区各门店近3个月成交额",
            "creator_ucid": "10086",
            "detail": {
              "raw_sql": "SELECT shop_code, SUM(deal_amount) FROM dw_deal_da WHERE ...",
              "odin_cluster": "standard"
            }
          },
          {
            "ref": "asset:metric:34",
            "asset_type": "metric",
            "asset_id": 34,
            "name": "新房成交量指标",
            "description": "",
            "creator_ucid": "10086",
            "detail": {
              "targets": "25667,120849",
              "params": {"dateType": "month", "startDate": "2024-01-01", "endDate": "2024-06-30"}
            }
          }
        ]
      }
    ],
    "untagged": [
      {
        "ref": "asset:data_model:7",
        "asset_type": "data_model",
        "asset_id": 7,
        "name": "门店基础信息模型",
        "description": "贝壳门店维度基础数据",
        "creator_ucid": "10087",
        "detail": {
          "model_id": 191976,
          "model_name": "moma模型接入",
          "cluster_type": "default",
          "query_params": {"pageNo": 1, "pageSize": 100}
        }
      },
      {
        "ref": "asset:odin_fetch:9",
        "asset_type": "odin_fetch",
        "asset_id": 9,
        "name": "奥丁城市成交趋势",
        "description": "",
        "creator_ucid": "10086",
        "detail": [
          {
            "request_id": "a1b2c3d4-xxxx-xxxx-xxxx-000000000001",
            "date_params": {"dateType": "month", "offset": -1}
          }
        ]
      }
    ],
    "by_team": [
      {
        "ref": "team:5",
        "team_id": 5,
        "team_name": "数据分析团队",
        "items": [
          {
            "ref": "asset:hive:21",
            "asset_type": "hive",
            "asset_id": 21,
            "name": "团队共用 - 全国成交汇总",
            "description": "",
            "creator_ucid": "10099",
            "detail": {
              "raw_sql": "SELECT city_code, COUNT(*) FROM dw_deal_da WHERE ...",
              "odin_cluster": "standard"
            }
          }
        ]
      }
    ]
  }
}
```

## 返回结构说明

顶层三个分组：

| 字段      | 说明                                          |
|-----------|-----------------------------------------------|
| `by_tag`  | 有标签的资产，按标签名归组，一条资产可属于多个标签组 |
| `untagged`| 当前用户无标签的资产（含我创建 + 被个人分享）  |
| `by_team` | 通过团队分享获得的资产，按团队归组              |

每条资产公共字段：

| 字段           | 说明                               |
|----------------|------------------------------------|
| `asset_type`   | 资产类型，见下方类型说明            |
| `asset_id`     | 资产 ID                            |
| `name`         | 资产名称（用于匹配用户描述）        |
| `description`  | 资产描述                           |
| `creator_ucid` | 创建人 ucid                        |
| `detail`       | 资产详情，结构因 `asset_type` 而异  |
| `allow_probe`  | 是否允许探查原始数据源：`1`=允许（默认）`0`=仅允许通过 supabase 快照表访问 |
| `ref`          | 资产/团队/标签等标识信息，仅作标识使用，无实际含义  |


## detail 字段说明（按 asset_type）

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

数据来自用户上传的 xlsx/xls/csv 文件，同步后落到用户 supabase 的 `excel_{asset_id}` 表。**发布即同步**（不排定时任务，`enabled=0` 是正常状态，只看 `sync_status`）——文件变化需资产负责人重新上传并再次发布触发同步。同步失败时后端会自动把资产回退到草稿态。

| 字段                 | 说明                                                                              |
|----------------------|-----------------------------------------------------------------------------------|
| `file_name`          | 原始文件名，如 `业绩明细.xlsx`                                                    |
| `file_type`          | 文件类型：`xlsx` / `xls` / `csv`                                                  |
| `file_size`          | 文件字节数                                                                        |
| `sheet_name`         | Excel 使用的 sheet 名（csv 为 null）                                              |
| `column_definitions` | 字段结构数组，每项 `{name, orig_name, type}`；`name` 是入库字段（可能被拼音化），`orig_name` 是原始列名（可能中文），`type` 为 `str/int/float/bool` |
| `row_count`          | 解析时的总行数                                                                    |

**取数方式**：数据在 supabase 快照表中，走 `supabase snapshot core flow`；展示时用 `column_definitions[].orig_name` 作展示名，查询表时用 `column_definitions[].name`。

## 使用建议

- 用户提到"上次的查询"、"之前保存的"、"复用已有配置"时，优先调用本接口定位资产，再根据 `asset_type` + `detail` 决定后续查询方式。
- `by_tag` 和 `untagged` 中可能包含重复资产（同一资产打了多个标签），以 `asset_id` 去重。
- `by_team` 中的资产 `creator_ucid` 可能不是当前用户，属于共享资产，只读不可编辑。
- 无法精准匹配时，使用 AskUserQuestion 让用户从列表中确认目标资产。

## 看板组件资产

页面将组件收纳在「奥丁报告 → 报告名 → 组件资产」，不在「全部」平铺；目录只是展示分组。
本接口仍通过 by_tag/by_team/untagged 返回当前用户已授权的资产，按 asset_id 去重；不要假设存在名为「奥丁报告」的标签或新查询 API。
用户已 @ 的组件优先匹配；同名组件核对详情中的 report_id/report_name。
用户先在数据资产页点击「获取有权限的报告 / 刷新报告」，服务端分批检查 Moma 中已录入、已发布且有组件资产的报告，并保存当前用户、当前环境的目录。拥有报告 view 权限的用户无需逐个组件分享；进入页面和调用 accessible 只读已保存目录，不扫描 Odin。列表未命中时引导用户点击该按钮，不自行遍历报告或调用刷新任务。access_via_report=true 表示通过报告目录发现，不等于查询授权；实际取数实时校验报告权限和源资产行级规则。lite=true 无 detail 时，通过 by-ids 补齐版本、列和筛选器。
命中后只走 [`report_component_query.md`](../report_component/report_component_query.md)，不能转去 supabase-tables、owner-table 或源模型。
