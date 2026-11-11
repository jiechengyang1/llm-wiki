# 列出已执行的 migration

> 查看 `public.schema_migrations` 表里记录的历史 migration。

## 指令

```bash
moma moma-data api GET_moma-data_personal_supabase_list-migrations --json
```

## 返回数据

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": [
    {"version": "20241001120000", "name": "create_records", "inserted_at": "2024-10-01T12:00:00+00:00"},
    {"version": "20241001120001", "name": "add_idx_created_at", "inserted_at": "2024-10-01T12:00:01+00:00"}
  ]
}
```

从未执行过 `apply-migration` 时返回空数组（不报错）。
