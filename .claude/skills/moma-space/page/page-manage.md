# web 节点定位、上传与发布

本流程中的已明确 API 直接调用；写操作首次调用即携带 `--yes`。

页面最终是 Space 中工程目录内的单 HTML `kind=web` 节点。新页面必须先创建远端工程目录，再把 HTML 与 Markdown 放入其中；页面依赖的 Database 创建时在 `schema` 中传 `"parent_id":"<project_folder_id>"` 归入工程目录，并保存响应中的真实 `database_id` 和 `database_name`，运行期仍通过 `database_id` 与工程建立逻辑关联。已有页复用当前父目录并直接更新原路径。两者都调用 publish-page 并返回发布 URL。

## 1. 解析 Space

新页面生成、导入、克隆或从素材转页时，无论用户是否给出 Space ID 或标题，都必须调用以下固定 API；这是新页面目标 Space 的唯一来源：

```bash
moma moma-space api GET_api_v1_tools_storage_space_list-user-spaces \
  --query 'pageQuery={"page_no":1,"page_size":100}' --json
```

从响应中的 space 列表按返回顺序解析：用户指定 ID 时，只在返回项的真实 ID 中精确匹配；用户指定标题时按标题精确匹配，唯一匹配后取该项真实 ID；用户未指定时，过滤 `mode == "team"` 并取第一项。同标题多项、指定项不存在或不可见、无 team space 时停止并报告，不询问。不得直接信任或构造外部 ID，后续 `space_id` / `space_root` 必须使用选中返回项的真实 ID。

已有页面编辑不走上述默认选择：从 `node-info` 或 `files_query` 的节点结果读取并沿用页面 `spaceId`。

## 2. 建立或确定工程目录

### 新页面

第一项持久化操作必须创建远端工程目录：

```bash
moma moma-space api POST_api_v1_tools_storage_file_create-folder \
  --data '{"space_id":"sp_abc123","title":"记账本"}' \
  --yes \
  --json
```

目标父目录和名称明确后直接执行上例；写调用首次携带 `--yes`。用户指定已有父目录时，在 body 中额外传其 `parent_id`。保存响应的 `id` 为 `<project_folder_id>`，并保存工程目录相对路径；后续 HTML 传该 `parent_id`，Markdown 的 `filepath` 以该路径为前缀。新建或克隆 Database 时在 `schema` 中传 `"parent_id":"<project_folder_id>"`，使其落在工程目录内；保存返回的 `database_id` 并关联到最终 HTML。

只有用户明确指定已有工程目录时才复用。新页面名称冲突时自动追加中文序号等后缀生成不冲突名称，不询问用户，不静默覆盖或复用已有目录。工程目录名、HTML 文件名、Markdown 文件名、Database 名称必须使用中文。本地临时 HTML 文件的 basename 会成为 `upload-node` 上传后的 web 节点标题，因此临时文件也必须用中文 `<page-slug>.html` 命名（如 `/tmp/.moma-tmp/记账本.html`），不得用英文 slug；创建 Database 后，以响应中的 `database_name` 作为真实 Database 名。新页面不得省略 HTML 的 `parent_id` 而上传到 Space 根目录。Database 也应归入工程目录（创建时传 `parent_id`）；按用户意图可以复用已有 Database（不新建），或创建带 `parent_id` 的项目专用副本。

### 已有页面

通过 node-info 或 files_query 取得页面当前 `parent_id`，复用该父目录作为 `<project_folder_id>`；不新建目录、不迁移页面。后续新增 Markdown 必须位于该目录；新增 Database 时传 `"parent_id":"<project_folder_id>"`，使其落在该工程目录内。

## 3. 定位节点

已知 node ID：

```bash
moma moma-space api POST_api_v1_tools_storage_file_node-info \
  --data '{"node_id":"file_abc123"}' \
  --json
```

只有路径时：

```bash
moma moma-space api GET_api_v1_tools_files_query \
  --query 'space_root=sp_abc123&path=<current-relative-path>' \
  --json
```

下载已有 HTML：先用上方 `GET_api_v1_tools_files_query` 验证 `exists=true`、`type=file`、`readable=true`，再取得 presigned URL。响应和文件只能保存在 `/tmp/.moma-tmp/`；不得输出完整 URL。

```bash
mkdir -p /tmp/.moma-tmp
moma moma-space api POST_api_v1_tools_file_presigned_url \
  --data '{"space_root":"sp_abc123","filepath":"<current-relative-path>","task_id":"page-task-001"}' \
  --json > /tmp/.moma-tmp/page-task-001-presign.json
URL=$(python3 -c "import json; print(json.load(open('/tmp/.moma-tmp/page-task-001-presign.json'))['url'])")
curl -sSfL -o /tmp/.moma-tmp/page-task-001-demo.html "$URL"
```

处理完成后，只在校验目标路径以 `/tmp/.moma-tmp/` 开头且文件确由本轮下载或生成后，删除下载文件和 presign 响应；任一条件不满足则停止删除。

## 4. 工程内 Markdown

需要持久化需求、内容母本、说明或其他 Markdown 时，`write_file` 不传 `parent_id`，而是把工程目录相对路径写入 `filepath`：

```bash
moma moma-space api POST_api_v1_tools_write_file \
  --data '{"space_root":"sp_abc123","filepath":"<project_folder_relative_path>/README.md","task_id":"page-task-001","content":"<Markdown 内容>"}' \
  --yes \
  --json
```

该写入直接执行，首次调用携带 `--yes`。禁止使用无工程目录前缀的根级 Markdown 路径。

## 5. 上传前检查

1. `analyze_page.py` 验证 final 页面模式和 Database ID 集；
2. `lint_page_resources.py` 无 error；
3. 动态页 `lint_database_sdk_usage.py` 无 error；
4. HTML 不超过 2 MiB。

## 6. 新页面上传

`POST_api_v1_tools_storage_file_upload-node`（`multipart/form-data`）把单个 `.md` / `.html` 上传为 web 节点：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `space_id` | form string | 页面流程必填 | 目标空间；必须是固定 API 选中返回项的真实 ID，不得省略 |
| `parent_id` | form string | 新页面必填 | 新页面工程目录节点 ID，不得省略 |
| `file` | file | 是 | 仅支持 `.md`、`.html`，忽略扩展名大小写；同名文件按现有上传链路覆盖 |

`--file` 必须用 `field=path` 格式，字段名固定为 `file`：

```bash
moma moma-space api POST_api_v1_tools_storage_file_upload-node \
  --data '{"space_id":"sp_abc123","parent_id":"<project_folder_id>"}' \
  --file 'file=<temporary-workdir>/记账本.html' \
  --yes \
  --json
```

新页面的 `parent_id` 必须是本工程目录 ID。`upload-node` 以 `--file` 指定文件的 basename 作为上传后 web 节点的标题（即 Space 中可见的文件名），因此临时 HTML 必须用中文 `<page-slug>.html` 命名（如 `/tmp/.moma-tmp/记账本.html`），不得用英文 slug 导致节点标题变英文。返回上传后的 `AppNodeVO`，其 `nodes` 为空数组；从响应根字段读取 `id` 作为 web node ID，用于下一步发布。

## 7. 已有页面更新

直接覆盖原路径：

```bash
moma moma-space api POST_api_v1_tools_write_file \
  --data '{"space_root":"sp_abc123","filepath":"<current-relative-path>","task_id":"page-task-001","content":"<完整新 HTML>"}' \
  --yes \
  --json
```

后续仍使用原 node ID 发布。

## 8. 关系登记与发布 Page

上传取得 node ID 或更新原节点后，按 [`page-database-relation.md`](page-database-relation.md) 处理 final ID 集。只有当前服务注册正式关系 API 时登记；父子节点层级不能替代关系。

```bash
moma moma-space api POST_api_v1_tools_storage_file_publish-page \
  --data '{"node_id":"file_abc123"}' \
  --yes \
  --json
```

当前后端直接返回发布 URL；Gateway 也可能放在 `data` 中。最终回复使用本次响应的 URL，不使用 node ID、Space 路径或编辑地址替代。

## 9. 清理

取得发布 URL 后只删除本次本地临时 HTML、下载、解压和转换产物。远端工程目录及其中 HTML、Markdown 节点，以及页面关联的 Database，都是工程产物，必须保留。
