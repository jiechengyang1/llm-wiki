# 创建 Storage 桶

> 在个人 supabase 实例上创建一个新的 Storage 桶。

## 指令

```bash
moma moma-data api POST_moma-data_personal_supabase_create-storage-bucket --json \
  -d '{"id": "my-bucket"}'
```

## 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | string | 是 | - | 桶 ID（同时作为桶名），全局唯一 |
| public | bool | 否 | false | 是否公开访问 |

## 使用示例

```bash
# 私有桶（默认）
moma moma-data api POST_moma-data_personal_supabase_create-storage-bucket --json \
  -d '{"id": "my-assets"}'

# 公开桶
moma moma-data api POST_moma-data_personal_supabase_create-storage-bucket --json \
  -d '{"id": "public-images", "public": true}'
```

## 返回数据

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": {
    "success": true,
    "data": [{"id": "my-assets", "name": "my-assets", "public": false, "created_at": "..."}]
  }
}
```

桶已存在时静默跳过（ON CONFLICT DO NOTHING），`data.data` 为空数组。
