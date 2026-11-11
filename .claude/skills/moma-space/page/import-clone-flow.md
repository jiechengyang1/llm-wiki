# HTML/ZIP 导入与页面克隆流程

本流程中的已明确 API 直接调用；写操作首次调用即携带 `--yes`。

用于本地 HTML、ZIP、指定 URL 或 Space 页面。将来源转换为单 HTML，上传新节点，发布并返回新 URL。

## 1. 准备目标并创建工程目录

导入或克隆生成新页面前，先按 [`entry.md`](entry.md) 调用固定 `GET_api_v1_tools_storage_space_list-user-spaces` API 解析目标 Space；即使用户指定 ID 或标题也必须从返回的 space 列表匹配出真实 ID，未指定时取返回顺序中第一个 `mode == "team"` 的 space。同标题多项、指定项不存在或不可见、无 team space 时停止并报告，不询问。后续 `space_id` / `space_root` 只使用选中返回项的真实 ID。

如果任务实际是编辑已有页面，则进入 [`edit-flow.md`](edit-flow.md)，沿用 `node-info` 或 `files_query` 节点结果中的 `spaceId`，不重新选择目标 Space。

解析目标 Space 并确定新文件名后，新页面工作必须先直接创建远端工程目录：

```bash
moma moma-space api POST_api_v1_tools_storage_file_create-folder \
  --data '{"space_id":"<target_space_id>","title":"项目复盘"}' \
  --yes \
  --json
```

从响应读取文件夹 ID，后续统一记为 `<project_folder_id>`，并记录工程目录相对路径 `<project_folder_relative_path>`。持久化 HTML 必须显式使用 `"parent_id":"<project_folder_id>"`；持久化 Markdown 的 `write_file` 不使用 `parent_id`，其 `filepath` 必须以 `<project_folder_relative_path>/` 为前缀。克隆或新建 Database 时在 `schema` 中传 `"parent_id":"<project_folder_id>"`，使其落在工程目录内，再保存返回的 `database_id` 并关联到最终 HTML。HTML 和 Markdown 均不得写入 Space 根目录。使用临时目录存放下载、解压、转换和最终 HTML。

## 2. 分析和转换来源

先执行 [`html-analysis.md`](html-analysis.md)，输出 canonical analysis、资源清单和完整 `sdk.database_ids`。所有来源资源按 [`resource-normalization.md`](resource-normalization.md) 处理。

### 本地 HTML

复制到临时目录，解析所引用的 CSS、JS 和图片，把发布需要的资源内联到单个中文命名 `<new-slug>.html`（如「项目复盘.html」）。

### 本地 ZIP

解压到临时目录，定位 HTML 入口，把相对资源内联为单 HTML。`upload-node` 接收 HTML，不直接上传 ZIP。

### Space 页面

对指定页面和每个依赖先调用 `GET_api_v1_tools_files_query` 查询精确相对路径并验证 `exists=true`、`type=file`、`readable=true`，再调用 `POST_api_v1_tools_file_presigned_url` 获取 URL。不得输出完整 URL；页面、依赖和 presign 响应只能下载到 `/tmp/.moma-tmp/`，再内联到新 HTML。

```bash
moma moma-space api GET_api_v1_tools_files_query \
  --query 'space_root=<space_id>&path=<relative-path>' \
  --json
mkdir -p /tmp/.moma-tmp
moma moma-space api POST_api_v1_tools_file_presigned_url \
  --data '{"filepath":"<relative-path>","space_root":"<space_id>","task_id":"<task_id>"}' \
  --json > /tmp/.moma-tmp/<task_id>-presign.json
URL=$(python3 -c "import json; print(json.load(open('/tmp/.moma-tmp/<task_id>-presign.json'))['url'])")
curl -sSfL -o /tmp/.moma-tmp/<task_id>-source "$URL"
```

处理完成后，只在校验每个目标路径以 `/tmp/.moma-tmp/` 开头且文件确由本轮下载或生成后，删除下载文件和 presign 响应；任一条件不满足则停止删除。

### URL 页面

下载指定页面及其实际引用的页面资源，转换为单 HTML。

## 3. 克隆动态页数据

用 `analyze_page.py` 提取 SDK 使用的全部字面 Database ID，包括常量和对象中的 `database_id`。不能只处理第一个 ID：

- **项目专用副本（默认）**：Agent 通过 CLI 读取源 schema 和记录，在目标 Space 创建带 `"parent_id":"<project_folder_id>"` 的新 Database（落在工程目录内），分页复制记录，再把 HTML 中的旧 ID 替换为新 ID。
- **共享原数据**：用户明确需要复用同一数据源且权限允许时，保留原 Database ID。
- **静态快照**：将当前数据固化到 HTML，移除 Database SDK 调用。

新建 Database 时应在 `schema` 中传 `"parent_id":"<project_folder_id>"`，使其落在工程目录内；项目关联以最终 HTML 中的真实 Database ID 集为准。

独立复制时，对每个源 ID：

1. `POST_api_v1_tools_storage_table_get-database-schema` 读取源 schema；
2. `POST_api_v1_tools_storage_table_create-database` 以 `"space_id":"<target_space_id>"` 创建对应目标 Database；`schema` 传 `"parent_id":"<project_folder_id>"`，使其落在工程目录内；
3. `POST_api_v1_tools_storage_table_query-database-records` 分页读取源记录，Agent CLI 的 `page_size <= 100`；
4. `POST_api_v1_tools_storage_table_batch-add-records` 分批复制记录；
5. 建立完整 `old_id → new_id` JSON mapping；
6. 执行 `python3 page/remap_database_ids.py --html <final.html> --mapping @<mapping.json>`；工具按 ID 边界进行非链式替换，并验证旧 ID 残留和替换计数；
7. 最终 HTML 按当前合同重建，只使用 `window.__SPACE_PAGE__.database`；再次分析并运行 SDK lint。

运行时实现见 [`database/database-sdk-contract.md`](database/database-sdk-contract.md)。不要把 SDK 页面改写成 HTTP 请求页面。

## 4. import_html.py 的取舍

Library 的 `page/import_html.py` 使用另一套 Page 服务协议及私有依赖。本 Skill 不调用它，统一执行：

```text
转换为单 HTML
→ POST_api_v1_tools_storage_file_upload-node
→ POST_api_v1_tools_storage_file_publish-page
```

## 5. 上传并发布

```bash
moma moma-space api POST_api_v1_tools_storage_file_upload-node \
  --data '{"space_id":"<target_space_id>","parent_id":"<project_folder_id>"}' \
  --file 'file=<temporary-workdir>/项目复盘.html' \
  --yes \
  --json
```

`--file` 必须用 `file=<path>` 格式；`space_id` 实测必填。返回 `AppNodeVO`，`nodes` 为空数组，从根字段读取 `id`。

`parent_id` 必填且必须为本次创建的 `<project_folder_id>`。读取新 web node ID 后，按 [`page-database-relation.md`](page-database-relation.md) 处理目标 ID 集；只有存在正式 API 时登记关系。验证 SDK/resource lint 无 error 后发布：

```bash
moma moma-space api POST_api_v1_tools_storage_file_publish-page \
  --data '{"node_id":"<new_web_node_id>"}' \
  --yes \
  --json
```

## 6. 清理与交付

取得 publish URL 后删除工作副本、下载、ZIP 解压目录和转换产物，回复：

```text
页面已导入并发布：<publishUrl>
```
