# 云端 CLI 资产管理

使用 `/moma-data/cli/asset-management` 的公开 OpenAPI，运行环境只需云端 `moma` CLI，不依赖仓库 `cli/src/commands/*.ts`。身份沿用 moma-shared 的登录与网关透传规则，不切换属主身份。

## 通用调用规则

`moma moma-data api '<apiName>' --json`：`-d` 传一个完整 JSON body，路径参数用 `-p 'data_asset_id=123'`，查询参数用 `-q 'key=value'`，文件上传用 `-F 'file=/absolute/path/data.xlsx'`。

资产 ID（data_asset_id，也是 preflight 的 asset_id）是本组接口返回的 id，或 by-ids/accessible 返回的 asset_id；本组接口返回里的 asset_id 是类型子表主键，不作资产 ID 使用。

调用前可用 `moma moma-data list` 和 `moma moma-data schema '<apiName>' --json` 核对部署版本。接口未出现应说明服务尚未发布/契约尚未刷新，不改调用隐藏的 Web 接口。

write/high-risk-write API 按 moma-shared 和命令返回先 `--dry-run` 核对路径、参数和影响；用户意图已授权且符合共享规则时再追加 `--yes` 执行。`--yes` 不代表同意安全告知或本次扫描风险，不能据此自动设置 notice_confirmed/risk_confirmed。

所有响应先检查 HTTP 状态及外层 errno；权限失败停止当前写入，展示实际申请引导，不改用专家导入、隐藏 Web 路由或其他身份绕过。业务成功还须检查接口特定字段，如预检 data.ok、发布 data.action、调度 items[].cron_error 和同步终态。

## 按操作读取接口文档

只读取本次操作需要的接口。名称中的 GET/POST/PUT 对应实际方法，路径参数保留 `{data_asset_id}`，执行时用 `-p` 传值。

| 分类 | 接口文档 |
|---|---|
| 查询 | [GET 资产列表](query/list_assets.md)、[GET 资产详情](query/get_asset.md) |
| 元数据 | [PATCH 名称/描述/标签](update/update_meta.md)（只改文案与标签，不 POST 新建） |
| 创建 | [POST 权限预检](create/precheck.md)、[POST Hive 草稿](create/create_hive.md)、[PUT Hive 草稿及预览](create/update_hive.md) |
| 创建 | [POST 指标草稿](create/create_metric.md)、[POST 模型草稿](create/create_data_model.md)、[POST 奥丁取数草稿](create/create_odin_fetch.md) |
| 创建 | [POST Excel/CSV 上传](create/upload_excel.md)、[POST Excel/CSV 草稿](create/create_excel.md) |
| 更新 detail | [PUT 各类型草稿回写](update/update_draft.md) |
| 发布 | [GET 安全告知要求](publish/requirements.md)、[POST 候选内容检测](publish/preflight.md)、[POST 发布资产](publish/publish_asset.md) |
| 同步 | [GET 同步配置](sync/get_config.md)、[PUT 定时/分片/索引配置](sync/configure.md)、[POST 立即同步](sync/run.md)、[GET 执行状态](sync/status.md) |
| 同步流程 | [定时时间推荐流程](sync/suggest_cron.md)：Hive 和数据模型调用 sync-cron-advise 取推荐时间 |

## 操作流程

- 新建资产：读对应创建接口 → [数据源权限预检](create/precheck.md) → 用当前参数查询预览 → 保存草稿。Hive 的快照和预览验证由服务端在保存时以当前用户身份重新执行生成；指标的 targets/params 变化后须重新预览，不能虚构 response。
- 发布、编辑已有资产的候选检测仅资产负责人可调用，非负责人直接返回「资产不存在或无权限」。
- 新建并发布：完成预览、组织待保存 body → [安全告知](publish/requirements.md) → [候选检测](publish/preflight.md) → 处理本次风险确认 → 保存草稿 → [发布同一个 ID](publish/publish_asset.md)。候选内容变化要重新检测。
- 发布已有草稿：读详情后调用发布接口，根据 action 补告知、风险确认或 Hive 预览；不要为重试发布重新创建资产。
- **只改名称、描述或标签**：调用 [PATCH 元数据](update/update_meta.md)，不要 POST 同名资产或 PUT 各类型保存接口。
- 改 SQL / 模型 / 取数等 detail：对**同一** `data_asset_id` 使用 [PUT 回写](update/update_draft.md)，已发布须 preflight 与保存 body 一致后再带 `publish_scan_id` 保存。
- Hive 定时/分片：读资产详情和同步配置 → 按[定时时间推荐流程](sync/suggest_cron.md)取推荐时间，让用户选择或手动输入 → 按用户意图保存完整配置。开启定时须资产已发布；保存不立即执行，用户要求立即同步时另调 run，再轮询 status。
- 指标只做预览、保存、发布，不配置或执行同步。模型/奥丁取数开启定时必须显式 cron；Excel 不支持定时任务。

保存草稿、发布、开启定时和立即同步分别按用户意图执行。创建超时后先查本人列表/详情核实，避免重复创建；已创建但发布未完成时返回草稿 ID、当前 action 及下一步。普通 Hive 保存不可改用 `/cli/data-assets/hive-query`，后者属于个人数据专家确认卡导入。

## 创建字段通则

name 必填，description 默认空串，tags 默认 [] 并沿用页面标签结构；security_level 可选，1=C1、2=C2、3=C3、4=C4，按用户声明填写，不能为跳过风险确认自动调高。具体类型字段和预览结构见各创建接口，完整入参以部署版本 OpenAPI schema 为准。
