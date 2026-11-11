# 创建前数据源权限预检

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api POST_moma-data_cli_asset-management_precheck --json -d '{"asset_type":"hive","name":"城市成交明细","raw_sql":"SELECT city_code,deal_date FROM rpt.example_table","odin_cluster":"standard","scenario":"create"}'
```

## 请求参数

asset_type 使用 hive / metric / data_model / odin_fetch / excel；name 用于展示。新建明确传 scenario=create（接口默认 resume），按类型带以下字段：

| 类型 | 数据源参数 |
|---|---|
| hive | raw_sql、odin_cluster |
| metric | targets（逗号分隔多个指标 ID），单指标也可 index_id |
| data_model | model_id、cluster_type、query_params；query_params 使用真实查询参数，不能省略后将上游参数异常当权限通过 |
| odin_fetch | request_ids 数组，覆盖所有待保存配置；任一失败则停止 |
| excel | 使用真实文件上传结果，预检不能代替上传及保存校验 |

已有资产更新可传 asset_id、scenario=update；target_ucid 仅用于明确的转让预告，不在普通创建中指定其他身份。其他 scenario 包括 copy / resume / transfer，按实际操作使用。

## 结果处理

外层 errno=0 且 data.ok=true 才继续。失败展示 error_type、identifiers、action、recover_hint 并停止保存/发布；保存处理仍会再次校验数据源权限。
