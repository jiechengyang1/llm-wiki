# 获取数据资产已同步的 supabase 快照表

> 列出某个数据资产被同步到 supabase 的表名与同步状态。
> `hive` / `odin_fetch` / `data_model` / `excel` 类资产的数据会同步成 supabase 表（快照），
> 查这张快照表比按 `detail.raw_sql` 实时打上游更快，且不要求你对原上游数据源有权限。
> **report_component 没有独立快照，禁止走本接口或回退源表**；组件只走 [`report_component_query.md`](../report_component/report_component_query.md)。
> **上述快照资产取数前必须先用本接口拿到真实表名**，不要自己按 `hive_asset_{id}` / `excel_{id}` 拼。

## 指令

```bash
moma moma-data api GET_moma-data_cli_data-assets_supabase-tables --json -q "asset_id=38"
```

## 指令参数说明

Query 参数（-q key=v）：

  asset_id    数据资产 ID，取自 data_asset_accessible 返回的 `asset_id` (必传)
  ucid        用户 UCID，CLI 模式下可通过此 query param 传入，也可由 header 自动注入 (选传)

使用示例：

```bash
# hive 类资产
moma moma-data api GET_moma-data_cli_data-assets_supabase-tables --json -q "asset_id=38"

# odin_fetch 类资产（可能返回多张表）
moma moma-data api GET_moma-data_cli_data-assets_supabase-tables --json -q "asset_id=52"
```

## 返回数据说明

示例数据（hive 类，1 张表）：

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": {
    "asset_id": 38,
    "asset_type": "hive",
    "tables": [
      {
        "target_table": "hive_asset_38",
        "asset_type": "hive",
        "config_id": 0,
        "owner_ucid": "1000000029360338",
        "sync_status": "success",
        "enabled": 1,
        "last_sync_at": "2026-08-01T20:38:14",
        "row_count": 100,
        "error_message": "",
        "config_desc": ""
      }
    ]
  }
}
```

示例数据（odin_fetch 类，多张表）：

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": {
    "asset_id": 52,
    "asset_type": "odin_fetch",
    "tables": [
      {
        "target_table": "odin_asset_52_301",
        "config_id": 301,
        "sync_status": "success",
        "enabled": 1,
        "last_sync_at": "2026-08-05T03:12:00",
        "row_count": 8231,
        "config_desc": "近 30 天成交明细"
      },
      {
        "target_table": "odin_asset_52_302",
        "config_id": 302,
        "sync_status": "success",
        "enabled": 1,
        "last_sync_at": "2026-08-05T03:12:40",
        "row_count": 412,
        "config_desc": "城市维度汇总"
      }
    ]
  }
}
```

## 返回结构说明

| 字段          | 说明                                                        |
|---------------|-------------------------------------------------------------|
| `asset_id`    | 资产 ID（回显入参）                                          |
| `asset_type`  | 资产类型：`hive` / `odin_fetch` / `metric` / `data_model`    |
| `tables`      | 已同步的表列表，**可能为空数组**，见下方"空数组的三种情况"     |

`tables[]` 每项：

| 字段            | 说明                                                                    |
|-----------------|-------------------------------------------------------------------------|
| `target_table`  | supabase 表名，**取数时原样使用，不要自己拼**                            |
| `config_id`     | 子配置 ID：hive 恒为 0；odin_fetch 为该条取数配置的 ID                   |
| `owner_ucid`    | 资产负责人 ucid（数据由他的身份同步，出问题找他）                        |
| `sync_status`   | 同步状态：`success` / `running` / `staged` / `failed` / `cancelled` / `pending`<br>含义见下方"sync_status 说明" |
| `enabled`       | 定时同步开关：1=开 0=关                                                  |
| `last_sync_at`  | **上次同步成功完成的时间**，空串表示从未成功同步过；这是判断快照是否可用的核心字段 |
| `row_count`     | 上次同步的行数，可用来预判数据量                                          |
| `error_message` | 上次同步失败原因，`sync_status=failed` 时看这里                          |
| `config_desc`   | **odin_fetch 多表时靠它选表**；hive 恒为空串                             |

### `sync_status` 说明

| 值 | 含义 | 快照目标表的数据情况 |
|---|---|---|
| `success` | 上次同步完整成功 | 最新完整数据 |
| `running` | 正在同步中（数据写入 staging） | **目标表保有上一次完整数据**（`last_sync_at` 非空则可查） |
| `staged` | 数据已全部写入 staging，等待原子切换 | 同 `running`，目标表仍是上一版本 |
| `failed` | 同步执行失败（staging 已清理） | **目标表保有上一次完整数据**（`last_sync_at` 非空则可查） |
| `cancelled` | 同步被用户手动取消（staging 已清理） | 同 `failed`，目标表仍是上一版本 |
| `pending` | 等待下次执行 | 同 `failed`，视 `last_sync_at` 判断 |

**关键结论**：`sync_status` 反映的是**最近一次同步任务的状态**，而非快照表是否有数据。判断能否取数应以 `last_sync_at` 是否非空为准。

## `tables` 为空数组的三种情况

`errno` 仍为 0，靠 `errmsg` 区分，不要当成报错：

| errmsg                                        | 含义与后续动作                                              |
|-----------------------------------------------|-------------------------------------------------------------|
| `指标 类资产没有 supabase 快照表，...`         | 该资产是 `metric`，改走 `index api use core flow`            |
| `数据模型 类资产没有 supabase 快照表，...`     | 该资产是 `data_model`，改走 `model api use core flow`        |
| `该资产的负责人尚未开启 supabase 同步，暂无可查的表` | 负责人没开同步，改走该类型的实时取数 flow（hive / odin_fetch）|

## 使用建议

- **`last_sync_at` 是判断快照是否可用的核心依据**（`hive / odin_fetch / data_model`）：
  - `last_sync_at` 为空 → 从未同步成功，快照无数据 → 改走实时取数 flow 或告知用户
  - `last_sync_at` 非空 → 历史快照存在，可查；根据 `sync_status` 给出适当提示（同步中/失败/已取消 → 告知数据截至时间）
  - `last_sync_at` 明显早于用户要求的数据时点 → 告知快照时间，改走实时取数 flow
- **`excel` 单独判断**：`sync_status == success` 直接查；`failed` 代表目标表已 DROP（后端回退草稿态），告知用户重新发布；`running/pending` 看 `last_sync_at` 是否有值
- odin_fetch 资产返回多张表时，按 `config_desc` 匹配用户需求；分不清就用 AskUserQuestion
  让用户选，不要默认取第一张。
- 报错 `资产不存在` / `无权限访问该资产`：说明 `asset_id` 传错了或该资产没分享给当前用户，
  回到 data_asset_accessible 重新确认。
