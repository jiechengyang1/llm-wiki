# 初始化个人 supabase 实例

> 个人实例首次使用前必须先调用，创建 `public.execute_sql` RPC 函数并将 schema 暴露给 PostgREST。
> 已初始化过可跳过。

## 指令

```bash
moma moma-data api POST_moma-data_personal_supabase_create-and-expose-schema --json
```

## 参数说明

无需参数，身份由 CLI 凭证自动注入。

## 返回数据

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": {
    "success": true,
    "schema": "public",
    "message": "个人实例初始化完成",
    "warnings": null
  }
}
```

`warnings` 非空时说明部分权限语句已存在（属正常现象，不影响使用）。

## 何时调用

- 第一次对个人实例执行任何操作前
- 调用 `execute-sql` 报 "execute_sql function not found" 时
