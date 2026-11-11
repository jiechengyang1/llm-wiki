# moma moma-appcompile api GET_api_moma-app-build_objects

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

列出某应用对象存储桶内的文件，支持路径前缀过滤和分页。

## Recommended Commands

```bash
# 列出桶内全部文件（默认前100条）
moma moma-appcompile api GET_api_moma-app-build_objects --json \
  --query "chat_id=<CHAT_ID>&bucket_id=<BUCKET_ID>"

# 下钻目录 + 分页（prefix 不要加前后 /）
moma moma-appcompile api GET_api_moma-app-build_objects --json \
  --query "chat_id=<CHAT_ID>&bucket_id=<BUCKET_ID>&prefix=images&limit=50&offset=0"
```

## Options

query 参数：

| 字段 | 是否必填 | 默认值 | 含义 |
|------|---------|-------|------|
| `chat_id` | **必填** | - | 应用 chat_id |
| `bucket_id` | **必填** | - | 桶 ID（来自 `buckets` API） |
| `prefix` | 可选 | `""` | 下钻目录名，**不要加前后 `/`**，如 `images` |
| `limit` | 可选 | `100` | 返回数量，上限 1000 |
| `offset` | 可选 | `0` | 偏移量，用于翻页 |

## 响应结构

| 字段 | 含义 |
|------|------|
| `data.items` | 对象列表（真实文件 **或** Supabase 聚合的虚拟目录占位） |
| `data.offset` | 当前偏移量 |
| `data.limit` | 当前每页数量 |

### items 条目：文件 vs. 虚拟文件夹

Supabase Storage 的 `.list()` 只返回一层。带下级路径的对象会按**首段路径**聚合成"虚拟目录占位"，与真实文件共用同一 schema，靠字段取值区分：

| 字段 | 真实文件 | 虚拟文件夹 |
|------|---------|-----------|
| `id` | uuid 字符串 | **`null`** |
| `metadata.size` / `metadata.mimetype` | 有值 | 不存在 |
| `created_at` / `updated_at` | ISO 时间 | `null` |

**判定推荐：** `id === null` 即文件夹，否则文件。**不要用 `metadata == {}` 判定**——后端把 `None` 归一为 `{}`，不可靠。

### 成功响应示例（含文件 + 虚拟目录）

```json
{
  "errno": 0,
  "data": {
    "items": [
      {
        "name": "report.pdf",
        "id": "6b2e4c58-9a1d-4a2d-9d1f-0f9c2d1a2b3c",
        "updated_at": "2026-09-18T10:00:00Z",
        "created_at": "2026-09-18T10:00:00Z",
        "metadata": { "size": 204800, "mimetype": "application/pdf" }
      },
      {
        "name": "invoices",
        "id": null,
        "updated_at": null,
        "created_at": null,
        "metadata": {}
      }
    ],
    "offset": 0,
    "limit": 100
  }
}
```

上例中 `report.pdf` 是文件，`invoices` 是虚拟目录（`id: null`）；下钻时传 `prefix=invoices`（**不加前后 `/`**）即可列出 `invoices/` 下的内容。

## Notes

- 文件列表不受 Supabase Storage RLS 控制，通过 owner 校验后可查看桶内所有文件。
- `prefix` 用于下钻目录，**不要加前后 `/`**：
  - ✅ `prefix=folder`
  - ❌ `prefix=folder/`（SDK 容忍，但层级拼接易错）
- **递归盘点全桶**：接口不原生支持 recursive。对 `id === null` 的条目，把 `name` 作为新 `prefix` 继续调用，直到没有 `id === null` 为止。
