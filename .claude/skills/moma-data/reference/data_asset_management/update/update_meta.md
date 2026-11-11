# 更新资产名称 / 描述 / 标签

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

用户**只改名称、描述或标签**（不改 SQL、模型参数、取数配置、预览快照等 detail）时，使用本组 PATCH，与页面资产卡片一致。**禁止**为此 POST 同名新资产，也**不要**走各类型的 PUT 保存草稿。

## 指令

```bash
moma moma-data api 'PATCH_moma-data_cli_asset-management_{data_asset_id}_description' --json -p 'data_asset_id=123' -d '{"description":"新的描述"}'

moma moma-data api 'PATCH_moma-data_cli_asset-management_{data_asset_id}_name' --json -p 'data_asset_id=123' -d '{"name":"新的名称"}'

moma moma-data api 'PATCH_moma-data_cli_asset-management_{data_asset_id}_tags' --json -p 'data_asset_id=123' -d '{"tags":["标签A","标签B"]}'
```

## 规则

- 仅资产 owner 可调用；草稿与已发布均可改，**不需要** publish-preflight / publish_scan_id。
- 不影响 detail、state 与同步配置；改完可直接向用户确认，无需重新发布。
- 若用户还要改查询内容或 detail，改走对应类型的 PUT 与[发布流程](../publish/preflight.md)，不要混在本 PATCH 里假装已保存 detail。
