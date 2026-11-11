# moma moma-appcompile api GET_api_moma-app-build_tables

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

列出某应用的数据库表（public schema），自动过滤平台内部表（`_app_` 前缀）。

## Recommended Commands

```bash
moma moma-appcompile api GET_api_moma-app-build_tables --json \
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
| `data.items[].table_name` | 表名，后续 `columns` API 的 `table_name` 参数 |
| `data.items[].table_type` | `BASE TABLE` 或 `VIEW` |
| `data.items[].table_comment` | 表注释 |
| `data.items[].column_count` | 列数 |
| `data.total` | 总表数 |

### 成功响应示例

```json
{
  "errno": 0,
  "data": {
    "items": [
      {
        "table_name": "orders",
        "table_type": "BASE TABLE",
        "table_comment": "订单表",
        "column_count": 8
      }
    ],
    "total": 1
  }
}
```

## 错误响应

| code | 含义 | Agent 处理 |
|------|------|-----------|
| `403` | 非 owner | 停止，不绕过 |
| `404` | 应用不存在 | 重新用 `list` 确认 `chat_id` |
