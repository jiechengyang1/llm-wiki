# 列出 Storage 桶

> 列出个人 supabase 实例上所有 Storage 桶。

## 指令

```bash
moma moma-data api GET_moma-data_personal_supabase_list-storage-buckets --json
```

## 返回数据

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": [
    {
      "id": "my-assets",
      "name": "my-assets",
      "owner": null,
      "public": false,
      "avif_autodetection": false,
      "file_size_limit": null,
      "allowed_mime_types": null,
      "created_at": "2024-10-01T12:00:00+00:00",
      "updated_at": "2024-10-01T12:00:00+00:00"
    }
  ]
}
```
