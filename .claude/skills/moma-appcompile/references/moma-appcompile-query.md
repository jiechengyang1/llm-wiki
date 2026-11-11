# moma moma-appcompile api POST_api_moma-app-build_query

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

统一查询入口：`type=table` 执行只读 SQL；`type=bucket` 列桶内文件。两种 type 共用同一接口，body 结构不同。

## Recommended Commands

```bash
# 执行只读 SQL（type=table）
moma moma-appcompile api POST_api_moma-app-build_query --json --data '{
  "chat_id": "<CHAT_ID>",
  "type": "table",
  "sql": "SELECT * FROM orders LIMIT 10"
}'

# 列桶内文件（type=bucket）
moma moma-appcompile api POST_api_moma-app-build_query --json --data '{
  "chat_id": "<CHAT_ID>",
  "type": "bucket",
  "bucket_id": "<BUCKET_ID>",
  "prefix": "",
  "limit": 100,
  "offset": 0
}'

# 下钻目录：把目录名直接作为 prefix 传入，不要加前后 /
moma moma-appcompile api POST_api_moma-app-build_query --json --data '{
  "chat_id": "<CHAT_ID>",
  "type": "bucket",
  "bucket_id": "<BUCKET_ID>",
  "prefix": "test1",
  "limit": 100,
  "offset": 0
}'
```

## Options

### type=table（SQL 查询）

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `chat_id` | **必填** | 应用 chat_id |
| `type` | **必填** | 固定 `"table"` |
| `sql` | **必填** | 只读 SQL（SELECT / EXPLAIN）；**禁止 DDL / DML** |

### type=bucket（桶文件列表）

| 字段 | 是否必填 | 默认值 | 含义 |
|------|---------|-------|------|
| `chat_id` | **必填** | - | 应用 chat_id |
| `type` | **必填** | - | 固定 `"bucket"` |
| `bucket_id` | **必填** | - | 桶 ID |
| `prefix` | 可选 | `""` | 路径前缀 |
| `limit` | 可选 | `100` | 返回数量，上限 1000 |
| `offset` | 可选 | `0` | 偏移量 |

## 响应结构

- `type=table`：返回 SQL 执行结果（行列数组），格式以后端返回为准。
- `type=bucket`：同 [`objects`](moma-appcompile-objects.md) 响应结构。
  **⚠️ `data.items` 里可能夹杂"虚拟文件夹"占位**：Supabase Storage 的 `.list()` 只返回一层，带下级路径的对象会按首段聚合成占位行，与真实文件共用同一 schema，靠字段取值区分：

  | 字段 | 真实文件 | 虚拟文件夹 |
  |------|---------|-----------|
  | `id` | uuid 字符串 | **`null`** |
  | `metadata.size` / `metadata.mimetype` | 有值 | 不存在 |
  | `created_at` / `updated_at` | ISO 时间 | `null` |

  **判定推荐：** `id === null` 即文件夹，否则文件。**不要用 `metadata == {}` 判定**——后端把 `None` 归一为 `{}`，不可靠。

  **递归盘点：** 接口不原生支持 recursive。对 `id === null` 的条目，把 `name` 作为新 `prefix`（不加前后 `/`）继续调用，直到没有 `id === null` 为止。

## 安全约束

- SQL 仅允许只读语句（SELECT、EXPLAIN、WITH...SELECT）。
- 禁止提交 INSERT / UPDATE / DELETE / DROP / CREATE / ALTER 等有副作用的语句。
- 后端会拒绝写操作并返回 400 错误。

## 错误响应

| code | 含义 | Agent 处理 |
|------|------|-----------|
| `400` + SQL 错误 | SQL 语法错误或写操作被拒绝 | 转述错误，修正 SQL 后重试 |
| `403` | 非 owner | 停止，不绕过 |
