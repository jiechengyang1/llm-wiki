# 创建 Excel/CSV 草稿

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api POST_moma-data_cli_asset-management_excel --json -d '{"name":"城市目标表","description":"","tags":[],"s3_key":"<upload 返回的 s3_key>","file_name":"data.xlsx","file_type":"xlsx","file_size":10240,"sheet_name":"Sheet1","column_definitions":[],"row_count":100,"response":{"list":[],"columns":[]}}'
```

先 [上传并预览真实文件](upload_excel.md)，再保存。

body：name 必填；description、tags、security_level 见[通则](../index.md)；s3_key 必填且必须来自 upload 响应。file_name、file_type、file_size、sheet_name、column_definitions、row_count、response 均使用上传结果，不凭空构造。file_type 默认 xlsx，response 是前 N 行真实预览快照。

成功记录 data.id，再按用户意图[发布](../publish/publish_asset.md)。发布可能触发该类型的即时同步副作用，按接口返回说明；Excel 不支持定时任务。手动执行支持覆盖/追加，见[立即同步](../sync/run.md)。
