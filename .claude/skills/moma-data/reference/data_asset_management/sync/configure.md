# 保存定时、分片、索引配置

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api 'PUT_moma-data_cli_asset-management_{data_asset_id}_sync' --json -p 'data_asset_id=123' -d '{"enabled":1,"crontab":"<用户选定的 cron>","sync_mode":"full","retry_interval":0,"notify_mode":"all"}'
```

先 [GET 同步配置](get_config.md)及[资产详情](../query/get_asset.md)，展示现值并按用户要求改动。PUT 使用完整定时配置：enabled、crontab、sync_mode、retry_interval、notify_mode 均必填；用户没提到的字段，已有配置沿用现值，首次配置用页面默认值（即上方示例：全量、不重试、成功和失败都通知），不自行改选。分片、索引字段省略/null 保持现值，空字符串清空。一次 PUT 对资产的所有同步行统一生效（奥丁取数每个取数配置一行）。

| 页面配置 | CLI body |
|---|---|
| 定时开关 | enabled=0/1；开启需资产已发布 |
| 定时任务 | crontab 五段 cron，北京时间（Asia/Shanghai）；开启定时前先按[定时时间推荐流程](suggest_cron.md)取推荐时间再让用户选择 |
| 同步方式 | sync_mode=full / incremental；具体增量行为沿用资产执行服务 |
| 时间分片 | slice_field 为查询结果中的时间字段，slice_mode=datetime |
| 取模分片 | slice_field 为可取模的字段，slice_mode=mod，slice_mod_n 为 2–100 |
| 不分片 | Hive slice_field="" |
| 索引配置 | index_sql 为创建索引 DDL，目标表用 {table}；多条用 ; 分隔；空串清空 |
| 失败重试 | retry_interval 秒，0=不重试；仅 Hive 生效 |
| 通知时机 | notify_mode=failure / success / all |

分片和索引与定时开关独立：关闭定时也可以保存这些配置。无同步行的草稿可能返回 items=[]，此时 Hive 分片/索引看资产详情；不是任务已开启。关闭状态下首次配置没有同步行时，cron/重试等不创建新行，开启时重新提交完整参数。

保存只写配置/创建 CronJob，不立即取数。检查 items[].cron_error；存在时说明配置已保存而调度未成功，告知后重试配置，不能声称任务已正常运行。summary.effective_enabled 和 paused_reason 用于判断任务是否实际生效。

模型和奥丁取数开启定时必须传非空 crontab；普通模型不支持 Hive 取模/索引，专家导入模型 slice_field 按 model_slice 契约处理。Excel 不支持定时，指标不调用本接口。用户要求立即同步时单独调用 [run](run.md)，随后轮询 [status](status.md)。
