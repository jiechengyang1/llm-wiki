# 读取同步配置

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api 'GET_moma-data_cli_asset-management_{data_asset_id}_sync' --json -p 'data_asset_id=123'
```

仅负责人可读对应同步配置，指标不支持同步。返回 data.items、summary、model_slice。items 包含现有开关、cron、同步方式、重试/通知、上次结果等；Hive 还附带 slice_field、slice_mode、slice_mod_n、index_sql。

修改配置前读取此接口及[资产详情](../query/get_asset.md)，保留未要求修改的字段。summary.effective_enabled 才表示当前生效，paused_reason 说明暂停原因。

无同步行可能返回 items=[]，Hive 分片/索引从资产 detail 读取。model_slice 描述特殊导入模型时间分片能力。写配置见 [PUT 同步配置](configure.md)，实际执行进度见 [GET 状态](status.md)。
