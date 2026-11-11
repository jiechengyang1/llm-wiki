# 素材与 Space 节点转页面流程

本流程中的已明确 API 直接调用；写操作首次调用即携带 `--yes`。

用于文档、表格、图片、URL、Database 节点、已有 web 节点和混合素材。宿主负责读取文件或多模态内容，本 Skill 负责提取母本、选择页面形态、生成并发布。

## 1. 建立工程目录并路由来源

先判断任务是否为已有 web/HTML 节点的原页修改。原页修改直接进入 [`edit-flow.md`](edit-flow.md)，沿用 `node-info` 或 `files_query` 节点结果中的 `spaceId` 并复用原页当前父文件夹，不重新选择目标 Space，不创建新文件夹、不迁移原页。

其他需要生成新页面的任务，先按 [`entry.md`](entry.md) 调用固定 `GET_api_v1_tools_storage_space_list-user-spaces` API 解析目标 Space；即使用户指定 ID 或标题也必须从返回的 space 列表匹配出真实 ID，未指定时取返回顺序中第一个 `mode == "team"` 的 space。同标题多项、指定项不存在或不可见、无 team space 时停止并报告，不询问。后续 `space_id` / `space_root` 只使用选中返回项的真实 ID。

解析目标 Space 后，必须在读取、转换和生成持久化产物前先创建远端工程目录：

```bash
moma moma-space api POST_api_v1_tools_storage_file_create-folder \
  --data '{"space_id":"<space_id>","title":"汇报材料"}' \
  --yes \
  --json
```

从响应读取文件夹 ID，后续统一记为 `<project_folder_id>`，并记录工程目录相对路径 `<project_folder_relative_path>`。持久化 HTML 必须显式使用 `"parent_id":"<project_folder_id>"`；持久化 Markdown 的 `write_file` 不使用 `parent_id`，其 `filepath` 必须以 `<project_folder_relative_path>/` 为前缀。新建或克隆 Database 时在 `schema` 中传 `"parent_id":"<project_folder_id>"`，使其落在工程目录内，再保存返回的 `database_id` 并关联到最终 HTML。HTML 和 Markdown 均不得写入 Space 根目录。

来源按下表路由：

| 来源 | 默认处理 |
|---|---|
| Markdown、TXT、DOC/DOCX | 提取标题/章节/表格/引用，生成静态长页 |
| PDF | 识别正文、图表、页序和结论，重组为静态页 |
| PPT/PPTX | 按演示结构生成滚动叙事或静态汇报页；不假设私有播放器 |
| CSV、XLS/XLSX | 一次性展示用静态快照；持续查询用 readonly；记录维护用 readwrite |
| 图片/设计稿 | 视觉理解后生成语义化、响应式 HTML，不只把图片铺满页面 |
| URL | 读取内容和实际依赖，按导入或内容重建设计 |
| Space 文档节点 | 用已注册文件读取 API 取得内容，按文档处理 |
| Space Database 节点 | 默认 readonly；用户要求维护记录时 readwrite |
| Space web/HTML 节点 | 修改原页走 edit；复制新页走 import/clone |
| 多素材包 | 提取共同主题、去重，融合成单一内容母本 |

## 2. 内容提取

形成结构化母本：

```text
title
summary / key message
sections[]
tables / metrics
images and captions
quotes / sources
actions
```

不得简单按文件顺序拼接。冲突数据保留来源说明；无法核实的数据不自行补造。

## 3. 页面分析与形态

把用户意图和提取内容交给 [`html-analysis.md`](html-analysis.md)：

- 报告、说明、专题 → static；
- 会持续变化但页面只消费数据 → database-readonly；
- 页面负责表单和记录维护 → database-readwrite。

表格来源不等于必须建 Database；维护意图才决定 readwrite。

## 4. Database 来源

Database 节点先通过 Agent CLI 获取真实 schema 和数据。生成新页面时，可按用户的数据共享意图复用来源 `database_id`（不新建）、在目标 Space 创建带 `"parent_id":"<project_folder_id>"` 的项目专用副本（落在工程目录内），或改为静态快照：

- 页面 runtime 只使用 `window.__SPACE_PAGE__.database`；
- 字段名取真实 `Property.name`；
- readonly 页不生成写操作；
- readwrite 只使用当前文档已验证的字段写入结构；
- 大量数据通过 runtime 分页读取，不把全部记录内联进 HTML。

## 5. 生成与资源

静态页加载 [`static-page-flow.md`](static-page-flow.md)，动态页加载 [`data-page-flow.md`](data-page-flow.md)，视觉编排加载 [`beautify-flow.md`](beautify-flow.md)。所有图片、脚本和字体按 [`resource-normalization.md`](resource-normalization.md) 处理。

## 6. 统一终态

```text
新页面：创建远端工程目录并取得 <project_folder_id>
已有页编辑：取得并复用原始 <project_folder_id>
→ 读取素材/节点
→ 提取内容母本
→ 页面分析和路由
→ 生成 HTML
→ SDK/resource lint
→ 新页面以 parent_id=<project_folder_id> upload-node；已有页 write_file 保持原路径
→ publish-page
→ 获得 publish URL
→ 清理读取、转换、分析和上传前产物
→ 返回 publish URL
```
