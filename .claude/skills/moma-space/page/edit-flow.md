# 已有页面编辑与重新发布流程

本流程中的已明确 API 直接调用；写操作首次调用即携带 `--yes`。

目标是修改已有 HTML web 节点，保持原 node ID，重新发布并返回本次发布 URL。

## 1. 定位并读取节点

已知 node ID：

```bash
moma moma-space api POST_api_v1_tools_storage_file_node-info \
  --data '{"node_id":"<node_id>"}' \
  --json
```

取得节点的 `spaceId`、路径、文件名、`kind` 和原始 `parent_id`，把原始 `parent_id` 统一记为 `<project_folder_id>`，并从当前相对路径记录父文件夹相对路径 `<project_folder_relative_path>`。核对两者都指向原页面当前所在文件夹；编辑流程不得新建工程目录、迁移原页面或改用其他父级。只有路径或发布 URL 时，先通过文件查询找到 web 节点，再调用 `POST_api_v1_tools_storage_file_node-info` 取得并复用其 `parent_id`。无法取得有效原始 `parent_id` 或父文件夹相对路径时停止，不得自行回退到根目录或其他目录。

下载现有 HTML：先查询精确相对路径并验证 `exists=true`、`type=file`、`readable=true`，再取得 presigned URL。响应和文件只能保存在 `/tmp/.moma-tmp/`；不得输出完整 URL。

```bash
moma moma-space api GET_api_v1_tools_files_query \
  --query 'space_root=<space_id>&path=<current-relative-path>' \
  --json
mkdir -p /tmp/.moma-tmp
moma moma-space api POST_api_v1_tools_file_presigned_url \
  --data '{"filepath":"<current-relative-path>","space_root":"<space_id>","task_id":"<task_id>"}' \
  --json > /tmp/.moma-tmp/<task_id>-presign.json
URL=$(python3 -c "import json; print(json.load(open('/tmp/.moma-tmp/<task_id>-presign.json'))['url'])")
curl -sSfL -o /tmp/.moma-tmp/<task_id>-source.html "$URL"
```

远端内容是本次编辑基线。先对下载文件运行 `analyze_page.py`，记录 original Database ID 集、页面模式和资源清单。处理完成后，先校验路径以 `/tmp/.moma-tmp/` 开头且文件确由本轮下载或生成，再删除下载文件和 presign 响应；任一条件不满足则停止删除。

## 2. 修改临时副本

1. 在临时目录创建与原文件同名的 HTML。
2. 功能、交互或视觉修复必须加载 [`repair-guide.md`](repair-guide.md)，先恢复核心交互，再优化交互反馈和视觉样式；保留已有健康功能、内容语义与数据关系。
3. 按用户要求修改内容，并按 [`resource-normalization.md`](resource-normalization.md) 内联、上传和改写 CSS、JS、图片及字体。
4. 动态页按 [`database/database-sdk-contract.md`](database/database-sdk-contract.md) 和 [`database/database-sdk-schema.md`](database/database-sdk-schema.md) 使用 `window.__SPACE_PAGE__.database`。修复场景无条件信任 SDK 及其成功返回的数据，保留正常 SDK 与数据代码；只有页面调用违反 SDK 合同时才做最小修改。
5. SDK 参数使用 snake_case，记录读取使用 `record_id` 和 `fields`。
6. 共享原数据时保留原 Database ID；改用新数据时写入新的真实 `database_id`。本次编辑新建 Database 时，创建 schema 传 `"parent_id":"<project_folder_id>"`，使其落在工程目录内；保存返回的 `database_id` 并写入最终 HTML。
7. 本次编辑如新建持久化 Markdown，`write_file` 不使用 `parent_id`；其 `filepath` 必须以 `<project_folder_relative_path>/` 为前缀，放在原页面当前父文件夹，不得改用其他目录。
8. 按 [`artifact-contract.md`](artifact-contract.md) 完成页面结构和状态。
9. 对 final HTML 再运行分析；动态页执行 SDK lint，所有页面执行资源 lint。
10. 比较 original/final ID 集，按 [`page-database-relation.md`](page-database-relation.md) 生成 added/removed；仅在当前服务有正式 API 时同步元数据。

## 3. 更新原节点

直接覆盖原路径：

```bash
moma moma-space api POST_api_v1_tools_write_file \
  --data '{"space_root":"<original_space_id>","filepath":"<current-relative-path>","task_id":"<task_id>","content":"<完整新 HTML>"}' \
  --yes \
  --json
```

沿用原 node ID 发布。

## 4. 重新发布

```bash
moma moma-space api POST_api_v1_tools_storage_file_publish-page \
  --data '{"node_id":"<original_node_id>"}' \
  --yes \
  --json
```

以本次响应的 publish URL 为准。

## 5. 清理与回复

删除本次临时 HTML、下载和转换产物，回复：

```text
页面已更新并发布：<publishUrl>
```
