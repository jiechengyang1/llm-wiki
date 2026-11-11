# 在个人实例上执行 SQL

> 在用户的个人 supabase 实例（`user_supabase_workspace`）上执行任意 SQL（DDL/DML）。
>
> ⚠️ DDL 操作（建表/改表/创建函数）建议改用 [`apply_migration.md`](apply_migration.md)，
> 有版本记录，出问题可追溯。

## 指令

```bash
moma moma-data api POST_moma-data_personal_supabase_execute-sql --json \
  -d '{"sql": "SELECT * FROM my_table LIMIT 10"}'
```

## 参数说明

Body 参数（-d JSON 字符串）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sql | string | 是 | 要执行的 SQL 语句 |

## 使用示例

```bash
# 查看某张表前 10 行
moma moma-data api POST_moma-data_personal_supabase_execute-sql --json \
  -d '{"sql": "SELECT * FROM my_table LIMIT 10"}'

# 创建表（推荐用 apply-migration 替代）
moma moma-data api POST_moma-data_personal_supabase_execute-sql --json \
  -d '{"sql": "CREATE TABLE IF NOT EXISTS records (id uuid DEFAULT gen_random_uuid() PRIMARY KEY, data jsonb, created_at timestamptz DEFAULT now())"}'

# 插入数据
moma moma-data api POST_moma-data_personal_supabase_execute-sql --json \
  -d '{"sql": "INSERT INTO records (data) VALUES ('\''{}'\'')"}'
```

## 返回数据

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": {
    "success": true,
    "data": [
      {"id": "...", "data": {}, "created_at": "..."}
    ]
  }
}
```

SELECT 等有结果集的语句，`data.data` 是行数组；DDL 语句通常返回空数组。

