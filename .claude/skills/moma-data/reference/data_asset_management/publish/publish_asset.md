# 发布已有草稿

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api 'POST_moma-data_cli_asset-management_{data_asset_id}_publish' --json -p 'data_asset_id=123' -d '{"notice_confirmed":false,"risk_confirmed":false,"scan_id":456}'
```

新建并发布时先完成[安全告知](requirements.md)、[候选检测](preflight.md)和草稿保存，发布同一个 ID。已有草稿可直接调用本接口，由服务端执行检查。

Body：notice_confirmed、risk_confirmed 默认 false；scan_id 可选，传本次内容对应的扫描记录。风险确认必须针对当前返回的风险和扫描，网关 --yes 不替代业务确认。

示例中的确认字段必须按本次真实用户确认填写。没有 scan_id 可省略。对已有草稿可直接调用发布接口，由服务端执行检查；返回风险确认后用同一资产 ID、相应 scan_id 和实际确认结果重试，不重新创建。

errno=0 仍可能返回 notice_required / risk_confirmation_required / preview_required，均不是发布成功。preview_required 时按 [Hive 草稿回写](../create/update_hive.md)流程补预览。只有 action=published 才报告发布完成。返回 advisory_risks/advisory_level 时如实提醒。

如果草稿已创建而发布未完成，告诉用户草稿 ID、当前 action 和下一步，不能报告全失败后重新创建。发布可能附带该类型的后端同步副作用（如 Excel 即时同步），按返回说明。
