# 更新 Hive 草稿及回写预览

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api 'PUT_moma-data_cli_asset-management_hive-query_{data_asset_id}' --json -p 'data_asset_id=123' -d '<完整编辑body>'
```

先 [GET 详情](../query/get_asset.md)。**仅改描述/名称/标签**时用 [PATCH 元数据](../update/update_meta.md)，不要调用本接口。

本接口由服务端在 **SQL、集群、引擎、source_mode、底表名等查询配置变化时** 以当前用户身份重新执行预览并回写快照；仅改元数据时不重跑预览。预览失败不回写。仅负责人或可编辑的团队管理员可调用。

body 的 name 必填；携带原 description、tags、source_mode、table_code、db_name、column_types、security_level、raw_sql、odin_cluster、engine 等完整编辑字段，防止默认值覆盖。

**草稿（state=1）**：`response` / `preview_verified` 不必传，查询配置变化时由 CLI 服务端重新预览并回写。

**已发布（state=2）改 SQL 等查询配置**：须先对**新 SQL** 做 Hive 预览（如 `execute-sql`），用**同一份**预览结果依次完成 [preflight](../publish/preflight.md) 的 `detail.response` 与本次 PUT 的 `response`，并传 `publish_scan_id` / `publish_risk_confirmed`。CLI **不会**在 PUT 时再跑第二次预览（与页面「检查并发布更新」一致）；preflight 与 PUT 的 SQL、集群、source_mode、快照不一致会报「待保存内容与安全检查内容不一致」。已发布详情接口可能不返回 `response`，不能从 GET 详情抄快照。

仅改 name/description/tags 用 [PATCH 元数据](../update/update_meta.md)，不要走本 PUT。

成功后核对 data.id 和预览状态；[发布](../publish/publish_asset.md) 返回 preview_required 时，回写同一草稿再重试发布，不新建副本。
