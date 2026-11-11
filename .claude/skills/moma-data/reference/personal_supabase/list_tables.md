# 列出个人实例的表

> 列出个人 supabase 实例 `public` schema 下所有可访问的表。

## 指令

```bash
moma moma-data api GET_moma-data_personal_supabase_list-tables --json
```

## 参数说明

无需参数。

## 返回数据

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": [
    {"schema": "public", "name": "records", "comment": null},
    {"schema": "public", "name": "schema_migrations", "comment": null}
  ]
}
```

`comment` 是表的 COMMENT，通过 `COMMENT ON TABLE xxx IS '...'` 设置。

## 使用建议

在 `execute-sql` 或 `apply-migration` 之后调用，确认建表是否成功。
