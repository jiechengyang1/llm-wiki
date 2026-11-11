# 查询本人资产及草稿

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api GET_moma-data_cli_asset-management --json -q 'view=owned&page=1&page_size=20'
```

Query 参数：asset_type、keyword、view、state、team_id、ids、page、page_size、lite、exclude_report_components。view=owned 查本人；state=1 草稿/2 已发布；ids 为逗号分隔 ID；page 从 1 开始，page_size 默认 20、最大 2000；lite=1 可省略指标预览结果，打开详情再取。

读取 data.items、data.total、data.page、data.page_size，按列表和分页信息展示，核对资产 ID、名称、类型及状态。创建超时后用本人列表核实是否已落库，避免重复创建。指定资产后用 [GET 详情](get_asset.md) 获取当前字段，不能仅凭同名认定为同一资产。
