# 查询数据资产 supabase 快照表的列信息

> 直接从 Supabase 的 `information_schema.columns` 查指定快照表的字段元数据，
> 包含字段名、数据类型、是否可空、默认值，以及 PostgreSQL 列注释（`col_description()`）。
> 权限校验与 `table-rows` 一致，凭 `asset_id` 做访问控制。
>
> **前置条件**：先用 data_asset_supabase_tables.md 拿到 `target_table`。

## 指令

```bash
moma moma-data api GET_moma-data_cli_data-assets_table-columns --json \
  -q "asset_id=38&table=hive_asset_38"
```

## 指令参数说明

Query 参数（-q key=v，拼在同一个 `-q` 里）：

  asset_id    数据资产 ID（必传）
  table       快照表名，取自 supabase-tables 的 `target_table`（必传）

## 返回数据说明

`data` 直接是**列信息数组**，按 `ordinal_position` 升序排列：

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": [
    {
      "name": "stat_date",
      "type": "text",
      "nullable": true,
      "default": null,
      "comment": "统计日期",
      "ordinal_position": 1
    },
    {
      "name": "city_code",
      "type": "text",
      "nullable": true,
      "default": null,
      "comment": "城市编码",
      "ordinal_position": 2
    },
    {
      "name": "deal_cnt",
      "type": "bigint",
      "nullable": true,
      "default": null,
      "comment": "成交套数",
      "ordinal_position": 3
    },
    {
      "name": "sys_created_at",
      "type": "timestamp with time zone",
      "nullable": true,
      "default": null,
      "comment": "",
      "ordinal_position": 4
    }
  ]
}
```

| 字段                 | 说明                                                     |
|----------------------|----------------------------------------------------------|
| `name`               | Supabase 列名（即同步时保留的原始字段名）                 |
| `type`               | PostgreSQL 数据类型（text / bigint / numeric 等）         |
| `nullable`           | 是否可空（bool）                                          |
| `default`            | 列默认值，通常为 null                                     |
| `comment`            | 列注释（`col_description()` 从 `pg_description` 读取）；未设注释时为空串 |
| `ordinal_position`   | 列在表中的序号，用于稳定排序                              |

## 使用建议

- **构建列名中文映射**：`comment` 非空时用 `comment` 作为展示名；为空时保留 `name`（英文列名）。
  ```
  #{col_display_map} = {col.name: col.comment || col.name for col in data}
  ```
- **过滤同步元数据列**：`sys_created_at` / `sys_updated_at` 是同步框架写入的内部字段，
  向用户展示结果时应过滤掉（按 `name` 前缀 `sys_` 过滤即可）。
- 本接口不含主键信息，只用于浏览字段和展示中文列名，不要用于写入场景。

## 错误处理

| 情形                                        | 后续动作                                  |
|---------------------------------------------|-------------------------------------------|
| `表 X 不属于数据资产 N`                     | 用 supabase-tables 重新取 `target_table`  |
| `负责人尚未开通独立 supabase 工作区`        | 告知用户联系资产负责人配置同步            |
| `无权限访问该资产`                          | 回 data_asset_accessible 确认权限         |
