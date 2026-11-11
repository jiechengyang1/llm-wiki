# moma moma-appcompile api GET_api_moma-app-build_list

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

列出当前登录用户自有的应用（agentic 会话），按最后更新时间倒序分页。返回的 `chat_id` 是后续所有操作的应用标识。

## Recommended Commands

> **必须添加 `--json`。** apiName 必须照抄，禁止短名。

```bash
# 列出自有应用（默认第1页，每页20条）
moma moma-appcompile api GET_api_moma-app-build_list --json

# 分页
moma moma-appcompile api GET_api_moma-app-build_list --json \
  --query "page=2&page_size=50"
```

## Options

query 参数：

| 字段 | 是否必填 | 默认值 | 含义 |
|------|---------|-------|------|
| `scope` | 可选 | `owner` | 当前仅支持 `owner`（自有应用） |
| `page` | 可选 | `1` | 页码，从 1 开始 |
| `page_size` | 可选 | `20` | 每页数量，上限 100 |

## 响应结构

| 字段 | 含义 |
|------|------|
| `data.items[].chat_id` | **后续所有 API 的应用标识** |
| `data.items[].title` | 应用标题 |
| `data.items[].updated_at` | 最后更新时间（ISO 字符串） |
| `data.total` | 总数 |
| `data.page` / `data.page_size` | 当前页信息 |

### 成功响应示例

```json
{
  "errno": 0,
  "data": {
    "items": [
      {
        "chat_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        "title": "我的数据应用",
        "updated_at": "2026-09-18T14:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
}
```

## Workflow

1. 用户只给出应用名/标题时，调用本 API 列出全部应用，按标题精确匹配 `chat_id`。
2. 唯一命中 → 使用该 `chat_id`；多个命中 → 列出候选让用户选择；无命中 → 告知用户确认名称。
3. 上下文已有 `chat_id` 时直接使用，不再重新列出。
