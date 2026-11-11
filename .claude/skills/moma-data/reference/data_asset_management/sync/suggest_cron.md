# 定时时间推荐流程

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

本文是流程说明，没有名为 suggest_cron 的接口。开启定时前先取推荐时间再让用户选择，不凭空给出固定时刻。

## 指令

```bash
moma moma-data api 'GET_moma-data_cli_asset-management_{data_asset_id}_sync-cron-advise' --json -p 'data_asset_id=123'
```

Hive 和数据模型资产调用此接口，推荐口径与页面一致，服务端已完成底表分区分析和错峰，不要自行计算或改写结果。data.crontab 非空时作为推荐，并原样展示 data.reason；为空时说明 data.reason，表示没有推荐。

## 让用户选择

用 AskUserQuestion：

| 选项 | crontab |
|---|---|
| 每天 {时间}（推荐） | data.crontab；没有推荐时不提供 |
| 保持当前 {时间} | 现值；仅已有定时配置时提供 |
| 其他（手动输入） | 用户输入每天 HH:MM 转为 `M H * * *`，或直接给五段 cron；北京时间 |

手动输入无法识别时让用户重新输入，crontab 不传空串。

奥丁取数没有推荐接口，提供「每天 10:00（页面默认）」和手动输入。Excel 不支持定时，指标不配置同步。

选定后按 [保存同步配置](configure.md) 提交。
