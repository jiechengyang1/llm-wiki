# 对数据资产 supabase 快照表做聚合查询

> 对 `hive` / `odin_fetch` / `data_model` / `excel` 资产的快照表做 **DB 侧聚合**（分组、求和、计数、时间粒度），
> 只回传聚合后的结果行。
> **别用 table-rows 拉明细回来自己加** —— 快照表可能几十万行，拉回终端既慢又容易超限。
> 前置条件：先用 data_asset_supabase_tables.md 拿到 `target_table`，
> 再用 data_asset_table_rows.md 摸清真实列名（聚合的列名必须真实存在）。

## 指令

```bash
moma moma-data api POST_moma-data_cli_data-assets_table-aggregate --json \
  -d '{"asset_id":38,"table":"hive_asset_38","dims":[{"field":"city"}],"metrics":[{"agg":"SUM","field":"cnt"}],"limit":50}'
```

⚠️ 与 table-rows 不同：本接口是 **POST + `-d` JSON body**（聚合参数是嵌套结构，
query 参数表达不了）。POST 只是入参形态，**语义仍是只读**，快照表依旧不可写。

## 指令参数说明

Body 参数（-d JSON 字符串）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asset_id | int | 是 | 数据资产 ID |
| table | string | 是 | 表名，取自 supabase-tables 的 `target_table`，不要自己拼 |
| metrics | array | 是 | 聚合指标，**至少一项**（不聚合请改用 table-rows） |
| dims | array | 否 | 分组维度；不传则整表汇总（返回 1 行） |
| filters | array | 否 | 过滤条件，条件之间 AND |
| having | array | 否 | 对聚合结果过滤 |
| order | array | 否 | 排序；`field` **只能是已声明的维度或指标别名** |
| limit | int | 否 | 默认 1000，上限 10000 |
| offset | int | 否 | 默认 0 |

### metrics（聚合指标）

| 字段 | 说明 |
|------|------|
| agg | `COUNT` / `SUM` / `AVG` / `MAX` / `MIN` |
| field | 列名；仅 `COUNT` 可用 `*`（缺省就是 `*`） |
| distinct | 布尔，如 `COUNT(DISTINCT user_id)` |
| alias | 输出列名；缺省为 `{agg小写}_{field}`，如 `sum_cnt`；`COUNT(*)` 缺省为 `count` |

### dims（分组维度）

| 字段 | 说明 |
|------|------|
| field | 分组列名 |
| trunc | 时间粒度：`day` / `week` / `month` / `quarter` / `year` |
| dateFormat | **日期列是 TEXT 时必填**（如 `20260814` 传 `YYYYMMDD`），否则转换会报错 |
| alias | 输出列名；缺省用字段名 |

### filters / having（过滤条件）

filters 的 `op`：`eq` `ne` `gt` `gte` `lt` `lte` `like` `not_like` `in` `not_in` `is_null` `is_not_null`
（`in` / `not_in` 的 `value` 传数组；`is_null` / `is_not_null` 不需要 `value`）

having 只支持标量比较：`eq` `ne` `gt` `gte` `lt` `lte`，字段为 `{agg, field, op, value}`。

## 使用示例

```bash
# 按城市汇总
moma moma-data api POST_moma-data_cli_data-assets_table-aggregate --json \
  -d '{"asset_id":38,"table":"hive_asset_38","dims":[{"field":"city"}],"metrics":[{"agg":"SUM","field":"cnt"}],"order":[{"field":"sum_cnt","dir":"desc"}],"limit":20}'

# 按月趋势（日期列是 TEXT 20260814 格式，必须给 dateFormat）
moma moma-data api POST_moma-data_cli_data-assets_table-aggregate --json \
  -d '{"asset_id":38,"table":"hive_asset_38","dims":[{"field":"stat_date","trunc":"month","dateFormat":"YYYYMMDD","alias":"month"}],"metrics":[{"agg":"SUM","field":"cnt"}],"order":[{"field":"month","dir":"asc"}]}'

# 整表汇总（不分组）+ 去重计数
moma moma-data api POST_moma-data_cli_data-assets_table-aggregate --json \
  -d '{"asset_id":38,"table":"hive_asset_38","metrics":[{"agg":"COUNT"},{"agg":"SUM","field":"cnt"},{"agg":"COUNT","field":"shop_id","distinct":true}]}'

# 过滤 + HAVING（只看总量超 1000 的城市）
moma moma-data api POST_moma-data_cli_data-assets_table-aggregate --json \
  -d '{"asset_id":38,"table":"hive_asset_38","dims":[{"field":"city"}],"metrics":[{"agg":"SUM","field":"cnt"}],"filters":[{"field":"biz_type","op":"in","value":["二手","新房"]}],"having":[{"agg":"SUM","field":"cnt","op":"gt","value":1000}]}'
```

## 返回数据说明

`data` 直接是**聚合结果行数组**，列名就是维度别名 + 指标别名：

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": [
    {"city": "北京市", "sum_cnt": 12043},
    {"city": "上海市", "sum_cnt": 9821}
  ]
}
```

## 能力边界

- **仅支持单表**：没有 JOIN、没有子查询、不能传 SQL 片段。需要关联多表时分开查、在结果层合并。
- **不能自定义表达式**：只有上面列出的聚合函数与操作符。比率、同比这类派生指标请取回分子分母
  两个指标后在展示层计算。
- 列名必须是快照表里真实存在的列（先用 table-rows 摸清）。

## 错误处理

先判 `errno`，非 0 时 `errmsg` 带具体错误码。除 table-rows 那张表里的
`OWNER_ASSET_TABLE_*`（无权 / 已下线 / 未同步完成，处理方式完全相同）之外，本接口特有：

| errmsg 含错误码 | 含义 | 后续动作 |
|-----------------|------|----------|
| `asset_id（整数）与 table 必传` | body 缺参数 | 补上 |
| `ASSET_AGG_BAD_PARAM` | 聚合参数不合法（列名非法、metrics 为空、order 引用了未声明的列等） | 按 errmsg 里指出的字段改正 |
| `ASSET_AGG_TABLE_NOT_FOUND` | 该表不是可聚合的资产表 | 用 supabase-tables 重新取表名 |
| `ASSET_AGG_FORBIDDEN` | 当前身份对该资产无访问权 | 回 data_asset_accessible 确认，或让用户找负责人分享 |
| `ASSET_AGG_QUERY_FAILED` | SQL 被数据库拒绝（最常见是 TEXT 日期列没给 `dateFormat`） | 按 errmsg 提示补 `dateFormat`，或确认列类型 |
| `ROW_FILTER_DENIED` | 行级数据权限判定为拒绝 | 告知用户联系资产负责人 |

**这些错误一律把原文透传给用户**，不要压成一句"查询失败"。

## 使用建议

- **能聚合就聚合**：用户问"各城市总量""按月趋势""有多少条"时，直接用本接口，
  不要 table-rows 拉明细再自己算。
- 行级数据权限由服务端自动注入，你不需要也不能自己加（同 table-rows）。
- 只要总行数这一个数时，`table-rows` 的 `select=count` 更省事，两者都行。
