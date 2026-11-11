# moma moma-appcompile api GET_api_moma-app-build_columns

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

获取某应用下指定表的列信息（列名/类型/主键/可空/注释）。表名不存在时返回 404 并附可用表列表。

## Recommended Commands

```bash
moma moma-appcompile api GET_api_moma-app-build_columns --json \
  --query "chat_id=<CHAT_ID>&table_name=<TABLE_NAME>"
```

## Options

query 参数：

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `chat_id` | **必填** | 应用 chat_id |
| `table_name` | **必填** | 表名，只允许字母/数字/下划线，长度 ≤ 63 |

## 响应结构

| 字段 | 含义 |
|------|------|
| `data.table_name` | 表名 |
| `data.items[].column_name` | 列名 |
| `data.items[].data_type` | 数据类型（pg 类型字符串） |
| `data.items[].is_nullable` | 是否可为空 |
| `data.items[].column_default` | 默认值（可为 null） |
| `data.items[].column_comment` | 列注释 |
| `data.items[].is_primary_key` | 是否主键 |
| `data.items[].character_maximum_length` | 字符最大长度（varchar 等） |
| `data.items[].numeric_precision` | 数值精度 |
| `data.items[].numeric_scale` | 数值小数位 |
| `data.total` | 列数 |

### 成功响应示例

```json
{
  "errno": 0,
  "data": {
    "table_name": "orders",
    "items": [
      {
        "column_name": "id",
        "data_type": "uuid",
        "is_nullable": false,
        "column_default": "gen_random_uuid()",
        "column_comment": "",
        "is_primary_key": true
      },
      {
        "column_name": "amount",
        "data_type": "numeric",
        "is_nullable": true,
        "numeric_precision": 10,
        "numeric_scale": 2
      }
    ],
    "total": 2
  }
}
```

## 错误响应

| code | 含义 | Agent 处理 |
|------|------|-----------|
| `404` | 表名不存在 | 错误信息中包含可用表列表，按提示修正 `table_name` |
| `403` | 非 owner | 停止，不绕过 |
