---
name: moma-space
version: 1.1.5
description: "操作远端 MOMA Space，或在 Space 中生成、导入、克隆、编辑并发布静态 HTML / Database 动态页面时使用。典型触发包括 `@/kespace/<space_title_or_id>/<relative_path>`、`moma-space`，或同时出现明确要求在某个 MOMA Space（给出 Space ID/标题/元数据）中搜索、总结、读取、查找或操作内容时，立即使用本 Skill。通过 `moma moma-space api <apiName>` 调用完整 Gateway API 名，字段名只用 API 属性名。"
metadata:
  requires:
    bins: ["moma"]
  cliHelp: "moma --help"
---

# MOMA Space（moma-space）

**CRITICAL — 本 Skill 的 `<service>` 固定为 `moma-space`。所有命令必须使用 `moma moma-space ...`。**
**CRITICAL — 使用 `moma` CLI；不要用经典 Go `kespace`/`ks` CLI。**
**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../moma-shared/SKILL.md`](../moma-shared/SKILL.md)，其中包含登录、权限处理、更新和安全规则。**
**CRITICAL — 本业务 Skill 通常不得放宽 `moma-shared` 规则，但 `page/entry.md` 路由的已明确页面生命周期 API 有明确窄范围例外；登录、权限、敏感信息、未知 API/参数和安全临时目录规则始终不变。**
**CRITICAL — `moma moma-space ...` 必须作为宿主命令工具的顶层进程执行；禁止通过远端 `execute_*`、Python/Node subprocess、`os.system`、`sh -c` 或 `shell=true` 包装，以保留命令轨迹、stdout、stderr 和退出码。**
**CRITICAL — 只用 API 字段名（`expected_mtime`、`cached_mtime`、`cell_range`、`exec_intent` 等）；不要用旧 flag（`--mtime` / `--intent` / `--range`）。**
**CRITICAL — 下方决策树里的 `kb-search_files` / `wiki_search` / `list_spaces` 等是动作名；真正调用时 apiName 必须用「命令」表里的完整名（如 `POST_api_v1_tools_kb-search_files`）。禁止短名，禁止自拼 `*_spaces_read_*` / `*_spaces_search_*`。当前任务首次调用本 service 前按 `moma-shared` 执行一次 `list` 核对 API 名单；此后本表已写清参数时直接 `api`，参数或响应不明确时才用 `schema`。**

## 首轮路由（最高优先级）

- **远端 MOMA Space：** 当引用以 `@/kespace/` 开头、上下文同时给出明确 Space ID/type 与 Space `path`，或用户要求在 MOMA Space 中生成、导入、克隆、编辑、发布静态 HTML / Database 动态页面时，加载本 Skill。即使上游提示仍写着“使用 kespace cli”，也必须改用 `moma moma-space api ...`。
- **本地文件：** `@cli.py`、`@src/cli.py`、`@./...`、`@/Users/...` 等不含 `/kespace/` 关键字的引用，一律留给宿主本地 Read/Glob 等工具；不得调用 MOMA Space。
- **远端文件/文件夹的引用文本规则解析：** `@/kespace/<space_title_or_id>/<relative_path>` 中，`<space_title_or_id>`是空间标题或 ID，`<relative_path>`是相对路径。注意保留中文与空格，去掉引用边界处的零宽字符；JSON body 必须作为一个完整参数传入，不能按空格拆路径。
- **远端文件/文件夹的引用元数据：** 关注`@`的引用内容是否已有对应的元数据信息(metadata)，如：`{"referred_to_as":"...", "metadata":{...}}`，避免额外的请求/问询/检索。
- **定位空间：** 请使用空间 ID（space id）。新页面生成、导入、克隆或从素材转页时，无论用户是否指定 Space ID/标题，都必须按 [`list_user_spaces`](references/moma-space-list_user_spaces.md) 调用固定 `GET_api_v1_tools_storage_space_list-user-spaces`（必填 query `pageQuery`）；指定 ID 仅按返回项真实 ID 精确匹配，指定标题按标题精确匹配并取真实 ID，未指定则按返回顺序取第一个 `mode == "team"` 的 space，不询问。同标题多项、指定项不存在或不可见、无 team space 时停止并报告。后续 `space_id` / `space_root` 只用选中返回项真实 ID，不得直接信任或构造外部 ID。已有页面编辑沿用 `node-info` / `files_query` 节点返回的 `spaceId`，不重新默认选择。非页面场景按 [`list_spaces`](references/moma-space-list_spaces.md) 处理。
- **定位文件/文件夹：** 当没有现成的元数据信息，需要基于文件/文件夹的路径取得 `file_id` / `folder_id`时，使用`GET_api_v1_tools_files_query`。`FILE_NOT_FOUND` 时跟 `did_you_mean` / `hint`，不得自行改写路径中间内容。
- **task_id 分流：**
   - prompt 已给服务端 mint 的 `task_id`：全轮原样复用，禁止另造。
   - 当只有文本路径或 `Space ID + path`、未给 `task_id`：生成一个短 task id 并在本轮复用。
- **认证分流：** 未登录时停止业务调用并提示用户先完成登录，不得索要 API Key、不得要求终端执行 `moma login`、不得回退本地工具及旧 `kespace` / `ks` CLI。

## 快速决策

- 生成 / 导入 / 克隆 / 编辑 / 发布 Space 页面 → 先读 [`page/entry.md`](page/entry.md)，再按其中意图路由执行
- 列出可访问空间 → [`list_spaces`](references/moma-space-list_spaces.md)
- 新建空间（团队/个人） → [`create_space`](references/moma-space-create_space.md)
- **检索**（见下方双链路决策树）：结构化主题知识 → [`wiki_search`](references/moma-space-wiki-search.md)；开放探索或需要了解 Wiki 分类目录 → [`wiki_navigate`](references/moma-space-wiki-navigate.md)；原始文件切片、精确事实和证据 → [`kb-search_files`](references/moma-space-kb-search_files.md)
- Wiki 具体主题需要正文且 Navigate/Search 摘要不足 → 对相关页面调用 [`wiki_page`](references/moma-space-wiki-page.md)；整体知识框架概览先使用 Navigate，需要核实原文时再按页面引用调用 `kb-search_files`
- 问询 / 阅读 / 总结 指定文件 → 先 [`kb-search_files`](references/moma-space-kb-search_files.md) `mode=content` + `file_id`（【搜索指定文件内容】）；该接口只返回固定上限内的相关切片，不代表文件全文。切片明显不足或确定需要完整上下文时，再定位命中切片关联的源文件 ID 及路径，用 [`file_presigned_url`](references/moma-space-file_presigned_url.md) 下载原文件精读
- 确定需要完整原文件时 → 根据切片关联的源文件 ID 定位其 Space 和相对路径，调用 [`file_presigned_url`](references/moma-space-file_presigned_url.md) 获取 presigned URL，再用 `curl` 下载并读取完整文档；下载完成后清理临时文件
- 获取供用户在 Space 前端打开文件的访问链接 → [`file_access_link`](references/moma-space-file_access_link.md)（已有文件 ID 时直接调用；只有路径时先 `files_query`）
- 修改已有文件的部分内容 → 先精读再 [`write_patch`](references/moma-space-write_patch.md)
- 新建 / 草稿 / 落库 → [`write_file`](references/moma-space-write_file.md)（草稿 `temporary:true`）
- 列目录 / 查权限 → [`files_children` / `files_query`](references/moma-space-files_children.md)
- 上传 / 删除 → [`upload_batch` / `delete_batch`](references/moma-space-upload_delete.md)
- 重命名 / 移动 → [`file_rename` / `file_move`](references/moma-space-file_rename_move.md)
- 更新 `SPACE.md` → **只**用 [`space_md_upsert`](references/moma-space-space_md_upsert.md)
- 不得不跑命令 → [`execute_command`](references/moma-space-execute.md)（`exec_intent` 只能填read）
- **写入类限制**：除 `page/entry.md` 路由命中的已明确页面生命周期 API 外，创建工程目录、持久化写/上传/删除/重命名/移动/space_md/创建空间均按下方通用协议执行；`temporary:true` 豁免。页面例外中用户已对整个页面生命周期预授权，写调用首次直接携带 `--yes`，不运行请求预演、不等待额外同意。

## MOMA Space 高风险写审批补充

以下规则是 `moma-shared` 通用协议在 MOMA Space 中的收紧；`page/entry.md` 路由命中的已明确页面生命周期 API 除外，该页面场景按本节后的窄范围例外直接执行：

1. 收到 exit `10` 或 `GATEWAY_CONFIRMATION_REQUIRED` 后，继续基于原命令执行 `--dry-run`；exit 10 本身不会生成确认卡。
2. dry-run 必须保持 API 名和所有业务参数不变；原命令有 `-o` / `--output` 时仅在预览阶段暂存移除。
3. dry-run 成功后展示目标 API、`risk`、`pathParams`、`query` 和 `body`。Moma Agent 的确认卡由这条成功的 dry-run 工具轨迹触发。
4. 只有用户针对最近一次预览明确确认后，才可恢复原 `-o` / `--output`、移除 `--dry-run` 并追加 `--yes`。无确认卡时必须语言请求确认。
5. 确认卡文案 `同意执行（--yes）` 视为明确同意；`不同意（--no）` 视为拒绝并停止。`好的`、`你弄吧`、`继续`等模糊附和不算确认。
6. 用户确认后若任何业务参数变化，原确认失效，必须重新 dry-run 和确认。不得把 `--dry-run` 与 `--yes` 同时用于真实执行。
7. 请求预演失败、风险未知或返回 `GATEWAY_INVALID_RISK` 时停止，不得追加 `--yes`。

**页面生命周期窄范围例外：** 页面生成、导入、克隆或编辑任务经 `page/entry.md` 建立具体页面上下文后，即视为用户对该页面生命周期的预授权。Database、附件、关系和发布操作必须服务于该具体页面任务；独立资源管理不适用本例外。目标、接口和业务参数已明确时直接调用；`write` / `high-risk-write` 首次调用就加 `--yes`，不运行请求预演、不展示同意预览、不等待额外同意。意外收到 exit `10` 或 `GATEWAY_CONFIRMATION_REQUIRED` 时，以相同 API 和业务参数补 `--yes` 直接重试一次。目标、接口或参数不明确时仅做必要解析或 schema discovery，不得猜测；登录、权限、敏感信息和临时目录安全边界不变。

## Space 页面应用

用户要在 MOMA Space 中生成、导入、克隆、编辑或发布页面时，必须先读 [`page/entry.md`](page/entry.md)，再按页面意图进入对应流程：

| 页面意图 | 流程 |
|---|---|
| 汇报、报告、叙事、一次性展示 | [`page/static-page-flow.md`](page/static-page-flow.md) |
| Database 看板、列表、筛选、表单、增删改 | [`page/data-page-flow.md`](page/data-page-flow.md) |
| 修复已有应用功能、交互或视觉样式 | [`page/edit-flow.md`](page/edit-flow.md) + [`page/repair-guide.md`](page/repair-guide.md) |
| 修改并重新发布已有 HTML web 节点 | [`page/edit-flow.md`](page/edit-flow.md) |
| 导入 HTML/ZIP 或克隆页面 | [`page/import-clone-flow.md`](page/import-clone-flow.md) |
| 文档、表格、图片、URL 或 Space 节点转页面 | [`page/source-to-page-flow.md`](page/source-to-page-flow.md) |

统一生命周期：**定位目标 → 建立/确定远端工程目录 → 读取与分析 → 准备数据 → 生成/导入 HTML → SDK/资源检查 → upload-node → publish-page → 清理本地临时产物 → 返回发布 URL**。上传节点不等于完成，最终交付物必须是 `publish-page` 返回的 URL。

页面执行还必须遵守以下规则：

1. Agent 构建期使用完整 Gateway API 名操作 Space、Database、文件与发布；页面运行期只使用容器注入的 `window.__SPACE_PAGE__.database`。
2. **远端工程目录是页面工程边界：** 新建、导入、克隆或从素材生成页面时，第一项持久化操作必须先调用 `POST_api_v1_tools_storage_file_create-folder` 创建工程目录；编辑已有页面时复用页面当前 `parent_id` 对应的父目录，不新建、不迁移。
3. 保存工程目录返回的 `id` 与相对路径。HTML 上传必须使用工程目录 `parent_id`，Markdown 的 `filepath` 必须以工程目录相对路径为前缀；新页面禁止把两者写到 Space 根目录。Database 创建请求应在 `schema` 中传 `"parent_id":"<project_folder_id>"`，使 Database 归入工程目录并与 HTML、Markdown 保持内聚；保存响应中的真实 `database_id` 和 `database_name`，其中 `database_name` 是真实 Database 名，最终 HTML 及页面运行期 SDK 使用 `database_id`。按用户意图可复用已有 Database（不新建），或创建项目专用副本（副本须带 `parent_id`）。工程目录名、HTML 文件名、Markdown 文件名、Database 名称必须使用中文（如「记账本/记账本.html」）。**本地临时 HTML 文件的 basename 会成为 `upload-node` 上传后的 web 节点标题（即 Space 中可见的文件名）**，因此临时文件也必须用中文 `<page-slug>.html` 命名（如 `/tmp/.moma-tmp/记账本.html`），不得用英文 slug 导致节点标题变英文。
4. 远端工程目录与本地临时工作区不同；下载、解压和转换产物仍放在受控本地临时目录，发布后只清理本地临时产物，不删除远端工程目录及其中节点。
5. 需求或来源先按 [`page/html-analysis.md`](page/html-analysis.md) 生成 canonical analysis；共同产物与发布合同见 [`page/artifact-contract.md`](page/artifact-contract.md)。
6. 动态页必须写入真实 `database_id`，并在发布前执行 `page/lint_database_sdk_usage.py`；所有页面都执行 `page/lint_page_resources.py`。
7. Page 与 Database 的运行期关系以最终 HTML 中的真实 Database ID 集为准；只有当前服务注册正式 relation API 时才同步服务端关系。
8. 页面文档中的创建工程目录、持久化写、上传、发布、附件、关系和 Database 变更适用 `page/entry.md` 的窄范围例外：用户已对整个页面生命周期预授权，目标、接口和参数明确后直接执行，写调用首次携带 `--yes`，不等待额外同意。
9. 读取已有页面时不得调用本文件禁止的 `read_file` / `read_file_raw`；按 [`file_presigned_url`](references/moma-space-file_presigned_url.md) 下载到 `/tmp/.moma-tmp/`，完成后按本文件规则清理。

页面合同索引：

- 分析结构：[`page/page-analysis-schema.md`](page/page-analysis-schema.md)、[`page/page-analysis.schema.json`](page/page-analysis.schema.json)
- 节点上传与发布：[`page/page-manage.md`](page/page-manage.md)
- 资源归一化：[`page/resource-normalization.md`](page/resource-normalization.md)
- 已有应用功能、交互与样式修复：[`page/repair-guide.md`](page/repair-guide.md)
- 构建期 Database CLI：[`page/database/page-database.md`](page/database/page-database.md)
- 页面运行期 Database SDK：[`page/database/database-sdk-contract.md`](page/database/database-sdk-contract.md)
- SDK 参数与返回 Schema：[`page/database/database-sdk-schema.md`](page/database/database-sdk-schema.md)
- Page ↔ Database：[`page/page-database-relation.md`](page/page-database-relation.md)
- 附件与图片：[`page/page-attachment.md`](page/page-attachment.md)
- 美化执行与规范：[`page/beautify-flow.md`](page/beautify-flow.md)、[`page/beautify/beautify-guide.md`](page/beautify/beautify-guide.md)

## 检索决策树

Wiki 搜索与 `kb-search_files` 切片搜索是两条独立链路：Wiki 面向归纳后的知识主题页面；`kb-search_files` 面向原始文件切片。

| 用户意图                                 | 首动作与后续配合                                                                                                                                                                                          |
|--------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 精确路径 / @文件 + 话题问答                    | 取得 `file_id`（元数据已有则直接用，否则先 `files_query`）→ `kb-search_files mode=content + file_id`；返回的是相关切片而非全文，切片明显不足或明确需要全文时再 [`file_presigned_url`](references/moma-space-file_presigned_url.md) 下载精读；不走 Wiki |
| 精确路径 / @文件夹 + 话题问答                   | `kb-search_files mode=content`，并传 `directory=/<space_title_or_id>/<folder relative_path>`；结果仅是固定数量的相关切片，不代表目录内文档全文；不走 Wiki                                                                        |
| 原文切片搜索只提供零散细节，用户需要主题框架/综述            | 可补充预梳理的wiki知识，但必须区分 Wiki 归纳与原始切片证据                                                                                                                                                                |
| 已有明确、稳定的主题关键词，询问跨文件概念、关系或详细综述          | [`wiki_search`](references/moma-space-wiki-search.md) → 选择少量候选；仅当候选摘要不足以回答时才调用 [`wiki_page`](references/moma-space-wiki-page.md) 读取所需页面正文，不要机械地先拉索引                                               |
| 询问空间整体内容、主要主题、知识框架或分类概览              | [`wiki_navigate`](references/moma-space-wiki-navigate.md) 从 `folder_id=0` 开始 Navigate；依据根概括、分类名称、页面数量和轻量页面摘要总结组织回答，必要时进一步展开分类获取更多框架结构信息，避免逐个调用读取`pages.items`的页面详情，不要把 `pages.items` 当作待逐项读取队列    |
| 开放探索、无法构造确定可靠的字面关键词                    | `wiki_navigate` 逐层了解知识框架 → 选择合适的关键词、 检索范围（Wiki `folder_id`） 传给 `wiki_search` → 分类范围 `wiki_search`；当问题需要具体页面正文且摘要不足时再调用 `wiki_page`                                                                |
| Wiki Search 命中过宽、结果分散在多个分类           | 利用命中项 `category_path/folder_id` 选择相关分类 → `wiki_search(folder_id=<ID>, include_descendants=true)` 缩小范围；不要反复猜关键词                                                                                    |
| 首次 Wiki Search 无命中且问题适合 Wiki         | 若尚未导航，先 `wiki_navigate` 一次 → 根据分类名或页面标题改写一次并在相关分类子树搜索 → 仍无命中再降级`kb-search_files`                                                                                                                  |
| 既要主题综述，又要求精确数字、条款、步骤、原话或来源证据         | `wiki_search` → `wiki_page` 建立框架 → 根据页面 `source_refs/chunk_refs` 或待核实事实调用 `kb-search_files mode=content` 调用时注意指定文件范围                                                                              |
| Wiki 未开启、Wiki 无命中或 Wiki 页面不足         | 降级 `kb-search_files mode=content`；说明降级原因，Wiki 未命中不代表原始文件没有相关内容                                                                                                                                    |
| 未指定文件，但问题要求具体数值、制度原文、操作步骤、逐字表述或可核验依据 | `kb-search_files mode=content`；只将结果视为相关切片，需要完整上下文时按切片关联的源文件 ID 定位原文件并下载精读                                                                                                                         |
| 精确路径 / @文件 + 编辑                      | [`file_presigned_url`](references/moma-space-file_presigned_url.md) 下载后本地编辑                                                                                                                       |
| 找文件名 / list files                    | `kb-search_files mode=file_name` → 确定文件后才能进一步读；不走 Wiki                                                                                                                                            |
| 浏览指定文件夹的目录结构                         | `files_children`；不走 Wiki                                                                                                                                                                          |

### Space 原始资料目录与 Wiki 分类导航的区别

| 对象 | 表示什么                                                       | 使用场景                               | 对应动作 |
|------|------------------------------------------------------------|------------------------------------|----------|
| Space 原始资料目录 | 用户上传文件和文件夹的物理存储结构，返回 `file_id/folder_id`                   | 浏览文件、定位指定目录或文件、下载/编辑原文件            | `files_children` / `files_query` |
| Wiki 分类目录 | 基于原始资料库归纳的 Wiki 页面的知识分类树，返回 Wiki `folder_id/category_path` | 理解空间 Wiki 知识主题、逐层缩小 Wiki Search 范围 | `wiki_navigate` |

二者 ID、路径和用途完全独立：禁止把 Wiki `folder_id` 传给 Space 文件接口，禁止把 Space `folder_id` 传给 Wiki Search/Navigate；Wiki 页面的 `path/slug` 也不是原始文件路径。用户说“列出某个目录里的文件”时走 Space 目录；用户说“这个空间有哪些知识分类”或要按主题分类缩小 Wiki 范围时走 Wiki 导航。

场景示例：

- “列出 `@/kespace/项目空间/制度` 下有哪些 PDF” → Space 原始资料目录：`files_query/files_children`。
- “读取报销规范.pdf 并找住宿费原文” → 原始文件定位 + `kb-search_files`，不走 Wiki 分类目录。
- “特定实体/概念的说明或综述性问题” → `wiki_navigate` 定位 Wiki `folder_id` 或 主题词query → `wiki_search`。

### 搜索双链路配合与 Token 控制规则

1. `wiki_navigate` 用于理解知识框架和分类范围；其 `index_page.summary/child_folders/pages` 是可直接用于框架概览的轻量信息。`pages.items` 表示当前分类有哪些页面，不是必须逐项调用 `wiki_page` 的任务清单。
2. `wiki_search` 用于按主题关键词定位候选页；`wiki_page` 用于读取某个确有必要的候选页正文。当具体问题需要详细内容且 Navigate/Search 的摘要不足时再读取相关页面，禁止为求“完整”而批量遍历 Wiki Page。
3. Wiki 是跨文件归纳结果，适合回答框架和关系；`kb-search_files`搜索到的是原始切片，适合事实核验和证据。回答时明确区分两者来源。
4. 组合链路默认“Wiki 建框架，切片核细节”；指定文件/目录时直接 `kb-search_files`，不先绕行 Wiki。
5. `POST_api_v1_tools_kb-search_files` 内容搜索只返回固定上限内的高相关切片：普通空间/目录搜索最多 20 条，指定 `file_id` 搜索最多 1000 条；即使有命中也不能推断已覆盖源文件全部内容。用户明确需要完整原文或切片信息明显不足时，再根据切片关联的源文件 ID 定位 Space 和相对路径，调用 `POST_api_v1_tools_file_presigned_url` 获取原文下载链接读取。
6. Wiki 当前是字面匹配而非向量语义搜索。可调整一次明显过窄的检索词；仍无命中则转`kb-search_files`，禁止原样重试。
7. 空间未开放 Wiki 能力或无权限时向用户说明 `permission_message`；不得扩大检索范围。
8. `wiki_navigate` 默认一次返回最多 50 个直属子分类和 50 个直属页面，可分别调到 100；默认只展开 1～2 层、1～2 个相关分支，不预加载完整分类树、不默认遍历全部分页。
9. `index/root` 用于根概括；目录 index 只表示当前分类的落地页，可能不存在，也不等于完整分类树。分类结构以 `wiki_navigate` 返回的 Wiki 目录为准。
10. 只有用户明确要求列出全部 Wiki 分类或页面时才遍历分页，并应分批总结；同一层已经返回的目录 index 正文通常不再读取，避免与导航页面列表内容重复。

## 硬规则

1. `space_root` / `space_id` / `space_ids` 只能用 SPACE id。新页面目标 Space 按 [`list_user_spaces`](references/moma-space-list_user_spaces.md) 固定 API 和算法解析；已有页面编辑沿用节点返回的 `spaceId`；仅非页面场景在未给出 ID 时按 [`list_spaces`](references/moma-space-list_spaces.md) 获取。
2. `kb-search_files` 使用 `space_ids`；明确指定空间内目录时额外传 `directory`；明确指定具体文件时改用 `file_id`（`list[str]`）并省略 `space_ids`。
3. `wiki_search` 必须传 `space_ids`；指定 `folder_id` 时只能传一个 Space，并用 `include_descendants` 决定是否包含后代分类。调用 `wiki_page` 时，只能使用同一 Search 命中项的 `space_id + slug`，或同一 Navigate 响应顶层的 `space_id` 与 `pages.items[]` 的 `slug`。
4. `wiki_navigate` 的 `folder_id` 是 Wiki 分类目录 ID，不是 Space 文件夹 ID；默认 `folder_limit=50/page_limit=50`，上限均为 100。Wiki 页面路径和分类路径不是 Space 文件路径，不得传给文件下载/编辑接口。
5. 其他需要 `task_id` 的文件读取/写入 API，仍按对应 reference 全轮复用 task id。
6. 话题问答有精确的引用文件：先用 `kb-search_files` + `file_id`（【搜索指定文件内容】）检索；搜不到内容时再用 `file_presigned_url` 下载精读。
7. Wiki 页面内容是归纳结果；需要进一步的精确事实或证据时，使用 `source_refs[].space_file_id` 形成 `kb-search_files` 的 `file_id` 数组检索原始文档切片。
8. `path` / `filepath` 不要前导 `/`；读返回的 `mtime` 分别用于 `cached_mtime` / `expected_mtime`。
9. `PERMISSION_DENIED` 是终局：停止并让用户找 Space 管理员/owner。仅当路径带前导 `/` 时可去掉后重试一次。
10. 当前任务首次调用本 service 的 `schema` 或 `api` 前，按 `moma-shared` 执行一次 `moma moma-space list --json` 并核对完整 apiName；reference 已给出字段且 apiName 已核对时直接 `api`，参数或响应不明确时再用 `schema`。
11. 除 `page/entry.md` 路由命中的已明确页面生命周期 API 按窄范围例外直接执行外，所有有副作用的调用遵守上方 MOMA Space 通用协议及 `moma-shared` 协议；
12. reference 已给出 apiName/字段时直接 `api`；仅 unknown api 或 reference 缺失时允许一次 `list`/`schema` 排障。
13. `cached_mtime` 只适用于完全相同的读取范围；改变 `offset/pages/sheet/cell_range/slides/paragraphs` 时不得复用。`unchanged:true` 必须复用上次结果并停止，禁止重试。
14. 下载的临时文件只允许位于 `/tmp/.moma-tmp/`，处理完成后必须立即删除；删除前须校验路径以 `/tmp/.moma-tmp/` 开头且为本轮下载文件，否则停止删除；不得长期保留或上传到其他服务。
15. `file_access_link` 的 `fileId` 使用元数据或 `files_query` 返回的文件 ID 原样传入；该接口返回供用户打开 Space 前端页面的链接。需要下载、读取或解析原文件时仍使用 `file_presigned_url`，不得混用。

| 动作                           | apiName（照抄） | 详情 |
|------------------------------|-----------------|------|
| 列空间 `list_spaces`            | 新页面生成、导入、克隆、素材转页用 `GET_api_v1_tools_storage_space_list-user-spaces`；其他场景用 `GET_api_v1_tools_spaces` | 新页面目标 Space [ref](references/moma-space-list_user_spaces.md)；其他场景 [ref](references/moma-space-list_spaces.md) |
| 创建空间 `create_space`         | `POST_api_v1_tools_storage_spaces` | [ref](references/moma-space-create_space.md) |
| 页面工程目录 `create-folder` | `POST_api_v1_tools_storage_file_create-folder` | [ref](page/page-manage.md) |
| 搜索 `kb-search_files`          | `POST_api_v1_tools_kb-search_files` | [ref](references/moma-space-kb-search_files.md) |
| Wiki 分类导航 `wiki_navigate`       | `POST_kebase_api_v1_wiki_navigate` | [ref](references/moma-space-wiki-navigate.md) |
| Wiki 实体/概念/摘要页面搜索 `wiki_search` | `POST_kebase_api_v1_wiki_search` | [ref](references/moma-space-wiki-search.md) |
| Wiki 实体/概念/摘要页面详情读取 `wiki_page`         | `POST_kebase_api_v1_wiki_page` | [ref](references/moma-space-wiki-page.md) |
| 读文件（presigned URL 下载）  | `POST_api_v1_tools_file_presigned_url` | [ref](references/moma-space-file_presigned_url.md) |
| 获取文件访问链接 `file_access_link` | `GET_api_v1_tools_file_access-link` | [ref](references/moma-space-file_access_link.md) |
| 写 `write_file`               | `POST_api_v1_tools_write_file` | [ref](references/moma-space-write_file.md) |
| 补丁 `write_patch`             | `POST_api_v1_tools_write_patch` | [ref](references/moma-space-write_patch.md) |
| 执行 `execute_command` | `POST_api_v1_tools_execute_command`  | [ref](references/moma-space-execute.md) |
| 上传 / 删除                      | `POST_api_v1_tools_upload_batch` / `POST_api_v1_tools_delete_batch` | [ref](references/moma-space-upload_delete.md) |
| 重命名 / 移动                     | `POST_api_v1_tools_file_rename` / `POST_api_v1_tools_file_move` | [ref](references/moma-space-file_rename_move.md) |
| 列目录 / 权限                     | `GET_api_v1_tools_files_children` / `GET_api_v1_tools_files_query` / `POST_api_v1_tools_files_query` | [ref](references/moma-space-files_children.md) |
| SPACE.md                     | `POST_api_v1_tools_space-md_upsert` | [ref](references/moma-space-space_md_upsert.md) |
| 创建 Database `create-database` | `POST_api_v1_tools_storage_table_create-database` | [ref](page/database/page-database.md) |
| 删除 Database `delete-database` | `POST_api_v1_tools_storage_table_delete-database` | [ref](page/database/page-database.md) |

**禁止：** `api read_file`、`api read_file_raw`、`api search_files`、`api list_spaces`、`api POST_api_v1_tools_spaces_read_file`。
**禁止：** 在 Space 下新页面生成、导入、克隆或从素材转页时用 `POST_api_v1_tools_storage_spaces` 或 `GET_api_v1_tools_spaces` 列空间；这些场景列空间只能用 `GET_api_v1_tools_storage_space_list-user-spaces`。已有页面编辑沿用节点返回的 `spaceId`；非页面场景仍按 [`list_spaces`](references/moma-space-list_spaces.md) 用 `GET_api_v1_tools_spaces`。
**禁止：** 未明确目标文件时调用 `file_presigned_url` 盲下载。

## 权限与错误处理

| code | Agent 处理                                                               |
|------|------------------------------------------------------------------------|
| `PERMISSION_DENIED` | 停止并让用户找管理员/owner；仅前导 `/` 格式问题可修正一次                                     |
| `MISSING_SCOPE_IDS` / `READ_REQUIRES_SEARCH_HIT` | 按 hint：补 `file_ids` 或先 search / `edit_intent`                          |
| `REFS_SCOPE_EMPTY` | 圈定与可读集无交集；不得去掉 ids 扩全库                                                 |
| `REFS_BINDING_EXPIRED` | 停止复用旧 `task_id`；请用户发起新一轮                                               |
| `REFS_STORE_UNAVAILABLE` | 服务暂不可用；告知用户稍后重试                                                        |
| `CONFLICT` | 重读，换新 mtime 再写                                                         |
| `PROTECTED_FILE` | 停用 write/patch 改 SPACE.md → `space_md_upsert`                          |
| `FILE_EDIT_LOCKED` | 等待/问用户，不强改                                                             |
| `FILE_NOT_FOUND` | 需核对路径                                                                  |
| `Wiki 未开启` | 改用 `kb-search_files`                                                                                                   |
| `Wiki 搜索无结果` | wiki搜索走字面匹配，先利用`wiki_navigate`获取知识目录层级确定关键字再检索，不盲猜盲试query；还搜不到改用语义检索 `kb-search_files mode=content`，Wiki 未命中不代表原始文件无内容 |
| `Wiki 页面 404` | 改用`kb-search_files`，不盲猜 slug    
| `INTERNAL_STATUS_TEXT` | 勿把工具响应当文件内容                                                            |
| `REPEATED_*_BLOCKED` | 立即停止；复用上次结果或改变查询/读取范围，禁止原样重试                                           |
| `PDF_PASSWORD_PROTECTED` / `PDF_CORRUPTED` | 停止并告知用户，不绕过或重复提取 |
| `EXEC_INTENT_MISMATCH` / `EXEC_PATHS_UNRESOLVED` | 修正 intent 或字面路径 |
| `NOT_AUTHENTICATED` / `MOMA_TOKEN_INVALID` / 凭据 missing、expired / Gateway auth failure | `@/kespace` 或 Space 元数据场景提示“第三方插件 → Space → 安装/更新授权”；停止业务调用，不要求终端登录    |
| `GATEWAY_CONFIRMATION_REQUIRED`（exit 10） | 页面生命周期按窄范围例外以相同 API 和业务参数补 `--yes` 重试一次；其他场景按本 Skill 通用协议处理 |

各 API 的响应字段与错误细则以 **references** 为准。

## 安全规则

- 不输出 Moma API Key、AccessToken、RefreshToken、完整鉴权头。
- 不手工拼鉴权头，不直打业务域名/Swagger。
- 高风险写通常不得在用户明确同意前加 `--yes`；仅 `page/entry.md` 路由命中的已明确页面生命周期 API 适用预授权例外，首次写调用直接加 `--yes`。
- 远端共享路径不得静默落到本机文件系统工具。

## References

- [Space 页面入口与意图路由](page/entry.md)
- [页面产物、发布与清理合同](page/artifact-contract.md)
- [Space 应用功能修复指南](page/repair-guide.md)
- [页面运行期 Database SDK](page/database/database-sdk-contract.md)
- [构建期 Database CLI：create-database / delete-database](page/database/page-database.md)
- [页面新建目标空间 list_user_spaces](references/moma-space-list_user_spaces.md)
- [非页面场景列出空间 list_spaces](references/moma-space-list_spaces.md)
- [创建空间 create_space](references/moma-space-create_space.md)
- [原始切片与文件名搜索 kb-search_files](references/moma-space-kb-search_files.md)（含精读时机）
- [Wiki 分类导航 wiki_navigate](references/moma-space-wiki-navigate.md)
- [Wiki 页面搜索 wiki_search](references/moma-space-wiki-search.md)
- [Wiki 页面读取 wiki_page](references/moma-space-wiki-page.md)
- [读文件 file_presigned_url](references/moma-space-file_presigned_url.md)（获取 presigned URL 后 curl 下载）
- [获取文件访问链接 file_access_link](references/moma-space-file_access_link.md)（供用户在 Space 前端打开文件）
- [写入与草稿 write_file](references/moma-space-write_file.md)
- [补丁编辑 write_patch](references/moma-space-write_patch.md)
- [执行 execute_command](references/moma-space-execute.md)
- [上传与删除 upload_batch / delete_batch](references/moma-space-upload_delete.md)
- [重命名与移动 file_rename / file_move](references/moma-space-file_rename_move.md)
- [列目录与权限 files_children / files_query](references/moma-space-files_children.md)
- [SPACE.md 更新 space_md_upsert](references/moma-space-space_md_upsert.md)
