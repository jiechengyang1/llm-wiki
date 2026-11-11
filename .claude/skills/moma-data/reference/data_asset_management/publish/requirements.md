# 读取发布安全告知要求

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api GET_moma-data_cli_asset-management_publish-requirements --json
```

返回 data.notice_required、notice_url 等告知信息。notice_required=true 时展示告知书并取得用户确认后，后续候选检测/发布才传 notice_confirmed=true；没有真实确认不能自动填写。

用户已确认时继续[候选检测](preflight.md)或[发布已有草稿](publish_asset.md)。网关 --yes 不能替代安全告知确认。
