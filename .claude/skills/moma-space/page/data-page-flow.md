# Database 驱动页流程

本流程中的已明确 API 直接调用；写操作首次调用即携带 `--yes`。

用于列表、看板、筛选、排序、分页、统计、表单和记录增删改。Agent 构建期使用 `moma-space` CLI；浏览器运行期使用独立预览页注入的 Database SDK。

## 1. 创建工程目录

新建 Database 驱动页前，先按 [`entry.md`](entry.md) 调用固定 `GET_api_v1_tools_storage_space_list-user-spaces` API 解析目标 Space；即使用户指定 ID 或标题也必须从返回的 space 列表匹配出真实 ID，未指定时取返回顺序中第一个 `mode == "team"` 的 space。同标题多项、指定项不存在或不可见、无 team space 时停止并报告，不询问。后续 `space_id` / `space_root` 只使用选中返回项的真实 ID。

已有页面编辑分支直接进入 [`edit-flow.md`](edit-flow.md)，沿用 `node-info` 或 `files_query` 节点结果中的 `spaceId`，不重新选择目标 Space。

解析目标 Space 后，新页面工作必须先直接创建远端工程目录：

```bash
moma moma-space api POST_api_v1_tools_storage_file_create-folder \
  --data '{"space_id":"<space_id>","title":"记账本"}' \
  --yes \
  --json
```

从响应读取文件夹 ID，后续统一记为 `<project_folder_id>`，并记录工程目录相对路径 `<project_folder_relative_path>`。持久化 HTML 必须显式使用 `"parent_id":"<project_folder_id>"`；持久化 Markdown 的 `write_file` 不使用 `parent_id`，其 `filepath` 必须以 `<project_folder_relative_path>/` 为前缀。Database 创建时在 `schema` 中传 `"parent_id":"<project_folder_id>"`，使其落在工程目录内，再保存返回的 `database_id` 作为本页面工程的关联资源。HTML 和 Markdown 均不得放在 Space 根目录。

## 2. 分析并确定读写模式

按 [`html-analysis.md`](html-analysis.md) 输出 canonical analysis：

- 持续查询、筛选、排序、分页、看板但不改记录 → `database-readonly`；
- 表单持久化、记录新增/更新/删除 → `database-readwrite`。

readonly 页面不生成写操作。readwrite 只生成真实 SDK 文档已验证的字段写入结构。

## 3. 创建或复用 Database

已有表先读取 schema。是否复用应按用户的数据共享意图、权限与目标 Space 判断；需要隔离数据时创建带 `"parent_id":"<project_folder_id>"` 的项目专用副本（落在工程目录内），需要共享数据时可直接保留已有 `database_id`：

```bash
moma moma-space api POST_api_v1_tools_storage_table_get-database-schema \
  --data '{"database_id":"<database_id>"}' \
  --json
```

需要新表时，直接创建；`schema` 传 `space_id`、`title`、`properties` 和 `"parent_id":"<project_folder_id>"`，使 Database 落在工程目录内。**`config` 类型写法以 [`database/page-database.md`](database/page-database.md) 的「config 类型以后端 schema 为准」对照表为准**——`number`/`currency` 必须用对象 `{"number":{}}`/`{"currency":{}}`，不能写成数字 `{"number":0}`，否则后端报 `INVALID_REQUEST`：

```bash
moma moma-space api POST_api_v1_tools_storage_table_create-database \
  --data '{"schema":{"space_id":"<space_id>","title":"记账本","parent_id":"<project_folder_id>","properties":[{"name":"标题","config":{"text":""}},{"name":"金额","config":{"number":{}}},{"name":"状态","config":{"select":{"options":[{"text":"待处理","style":1},{"text":"已完成","style":2}]}}}]}}' \
  --yes \
  --json
```

已有表缺字段时，直接添加：

```bash
moma moma-space api POST_api_v1_tools_storage_table_add-field \
  --data '{"database_id":"<database_id>","property":{"name":"负责人","config":{"text":""}}}' \
  --yes \
  --json
```

字段变更后再次调用 `POST_api_v1_tools_storage_table_get-database-schema`，后续只使用返回的真实字段名和 `config`。不要假设 property 存在通用 `type` 字段。

## 4. 写入可选初始数据

每批最多 100 条：

```bash
moma moma-space api POST_api_v1_tools_storage_table_batch-add-records \
  --data '{"database_id":"<database_id>","records":[{"标题":{"text":"示例任务"},"状态":{"select":"待处理"}}]}' \
  --yes \
  --json
```

构建期查询：

```bash
moma moma-space api POST_api_v1_tools_storage_table_query-database-records \
  --data '{"database_id":"<database_id>","page_size":100}' \
  --json
```

`has_more=true` 时把 `next_cursor` 作为下一页 `cursor`。

## 5. 生成 SDK 页面

最终 HTML 写入真实 Database ID，并使用推荐入口：

```javascript
const db = window.__SPACE_PAGE__.database;
const DATABASE_ID = "<real-database-id>";
```

按 [`database/database-sdk-contract.md`](database/database-sdk-contract.md) 和 [`database/database-sdk-schema.md`](database/database-sdk-schema.md) 生成运行时代码：

1. `db.getSchema({ database_id: DATABASE_ID })` 读取真实 schema。
2. `db.query` 使用 `database_id`、`cursor`、`page_size`，读取 `results`、`next_cursor`、`has_more`。
3. 每条记录从 `record.record_id` 和 `record.fields` 读取，不能使用 `_id` 或扁平字段。
4. 新增用 `db.addRecord({ database_id, record })`。
5. 更新用 `db.updateRecord({ database_id, record_id, properties })`。
6. 删除用 `db.deleteRecord({ database_id, record_id })`。
7. 图片用 `db.uploadImage({ file })`，不转 base64；把 URL 写进记录前先验证该字段的真实写入结构。
8. `db.onUpdated` 只监听当前 iframe 自己成功完成的增删改；事件后重新 query/getRecord。
9. 所有异步调用使用 try/catch，页面实现 loading、empty、ready、error、submitting。
10. SDK 没有 ready、内置超时或取消；需要避免永久 loading 时使用业务层 Promise.race 超时。

运行期 SDK 和 Agent CLI 都使用 snake_case，但不能把 Gateway 命令或批量请求结构直接写进页面 SDK 调用。

## 6. 页面产物和检查

- 最终 HTML 不超过独立预览页 2 MiB 上限；
- SDK 仅在 `/mspace/page/:id` 独立预览 iframe 中可用；
- 保持单 HTML，按 [`artifact-contract.md`](artifact-contract.md) 完成布局和页面状态；
- 按 [`resource-normalization.md`](resource-normalization.md) 处理资源；
- 执行 `lint_database_sdk_usage.py` 和 `lint_page_resources.py`，均无 error；
- 重新分析 final HTML，验证全部真实 Database ID。

## 7. 上传、关系与发布

```bash
moma moma-space api POST_api_v1_tools_storage_file_upload-node \
  --data '{"space_id":"<space_id>","parent_id":"<project_folder_id>"}' \
  --file 'file=<temporary-workdir>/记账本.html' \
  --yes \
  --json
```

`--file` 必须用 `file=<path>` 格式。`upload-node` 以 `--file` 指定文件的 basename 作为上传后 web 节点的标题（即 Space 中可见的文件名），因此临时 HTML 必须用中文 `<page-slug>.html` 命名（如 `/tmp/.moma-tmp/记账本.html`），不得用英文 slug 导致节点标题变英文。`parent_id` 必须为本次创建的 `<project_folder_id>`；`space_id` 实测必填。返回 `AppNodeVO`，`nodes` 为空数组，从根字段读取 `id` 作为 web node ID。

取返回节点 ID 后，按 [`page-database-relation.md`](page-database-relation.md) 处理 final ID 集；只有当前服务存在正式 relation API 时登记元数据。然后发布：

```bash
moma moma-space api POST_api_v1_tools_storage_file_publish-page \
  --data '{"node_id":"<uploaded_node_id>"}' \
  --yes \
  --json
```

取得发布 URL 后清理本次临时 HTML 和转换产物，回复：

```text
页面已发布：<publishUrl>
```
