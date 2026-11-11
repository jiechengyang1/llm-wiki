# 创建 Hive 草稿

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api POST_moma-data_cli_asset-management_hive-query --json -d '{"name":"城市成交明细","description":"","tags":[],"raw_sql":"SELECT city_code,deal_date FROM rpt.example_table","odin_cluster":"standard","engine":"sparksql","source_mode":"sql","table_code":"","db_name":""}'
```

## 流程

1. 收集页面同款参数：名称、描述、标签、SQL、集群、引擎、来源模式、列类型、安全等级。查询参数可以从用户已有 SQL 获取，不能替用户猜分区或指标口径。
2. 按 [权限预检接口](precheck.md)传 asset_type=hive、raw_sql、odin_cluster、scenario=create，只有 data.ok=true 才继续。

3. 需要先给用户看结果时，用完全相同的 SQL、集群和引擎查询预览（长查询需允许等待，不因超时盲目重复提交）。保存接口会再由服务端以当前用户身份执行同一查询并写入快照，此步只用于展示和确认：

```bash
moma moma-data api POST_moma-data_hive_execute-sql --json -d '{"sql":"SELECT city_code,deal_date FROM rpt.example_table","odin_cluster":"standard","engine":"sparksql"}'
```

不带其他资产的 asset_id，以当前用户权限预览。成功结果在 data.list、data.columns；展示 queryId 和非空 warn。必须有列结构才能标记预览成功。保持原 SQL，包括 Odin 分区变量；只加 LIMIT 得到的预览不能用于验证未加 LIMIT 的 SQL。

4. 组织保存 body，字段与页面一致：

| 字段 | 规则 |
|---|---|
| name / description / tags | 名称必填，描述默认空串，tags 默认 []，沿用页面标签结构 |
| raw_sql | 刚刚预览成功的原 SQL |
| odin_cluster | standard / high_confidential / financial，默认 standard |
| engine | 空串=默认，tez / hive / sparksql；仅 standard 生效 |
| source_mode | sql / table；sql 时 table_code、db_name 传空串 |
| table_code / db_name | table 模式填写选择的物理表 code 和库名，不能凭显示名称猜 |
| response / response_row_count / preview_verified | 不需要传；服务端保存前以当前用户身份执行预览，自动写入快照、行数和预览验证状态，传入的值会被忽略 |
| column_types | 可选 {"列名":"text/int/float/bool"}；省略由服务自动推断 |
| security_level | 可选 1=C1、2=C2、3=C3、4=C4；由用户声明，不为绕过风险确认自动调高 |

调用 Hive 保存接口。服务端预览失败（无表权限、SQL 错误、限流等）时不保存，按返回的 errmsg 处理。保存仅创建草稿，返回 data.id，记录该 ID。创建超时后先查本人列表/详情核实，避免重复创建。

权限预检见 [precheck](precheck.md)，发布见 [发布接口](../publish/publish_asset.md)。[候选检测](../publish/preflight.md)的 detail 仍需带本次真实预览的 response，以便检测字段；与保存后服务端快照字段不一致时，发布会要求重新检测。
