# 更新已有资产草稿（改 detail）

[管理流程与接口索引](../index.md)。**已发布或草稿，若只改名称、描述、标签**，用 [PATCH 元数据](update_meta.md)，不要走下面各类型 PUT。

## 接口

| 类型 | 方法 | 说明 |
|---|---|---|
| Hive | `PUT .../hive-query/{data_asset_id}` | 见 [Hive 草稿回写](../create/update_hive.md) |
| 指标 | `PUT .../metric/{data_asset_id}` | body 与 POST 创建同类字段；targets/params 变化须先重新预览 |
| 数据模型 | `PUT .../data-model/{data_asset_id}` | body 与 POST 创建同类字段 |
| 奥丁取数 | `PUT .../odin-fetch/{data_asset_id}` | configs 结构与 POST 一致 |
| Excel | `PUT .../excel/{data_asset_id}` | 按 OpenAPI schema 提交 |

先 [GET 详情](../query/get_asset.md)，在现值基础上改字段，防止默认值覆盖。

## 已发布资产（state=2）

覆盖 detail 前须 [候选检测](../publish/preflight.md)：`detail` / 保存 body 与 preflight **完全一致**（含 Hive 的 `detail.response` 快照）。保存时传 `publish_scan_id` 与必要的 `publish_risk_confirmed`。Hive 须**先预览、再 preflight、再 PUT 同一份 response**；不是 response 结构猜不对，而是 **preflight 与 PUT 必须是同一次预览结果**（metric/odin 在 PUT 里不重跑预览，所以更容易对齐）。

Hive CLI：草稿且查询配置变化时服务端预览；已发布带 `publish_scan_id` 时传与 preflight 相同的 `response`，不再二次预览。仅改 name/description/tags 应走 PATCH，不要 PUT Hive。
