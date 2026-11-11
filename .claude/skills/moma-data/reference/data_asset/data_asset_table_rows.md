# 查询数据资产 supabase 快照表的数据

> 读 `hive` / `odin_fetch` / `data_model` / `excel` 资产已同步的 supabase 快照表的**明细行**。
> 除 `asset_id` / `table` 外的 query 参数**原样透传给 PostgREST**，
> 所以 select / 过滤 / 排序 / 分页全部用 PostgREST 语法书写。
> 前置条件：先用 data_asset_supabase_tables.md 拿到 `target_table` 与同步状态。
>
> ⚠️ **要聚合值（分组 / SUM / COUNT / 按月趋势）请改用
> [data_asset_table_aggregate.md](data_asset_table_aggregate.md)** —— 让数据库算好只回传结果行。
> 别用本接口拉明细回来自己加：快照表可能几十万行。
> 例外：只要一个总行数时，本接口的 `select=count` 更省事。

## 指令

```bash
moma moma-data api GET_moma-data_cli_data-assets_table-rows --json \
  -q "asset_id=38&table=hive_asset_38&select=*&limit=10"
```

## 指令参数说明

Query 参数（-q key=v，全部拼在同一个 `-q` 里）：

  asset_id    数据资产 ID (必传)
  table       表名，取自 supabase-tables 的 `target_table`，不要自己拼 (必传)
  ucid        用户 UCID，CLI 模式下可通过此 query param 传入 (选传)
  其余参数     原样透传给 PostgREST，见下方「PostgREST 语法」

⚠️ `asset_id` / `table` / `ucid` 是本接口的**保留参数**，不会透传。若资产表里恰好有同名
列需要过滤，只能改用其它条件绕开（这种情况极少）。

## PostgREST 语法（透传部分）

| 用途     | 写法                                      | 说明                                        |
|----------|-------------------------------------------|---------------------------------------------|
| 选列     | `select=col_a,col_b`                      | `select=*` 取全部列                          |
| 等值     | `city=eq.北京市`                          | 值不需要手动编码，CLI 会处理                  |
| 不等     | `city=neq.北京市`                         |                                             |
| 比较     | `cnt=gt.100` / `gte` / `lt` / `lte`       |                                             |
| 多值     | `pt=in.(20260716000000,20260717000000)`   | 括号内逗号分隔                                |
| 模糊     | `name=like.*门店*`                        | `*` 是通配符                                  |
| 空值     | `col=is.null`                             |                                             |
| 排序     | `order=stat_date.desc`                    | 多列 `order=a.desc,b.asc`                    |
| 限量     | `limit=20`                                | **默认必须带**，避免拉全表                     |
| 分页     | `limit=20&offset=40`                      | 与 hive 不同，这里**支持** offset             |
| 计数     | `select=count`                            | 只要行数、不要数据时用                         |

使用示例：

```bash
# 看前 10 行全部列（先摸清有哪些字段）
moma moma-data api GET_moma-data_cli_data-assets_table-rows --json \
  -q "asset_id=38&table=hive_asset_38&select=*&limit=10"

# 挑列 + 过滤 + 排序
moma moma-data api GET_moma-data_cli_data-assets_table-rows --json \
  -q "asset_id=38&table=hive_asset_38&select=stat_date,city,cnt&city=eq.北京市&order=stat_date.desc&limit=20"

# 只要总行数
moma moma-data api GET_moma-data_cli_data-assets_table-rows --json \
  -q "asset_id=38&table=hive_asset_38&select=count"

# 第 3 页（每页 20）
moma moma-data api GET_moma-data_cli_data-assets_table-rows --json \
  -q "asset_id=38&table=hive_asset_38&select=*&limit=20&offset=40"
```

## 返回数据说明

`data` 直接就是**行数组**（不是对象，没有 `list` 嵌套）：

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": [
    {"stat_date": "2026-07-16", "city": "北京市", "cnt": 42},
    {"stat_date": "2026-07-15", "city": "上海市", "cnt": 37}
  ]
}
```

- 列名就是快照表的真实列名（同步时保留了 Hive / 奥丁的原始字段名）；
- `select=count` 时 `data` 形如 `[{"count": 8231}]`；
- 表里可能带 `sys_created_at` / `sys_updated_at` 等同步元数据列，展示给用户时可忽略。

## 错误处理

先判 `errno`，非 0 时 `errmsg` 会带上具体错误码，每种对应不同后续动作：

| errmsg 含错误码                              | 含义                       | 后续动作                                    |
|---------------------------------------------|----------------------------|---------------------------------------------|
| `表 X 不属于数据资产 N；该资产可读的表：[...]` | table 与 asset_id 对不上    | 按 errmsg 列出的表名改正                     |
| `无权限访问该资产`                            | 当前用户没有该资产权限      | 回 data_asset_accessible 确认，或让用户找负责人分享 |
| `OWNER_ASSET_TABLE_FORBIDDEN`               | 同上（服务端二次校验兜住）  | 同上                                        |
| `OWNER_ASSET_TABLE_SYNC_DISABLED`           | 负责人关闭了同步            | 告知用户联系 `owner_ucid`，或改走实时取数 flow |
| `OWNER_ASSET_TABLE_NOT_READY`               | 开了同步但从未成功过        | 改走实时取数 flow                            |
| `OWNER_ASSET_TABLE_ASSET_UNPUBLISHED`       | 资产被负责人撤销发布        | 告知用户，恢复发布后自动可用                  |
| `OWNER_ASSET_TABLE_ASSET_DELETED`           | 资产已删除                  | 告知用户，换资产                              |
| `OWNER_ASSET_TABLE_NOT_FOUND`               | 该表不是可读的资产表        | 用 supabase-tables 重新取表名                 |
| `取数服务响应超时`                            | 链路超时                    | 缩小 `limit` 重试                            |

**这些错误一律把原文透传给用户**，不要压成一句"查询失败"——「无权」「已下线」「未同步完成」
是三种完全不同的处理方式。

## 使用建议

- **第一次查一张陌生表，先 `select=*&limit=10`** 摸清真实列名，再写带 select / 过滤的查询。
  不要凭资产名猜列名。
- **永远带 `limit`**。快照表可能有几十万行，不带 limit 会把全表拉回终端。
- 属主资产表是**只读**的（数据由负责人的同步任务维护），本接口也只支持 GET。任何写入意图
  都应告知用户去找资产负责人改上游 SQL / 奥丁配置。
  （聚合接口 `table-aggregate` 用 POST 只是为了传嵌套参数，语义同样是只读，不是写入口）
- 用户要求"导出 / 下载"时：本接口按 `limit` + `offset` 分批取即可，不需要走 hive 的异步
  下载流程。
