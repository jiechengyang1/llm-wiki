# 列出桶内对象

> 列出指定 Storage 桶内的对象，支持路径前缀过滤。

## 指令

```bash
moma moma-data api GET_moma-data_personal_supabase_list-storage-objects --json \
  -q "bucket_id=my-assets&limit=20"
```

## 参数说明

Query 参数（-q key=v）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| bucket_id | string | 是 | - | 桶 ID |
| prefix | string | 否 | 空 | 路径前缀过滤，如 `images/` |
| limit | int | 否 | 100 | 返回条数上限（1-1000） |

## 使用示例

```bash
# 列出桶内全部对象
moma moma-data api GET_moma-data_personal_supabase_list-storage-objects --json \
  -q "bucket_id=my-assets"

# 只看 images/ 目录下的文件
moma moma-data api GET_moma-data_personal_supabase_list-storage-objects --json \
  -q "bucket_id=my-assets&prefix=images/"
```

## 返回数据

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": [
    {
      "id": "...",
      "name": "images/photo.jpg",
      "bucket_id": "my-assets",
      "mimetype": "image/jpeg",
      "size": "102400",
      "created_at": "2024-10-01T12:00:00+00:00",
      "updated_at": "2024-10-01T12:00:00+00:00",
      "last_accessed_at": "2024-10-01T12:00:00+00:00"
    }
  ]
}
```
