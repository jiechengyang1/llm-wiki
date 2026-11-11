# 静态展示页流程

本流程中的已明确 API 直接调用；写操作首次调用即携带 `--yes`。

用于汇报、报告、专题、叙事和一次性数据展示。最终交付发布 URL。

## 1. 定位目标并创建工程目录

静态新页面无论用户是否给出 Space ID 或标题，都必须调用以下固定 API；这是目标 Space 的唯一来源：

```bash
moma moma-space api GET_api_v1_tools_storage_space_list-user-spaces \
  --query 'pageQuery={"page_no":1,"page_size":100}' --json
```

从响应中的 space 列表按返回顺序解析：指定 ID 时只按返回项真实 ID 精确匹配；指定标题时按标题精确匹配并取唯一匹配项的真实 ID；未指定时过滤 `mode == "team"` 并取第一项。同标题多项、指定项不存在或不可见、无 team space 时停止并报告，不询问。不得直接信任或构造外部 ID，后续 `space_id` / `space_root` 只使用选中返回项的真实 ID。

新页面工作解析出目标 Space 后，必须先直接创建远端工程目录：

```bash
moma moma-space api POST_api_v1_tools_storage_file_create-folder \
  --data '{"space_id":"<space_id>","title":"季度复盘"}' \
  --yes \
  --json
```

从响应读取文件夹 ID，后续统一记为 `<project_folder_id>`，并记录工程目录相对路径 `<project_folder_relative_path>`。持久化 HTML 必须显式使用 `"parent_id":"<project_folder_id>"`；持久化 Markdown 的 `write_file` 不使用 `parent_id`，其 `filepath` 必须以 `<project_folder_relative_path>/` 为前缀。两者均不得写入 Space 根目录。

## 2. 分析并生成单 HTML

先按 [`html-analysis.md`](html-analysis.md) 验证 `none/weak` 证据并保持 static；表格和重复卡片本身不自动升级为 Database。在临时目录生成中文命名 `<page-slug>.html`（如「季度复盘.html」）：

- 内联必要 CSS 和 JS；
- 建立清晰的信息层级和主行动点；
- 支持移动端布局；
- 图表提供文字摘要；
- 美化编排使用 [`beautify-flow.md`](beautify-flow.md)，视觉细节参考 [`beautify/beautify-guide.md`](beautify/beautify-guide.md)；
- 资源遵循 [`resource-normalization.md`](resource-normalization.md)；
- 产物遵循 [`artifact-contract.md`](artifact-contract.md)，上传前执行 `lint_page_resources.py`。

## 3. 上传 web 节点

```bash
moma moma-space api POST_api_v1_tools_storage_file_upload-node \
  --data '{"space_id":"<space_id>","parent_id":"<project_folder_id>"}' \
  --file 'file=<temporary-workdir>/季度复盘.html' \
  --yes \
  --json
```

`--file` 必须用 `file=<path>` 格式。新页面的 `parent_id` 必填且必须为本次创建的 `<project_folder_id>`；页面流程的 `space_id` 必填，必须为固定 API 选中返回项的真实 ID，不得省略。返回 `AppNodeVO`，`nodes` 为空数组，从根字段读取 `id` 作为 web node ID。

## 4. 发布

```bash
moma moma-space api POST_api_v1_tools_storage_file_publish-page \
  --data '{"node_id":"<uploaded_node_id>"}' \
  --yes \
  --json
```

解析本次 publish URL。

## 5. 清理并交付

删除临时 HTML 和转换产物，回复：

```text
页面已发布：<publishUrl>
```
