# 创建指标草稿

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api POST_moma-data_cli_asset-management_metric --json -d '{"name":"城市成交指标","description":"","tags":[],"targets":"25667,120849","params":{"pageNo":1,"pageSize":20,"startDate":"20261001","endDate":"20261029","dateType":1,"dim":"performance_city_code"},"response":{"list":[],"columns":[],"mapping":{},"codeMapping":{},"totalCount":0},"custom_mapping":{},"scope":0,"team_id":0}'
```

示例中的 response、custom_mapping 仅示意结构，必须按下文规则用本次真实查询结果组织。

同样是权限预检 → 查询预览 → 草稿 → 按需发布，无同步步骤：

```bash
moma moma-data api POST_moma-data_cli_asset-management_precheck --json -d '{"asset_type":"metric","name":"城市成交指标","targets":"25667,120849","scenario":"create"}'
moma moma-data api POST_moma-data_index_query --json -d '{"targets":"25667,120849","params":{"pageNo":1,"pageSize":20,"startDate":"20261001","endDate":"20261029","dateType":1,"dim":"performance_city_code"},"skip_cache":true}'
```

params 使用 [指标查询契约](../../index/index_query.md)；新建不携带其他资产 asset_id。外层 errno 以及 data.errno（可能是字符串 "0"）都必须成功，真正数据在 data.data。

指标保存 body：

- name、description、tags、security_level 按[创建字段通则](../index.md)填写。
- targets 为逗号分隔的指标 ID，params 原样使用成功查询参数（保留 filter/dateType/dim 等）。
- response 为 {"list":预览前20行,"columns":[{"prop":"字段名","label":"中文名"}],"mapping":原mapping,"codeMapping":原codeMapping,"totalCount":原totalCount}。columns 合并 mapping 和结果行出现的键，空 label 回退字段名，零行也保留列映射。
- custom_mapping 保留页面口径：mapping 字段加 periodMode（general=通用周期，business=业务口径）及可选 dateWindow（页面使用 JSON 字符串）。不要擅自切换口径或丢掉 statistical_name 筛选。
- scope、team_id 可选，沿用页面默认为 0。

将这些字段合入一个 JSON，调用指标保存接口，targets/params 与本次预览保持一致。后续按[发布接口](../publish/publish_asset.md)处理；指标不存在 supabase 同步/分片配置，也不调用 sync/run。
