# 创建数据模型草稿

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api POST_moma-data_cli_asset-management_data-model --json -d '{"name":"城市新签模型","description":"","tags":[],"model_id":12345,"model_name":"","cluster_type":"default","sql_parse":0,"query_params":{"dimensions":[{"columnId":101,"alias":"统计日期"}],"measures":[],"page":{"pageNo":1,"pageSize":100}},"response":{"list":[],"columns":[]},"scope":0,"team_id":0}'
```

示例中的 query_params、response 仅示意结构，必须替换为本次成功预览的真实参数和结果。

先 [权限预检](precheck.md)，带 model_id、cluster_type 和真实 query_params。然后使用 [模型查询](../../model/model_query.md) 预览：`POST_moma-data_odin_model_query` body 的 modelId 对应 model_id、query 对应 query_params，secret 集群映射 high_confidential，其余 public；新建不带其他资产 asset_id。

## 保存参数

name、description、tags、security_level 见[通则](../index.md)。model_id 必填；model_name 默认空串，cluster_type 默认 default，sql_parse 默认 0；query_params 原样使用成功预览参数，response 使用真实模型查询结果。scope、team_id 默认 0。完整字段以 OpenAPI schema 为准。

成功后记录 data.id，按需[发布](../publish/publish_asset.md)。开启定时必须显式 crontab；普通模型不支持 Hive 取模/索引，专家导入模型时间分片按详情 model_slice 契约处理，见[同步配置](../sync/configure.md)。
