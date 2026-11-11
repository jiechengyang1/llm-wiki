# 创建奥丁取数草稿

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api POST_moma-data_cli_asset-management_odin-fetch --json -d '{"name":"城市成交取数","description":"","tags":[],"configs":[{"request_id":"9028b2ee-fb2b-4f46-8646-ed0be054347e","date_params":{"occur_date":["20260701000000","20260709235959"]},"desc":"","preview_data":{}}]}'
```

示例中的 date_params、preview_data 仅示意结构，必须替换为该配置真实验证过的筛选值和预览结果。

先沿 skill 的 odin_fetch flow 解析参数，读取 [筛选参数](../../odin_fetch/odin_fetch_filter_params.md) 和 [取数预览](../../odin_fetch/odin_fetch_preview.md)。对每个 request_id 用当前用户身份预览，不携带其他资产 asset_id。

## 保存参数

name、description、tags、security_level 见[通则](../index.md)。configs 必须非空，每项包含 request_id（必填）、date_params、desc、preview_data；date_params 使用该配置已验证的筛选值，preview_data 使用其真实预览结果。逐项预览成功后保存，不用一项结果填充其他配置。

[权限预检](precheck.md) 的 request_ids 应覆盖全部配置，任一失败停止。

保存成功记录 data.id。[候选检测](../publish/preflight.md) 的 detail 使用 configs 数组，按需发布。开启定时必须显式 cron；立即同步可通过 config_id 只执行一项，见[执行接口](../sync/run.md)。
