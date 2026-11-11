# 页面产物、发布与清理合同

本流程中的已明确 API 直接调用；写操作首次调用即携带 `--yes`。

## 1. 远端工程目录与最终产物

每个新页面工程必须先创建 MOMA Space 远端工程目录；已有页面编辑复用当前父目录。远端文件结构必须满足：

```text
<project-folder>/
├── <page-slug>.html
└── <related-name>.md
```

- 工程目录名、HTML 文件名、Markdown 文件名、Database 名称必须使用中文（如「记账本/记账本.html」「记账说明.md」）；`<page-slug>`、`<related-name>` 即中文短名。**本地临时 HTML 文件的 basename 会成为 `upload-node` 上传后的 web 节点标题，因此临时文件也必须用中文命名（如 `/tmp/.moma-tmp/记账本.html`），不得用英文 slug。** Database 创建时应在 `schema` 中传 `"parent_id":"<project_folder_id>"`；创建成功后，以响应中的 `database_name` 作为真实 Database 名，以 `database_id` 作为页面运行期 SDK 标识。
- HTML 上传时使用 `<project_folder_id>` 作为 `parent_id`；Markdown 使用 `<project-folder-relative-path>/<related-name>.md`。
- Database 创建请求应在 `schema` 中传 `"parent_id":"<project_folder_id>"`；保存返回的真实 `database_id`，通过最终 HTML 和项目文档建立逻辑关联。
- 新页面禁止把 HTML、Markdown 或 Database 散落到 Space 根目录或其他目录；Database 也应落在工程目录内。
- 按用户意图可以复用已有 Database（不新建），也可以创建项目专用副本（副本须带 `"parent_id":"<project_folder_id>"`）。
- `<temporary-workdir>/<page-slug>.html` 只表示上传前的本地副本，不是远端工程目录。
- CSS 和页面脚本优先内联。
- 静态页直接渲染内容。
- 动态页写入真实 Database ID，并使用容器注入的 Database SDK。
- 上传并发布后的 web 节点、工程目录内 Markdown，以及页面关联的 Database，都是保留的远端工程产物。

## 2. 操作 API

| 目的 | API |
|---|---|
| 解析新页面目标 Space | 固定使用 `GET_api_v1_tools_storage_space_list-user-spaces`；这是新页面目标空间的唯一来源，指定 ID/标题也必须从返回 space 中取得真实 ID |
| 查询已有页面节点 | `POST_api_v1_tools_storage_file_node-info`、`GET_api_v1_tools_files_query`；编辑沿用节点返回的 `spaceId`，不重新默认选择 |
| 创建远端工程目录 | `POST_api_v1_tools_storage_file_create-folder` |
| 下载已有 HTML | `GET_api_v1_tools_files_query` 定位并检查权限，再用 `POST_api_v1_tools_file_presigned_url` 获取 URL，下载到 `/tmp/.moma-tmp/` |
| 上传 HTML web 节点 | `POST_api_v1_tools_storage_file_upload-node` |
| 发布并返回 URL | `POST_api_v1_tools_storage_file_publish-page` |

## 3. 建立工程目录并上传

新页面必须先按 [`entry.md`](entry.md) 调用以下固定 API 解析目标 Space；无论用户是否指定 ID 或标题，后续都只使用选中返回项的真实 ID。用户未指定 Space 时，按响应顺序选择第一个 `mode == "team"` 的 space，不询问、不回退个人空间：

```bash
moma moma-space api GET_api_v1_tools_storage_space_list-user-spaces \
  --query 'pageQuery={"page_no":1,"page_size":100}' --json
```

新页面的第一项持久化操作是创建远端工程目录：

```bash
moma moma-space api POST_api_v1_tools_storage_file_create-folder \
  --data '{"space_id":"<space_id>","title":"记账本"}' \
  --yes \
  --json
```

若工程目录需要放在用户指定的已有父目录下，额外传该父目录 `parent_id`。保存响应中的 `id` 为 `<project_folder_id>`，并记录工程目录相对路径。目标父目录和名称明确后直接执行上例，首次调用携带 `--yes`。

然后把 HTML 上传到该目录（`--file` 必须用 `file=<path>` 格式）：

```bash
moma moma-space api POST_api_v1_tools_storage_file_upload-node \
  --data '{"space_id":"<space_id>","parent_id":"<project_folder_id>"}' \
  --file 'file=<temporary-workdir>/记账本.html' \
  --yes \
  --json
```

`POST_api_v1_tools_storage_file_upload-node` 只接受 `.md` / `.html`，同名文件覆盖。页面场景的 `space_id` 必填且必须是固定 API 选中返回项的真实 ID；新页面的 `parent_id` 必填且必须是本工程目录 ID。返回 `AppNodeVO`，`nodes` 为空数组，从根字段读取 `id` 作为 web node ID。

## 4. 发布

```bash
moma moma-space api POST_api_v1_tools_storage_file_publish-page \
  --data '{"node_id":"<web_node_id>"}' \
  --yes \
  --json
```

从直接返回值或 Gateway `data` 中取得 publish URL。

## 5. 页面检查

### 通用

- 需求或来源已通过 `python3 page/analyze_page.py ...` 生成 canonical analysis，并按 [`page-analysis-schema.md`](page-analysis-schema.md) 选定页面模式。
- 有 `doctype`、`html`、`head`、`body`、`title` 和 viewport。
- 移动端布局可用，图片不溢出，宽表格可横向滚动。
- loading、empty、error、ready 等状态与页面功能匹配。
- 资源已按 [`resource-normalization.md`](resource-normalization.md) 内联、上传或改写；运行 `python3 page/lint_page_resources.py <final.html>` 无 error。
- 单 HTML 内包含页面需要的 CSS 和 JS，文件不超过独立预览页的 2 MiB 上限。

### 动态页

- 使用 [`database/database-sdk-contract.md`](database/database-sdk-contract.md)，参数和返回结构符合 [`database/database-sdk-schema.md`](database/database-sdk-schema.md)。
- 新页面从 `window.__SPACE_PAGE__.database` 取得 SDK，并定义真实字面 `DATABASE_ID`。
- 运行时先用 `db.getSchema({ database_id: DATABASE_ID })` 取得真实字段。
- 查询使用 `cursor`、`page_size`、`next_cursor`、`has_more`，记录读取使用 `record_id` 和 `fields`。
- 新增使用 `addRecord({ database_id, record })`；更新和删除使用 `record_id`。
- 图片直接调用 `uploadImage({ file })`；`onUpdated` 只处理当前 iframe 自己成功完成的写操作。
- SDK 与 Agent CLI 都使用 snake_case，但分别属于浏览器方法调用和构建期 Gateway 命令，不能互相替代。
- 运行 `python3 page/lint_database_sdk_usage.py <final.html> [--schema <schema.json>]` 无 error。
- 重新分析 final HTML，完整 `sdk.database_ids` 与 [`page-database-relation.md`](page-database-relation.md) 的关系设计一致。

### 修复页

- 按 [`repair-guide.md`](repair-guide.md) 先实际操作主要任务路径，再优化交互反馈和视觉样式；
- SDK 及其成功返回的数据无条件可信，不增加 mock、fallback、数据纠错或重复查询；
- 键盘、触控、焦点、disabled/submitting、弹层、滚动与响应式交互均已检查；
- 桌面、平板和移动窄屏没有因修复产生新的视觉退化；
- 原 node ID、Space ID、路径、父目录、未要求变更的 Database ID 和已有健康功能均已保留。

## 6. 清理

发布并取得 URL 后，只删除下列本地临时产物；不得删除远端工程目录及其中 HTML、Markdown 节点，也不得删除页面关联的 Database：

- 生成的 HTML；
- ZIP 解压文件；
- 资源内联和转换产物；
- 临时 ZIP。

Space 下载文件和 presign 响应只能位于 `/tmp/.moma-tmp/`。清理它们前必须校验每个目标路径以 `/tmp/.moma-tmp/` 开头且文件确由本轮下载或生成；任一条件不满足则停止删除。

## 7. 回执

```text
页面已发布：<publishUrl>
```
