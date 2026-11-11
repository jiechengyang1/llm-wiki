# 查询同步执行状态

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api 'GET_moma-data_cli_asset-management_{data_asset_id}_sync_status' --json -p 'data_asset_id=123'
```

在 [run](run.md) 后轮询，返回 data.items 和 summary，按实际 sync_status、sync_status_text、进度和错误展示。

queued/pending/running/waiting 均未完成；success/failed/cancelled 为本次实际终态，按结果报告，不自动重复执行任务。多项配置分别展示失败/成功，不能把部分成功当全部完成。

定时是否生效检查 summary.effective_enabled、paused_reason，保存调度时的 cron_error 在[配置接口](configure.md)响应中检查；数据成功不代表 CronJob 创建成功。
