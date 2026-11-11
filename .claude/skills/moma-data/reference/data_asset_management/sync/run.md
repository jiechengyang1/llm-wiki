# 立即提交同步任务

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api 'POST_moma-data_cli_asset-management_{data_asset_id}_sync_run' --json -p 'data_asset_id=123'

# 奥丁取数只执行某一条配置
moma moma-data api 'POST_moma-data_cli_asset-management_{data_asset_id}_sync_run' --json -p 'data_asset_id=123' -q 'config_id=789'

# Excel 追加同步
moma moma-data api 'POST_moma-data_cli_asset-management_{data_asset_id}_sync_run' --json -p 'data_asset_id=123' -q 'sync_mode=incremental'
```

保存定时配置不会自动执行。用户要求立即同步时调用，需满足负责人及发布状态等服务端校验；指标不支持同步。

Query 可选（-q）：

| 字段 | 适用范围 |
|---|---|
| config_id | 奥丁取数只执行某一条配置，不传执行全部；ID 从同步配置获得 |
| sync_mode | Excel 专用 full=覆盖（默认）/incremental=追加；其他类型使用已保存配置，不靠该参数改同步方式 |

返回 data.items 是任务提交结果，queued/pending/running 不能报告为完成；随后轮询 [执行状态](status.md)。请求超时先核实配置和运行状态，不能盲目重复 run。
