# 执行 migration（带版本记录）

> 执行 DDL SQL 并把版本信息记录到 `public.schema_migrations` 表，便于追溯历史变更。
>
> 与 `execute-sql` 的区别：本接口在事务内执行 DDL + 写版本记录，失败自动回滚。

## 指令

```bash
moma moma-data api POST_moma-data_personal_supabase_apply-migration --json \
  -d '{"version": "20241001120000", "name": "create_records_table", "sql": "CREATE TABLE IF NOT EXISTS records (id uuid DEFAULT gen_random_uuid() PRIMARY KEY, data jsonb)"}'
```

## 参数说明

Body 参数（-d JSON 字符串）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| version | string | 是 | 版本字符串，推荐用时间戳格式 `YYYYMMDDHHMMSS` |
| sql | string | 是 | DDL SQL，在事务中执行 |
| name | string | 否 | 描述性名称，便于 list-migrations 时识别 |

## 使用示例

```bash
# 建表
moma moma-data api POST_moma-data_personal_supabase_apply-migration --json \
  -d '{"version": "20241001120000", "name": "create_records", "sql": "CREATE TABLE IF NOT EXISTS records (id uuid DEFAULT gen_random_uuid() PRIMARY KEY, data jsonb, created_at timestamptz DEFAULT now())"}'

# 加索引
moma moma-data api POST_moma-data_personal_supabase_apply-migration --json \
  -d '{"version": "20241001120001", "name": "add_idx_created_at", "sql": "CREATE INDEX IF NOT EXISTS idx_records_created_at ON records (created_at DESC)"}'

# 加字段
moma moma-data api POST_moma-data_personal_supabase_apply-migration --json \
  -d '{"version": "20241001120002", "name": "add_col_status", "sql": "ALTER TABLE records ADD COLUMN IF NOT EXISTS status text DEFAULT '\''active'\''"}'

# 创建 RPC 函数（之后可通过 execute-sql 调用：SELECT get_recent_records(5)）
moma moma-data api POST_moma-data_personal_supabase_apply-migration --json \
  -d '{"version": "20241001120003", "name": "create_fn_get_recent_records", "sql": "CREATE OR REPLACE FUNCTION get_recent_records(n int DEFAULT 10) RETURNS SETOF records LANGUAGE sql AS $$ SELECT * FROM records ORDER BY created_at DESC LIMIT n; $$"}'
```

## 返回数据

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": {
    "success": true,
    "version": "20241001120000",
    "message": "migration 20241001120000 已成功应用"
  }
}
```

version 重复时（已执行过同版本）会静默跳过（ON CONFLICT DO NOTHING）。
