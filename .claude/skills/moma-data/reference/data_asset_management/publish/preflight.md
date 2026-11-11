# 保存前检测候选内容

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api POST_moma-data_cli_asset-management_publish-preflight --json -d '{"asset_id":0,"asset_type":"hive","name":"城市成交明细","description":"","tags":[],"detail":{"raw_sql":"SELECT city_code,deal_date FROM rpt.example_table","odin_cluster":"standard","engine":"sparksql","source_mode":"sql","table_code":"","db_name":"","response":{"columns":["city_code","deal_date"],"rows":[]}},"notice_confirmed":false}'
```

示例中的 detail 必须替换为完整待保存 body，notice_confirmed 按真实安全告知确认填写。

新建并发布时，在保存前检测尚未落库的完整候选内容，避免用户取消发布后仍改动线上内容。先按 [安全告知](requirements.md) 完成必要确认。

## Body

| 字段 | 规则 |
|---|---|
| asset_id | 新建=0；编辑传现有 ID |
| asset_type | hive / metric / data_model / odin_fetch / excel |
| name / description / tags | 与待保存 body 完全一致 |
| detail | 待保存 body；odin_fetch 使用 configs 数组 |
| notice_confirmed | 只按真实安全告知确认填写，默认 false |
| security_level | 本次用户声明等级 1–4；新建时与保存 body 一致，不能为绕过风险自动调高 |

Hive sql 模式 table_code/db_name 清空，使候选指纹与保存结果一致。SQL、查询参数、结构或快照等候选内容变动时重新检测，不能复用旧扫描。

**已发布 Hive 改 SQL**：先 `execute-sql` 得到预览快照 → 用该快照填 preflight 的 `detail.response` → PUT 时传**相同** `response` 与 `publish_scan_id`（勿指望 GET 详情里的 response；CLI PUT 不会在带 scan 时再预览一次）。

## 结果处理

- notice_required：先完成告知，再重试。
- risk_confirmation_required：展示本次 risks，取得用户确认并保留 scan_id。确认后继续保存，再发布同一 ID 时传对应 scan_id 和实际 risk_confirmed。
- security_check_passed：继续保存，保留返回的 scan_id 用于发布。

errno=0 不代表已发布。候选通过/风险已确认后保存草稿，再调用[发布接口](publish_asset.md)。取消风险确认时停止发布，不更改候选等级跳过检测。
