# moma moma-appcompile api GET_api_moma-app-build_buckets

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

列出某应用的对象存储桶（Supabase Storage）。返回的 `bucket_id` 是后续 `objects` / `query` API 的桶标识。

## Recommended Commands

```bash
moma moma-appcompile api GET_api_moma-app-build_buckets --json \
  --query "chat_id=<CHAT_ID>"
```

## Options

query 参数：

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `chat_id` | **必填** | 应用 chat_id |

## 响应结构

| 字段 | 含义 |
|------|------|
| `data.items[].bucket_id` | **后续 `objects`/`query` API 的桶标识** |
| `data.items[].name` | 桶名（展示用） |
| `data.items[].public` | 是否公开桶 |
| `data.total` | 桶总数 |

### 成功响应示例

```json
{
  "errno": 0,
  "data": {
    "items": [
      {
        "bucket_id": "uploads",
        "name": "uploads",
        "public": false
      }
    ],
    "total": 1
  }
}
```

## Notes

- 应用不支持对象存储时返回空列表，不报错。
- `bucket_id` 通常等于 `name`，但以 `bucket_id` 字段为准传给后续 API。
