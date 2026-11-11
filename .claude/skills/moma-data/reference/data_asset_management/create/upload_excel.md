# 上传并预览 Excel/CSV

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api POST_moma-data_cli_asset-management_excel_upload --json -F 'file=/absolute/path/data.xlsx'
```

multipart 的 file 为必填真实文件，旧版 CLI 不支持 -F 时按共享升级规则处理，不能用本地文件路径充当 S3 key。

Query 可选 asset_id（默认 0，更新已有资产时沿用上次列类型）、reuse_column_types（默认 true，false 忽略已保存类型重新识别）。

成功读取 data.s3_key、file_name、file_type、file_size、sheet_name、column_definitions、row_count、response；检查并展示 warnings 及合并相关 merge_metadata。上传/预览不等于资产已创建，后续将这些真实字段传给 [Excel 保存接口](create_excel.md)。
