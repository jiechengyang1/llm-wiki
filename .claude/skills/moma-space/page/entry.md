# MOMA Space 页面场景路由

命中场景后加载对应流程。

## 1. 直接执行规则

- 仅在页面生成、导入、克隆或编辑任务已通过本入口建立具体页面上下文后，将用户对整个页面生命周期的请求视为对该流程中已明确 API 的预授权，直接调用接口；Database、附件、关系和发布操作必须服务于该具体页面任务，独立资源管理不适用本规则。
- `risk: "write"` / `risk: "high-risk-write"` 的写调用第一次执行就追加 `--yes`；不执行预演、不展示请求预览，也不等待额外交互。
- 如果意外收到退出码 `10` 或 `GATEWAY_CONFIRMATION_REQUIRED`，保持相同 API 名和全部业务参数，仅补充 `--yes` 直接重试一次；不得先执行预演。重试仍失败时按实际错误停止处理，不重复调用。
- 目标、API 名或参数不明确时，只做必要的目标解析、API 列表查询或 schema discovery；这些步骤属于技术校验，不是授权流程。未知 API、未知参数或无法满足 schema 时停止，不得猜测。
- 本规则不放宽登录、权限、敏感信息、未知 API/参数、安全临时目录等边界，也不适用于未通过本入口路由的非页面任务。

## 2. 路由

1. **导入或克隆**：本地 HTML/ZIP、URL、Space 页面、复制一份 → [`import-clone-flow.md`](import-clone-flow.md)。
2. **修复已有应用**：功能异常、控件不可用、反馈不清、交互或样式退化 → [`edit-flow.md`](edit-flow.md) + [`repair-guide.md`](repair-guide.md)。
3. **编辑已有页**：指定已有 web node、Space HTML 或发布页并要求修改 → [`edit-flow.md`](edit-flow.md)。
4. **素材/节点转页面**：文档、PDF、PPT、表格、图片、URL、Space doc/Database/web 节点 → [`source-to-page-flow.md`](source-to-page-flow.md)。
5. **Database 动态页**：持续数据、筛选、排序、分页、看板、表单、记录增删改 → [`data-page-flow.md`](data-page-flow.md)。
6. **静态展示页**：汇报、报告、总结、专题、叙事和一次性展示 → [`static-page-flow.md`](static-page-flow.md)。

需求或来源先按 [`html-analysis.md`](html-analysis.md) 分析：`none/weak` 默认 static，持续查询为 database-readonly，持久化和记录维护为 database-readwrite。

## 3. 目标与工程目录解析

- **新页面目标 Space 的唯一来源：** 新页面生成、导入、克隆或从素材转页时，无论用户是否给出 Space ID 或标题，都必须先调用以下固定 API；不得直接信任外部 ID、把标题当 ID，或自行构造 ID。

```bash
moma moma-space api GET_api_v1_tools_storage_space_list-user-spaces \
  --query 'pageQuery={"page_no":1,"page_size":100}' --json
```

- 从响应中的 space 列表按返回顺序解析：
  1. 用户指定 Space ID：仅在返回项的真实 ID 中精确匹配，并取该返回项的真实 ID；指定项不存在或当前账号不可见时停止并报告。
  2. 用户指定 Space 标题：按标题精确匹配；唯一匹配时取该返回项的真实 ID，同标题多项时停止并报告，不询问；无匹配时停止并报告指定项不存在或当前账号不可见。
  3. 用户未指定 Space：过滤 `mode == "team"` 的返回项并取第一项；没有 team space 时停止并报告，不询问。
- 选中后，所有后续 `space_id` / `space_root` 必须使用该返回项的真实 ID。
- **已有页面编辑例外：** 从 `node-info` 或 `files_query` 的节点结果读取并沿用该页面的 `spaceId`，不调用上述 API 重新做默认选择；不得改用外部提供或构造的 ID。
- 新建、导入、克隆或从素材生成页面：解析出目标 Space 后，先按 [`page-manage.md`](page-manage.md) 创建远端工程目录，保存返回的 `<project_folder_id>` 和工程目录相对路径，再创建 HTML、Markdown 和页面所需 Database；Database 创建时在 `schema` 中传 `"parent_id":"<project_folder_id>"`，使其落在工程目录内。
- 用户明确指定已有工程目录时才复用该目录。新页面未指定工程目录名时，使用简短、可识别的中文名作为 `<page-slug>`（如「记账本」「销售看板」）；名称冲突时自动追加中文序号等后缀生成不冲突名称，不询问用户，不静默覆盖或复用已有目录。
- 新页面未指定文件名：使用简短的中文 `<page-slug>.html`（如「记账本.html」）。Database 名称、Markdown 文件名同样使用中文。**本地临时 HTML 文件的 basename 会成为 `upload-node` 上传后的 web 节点标题，因此临时文件也必须用中文命名（如 `/tmp/.moma-tmp/记账本.html`），不得用英文 slug。** 创建 Database 后，以响应中的 `database_name` 作为真实 Database 名。
- 已有页面只有路径或发布 URL：用文件查询或 node-info 定位节点，并复用其当前 `parent_id` 对应的父目录作为工程目录；不新建、不迁移。
- 持久化 HTML 与 Markdown 必须位于同一远端工程目录；Database 创建时传 `"parent_id":"<project_folder_id>"` 归入工程目录，并通过响应中的真实 `database_id` 和 `database_name` 与最终 HTML、项目文档建立逻辑关联。本地临时工作区不属于该目录。

## 4. 依赖

所有流程加载：

- [`html-analysis.md`](html-analysis.md)
- [`artifact-contract.md`](artifact-contract.md)
- [`resource-normalization.md`](resource-normalization.md)
- [`page-manage.md`](page-manage.md)

动态页额外加载：

- [`database/page-database.md`](database/page-database.md)：Agent 构建期 CLI；
- [`database/database-sdk-contract.md`](database/database-sdk-contract.md)：页面运行期策略和示例；
- [`database/database-sdk-schema.md`](database/database-sdk-schema.md)：页面运行期参数与返回结构；
- [`page-database-relation.md`](page-database-relation.md)：运行期 ID 和条件服务端关系。

修复已有应用时加载 [`repair-guide.md`](repair-guide.md) 和 [`beautify-flow.md`](beautify-flow.md)。需要附件或图片时加载 [`page-attachment.md`](page-attachment.md)。其他视觉实现先加载 [`beautify-flow.md`](beautify-flow.md)，视觉细节再看 [`beautify/beautify-guide.md`](beautify/beautify-guide.md)。

## 5. 完成条件

1. 新页面已先创建远端工程目录；已有页面已核对并复用原父目录；
2. 持久化 HTML 与 Markdown 均位于该工程目录，页面依赖的 Database 已通过真实 `database_id` 关联；
3. final HTML 已生成并通过资源检查；
4. 动态页写入真实 `database_id`，通过 current SDK 使用注入能力，并通过 SDK 静态检查；
5. Page↔Database final ID 集已验证，正式关系 API 存在时已同步；
6. HTML 已上传为 web 节点；
7. web 节点已发布；
8. 已取得发布 URL；
9. 本次本地中间产物已清理，远端工程目录及其中节点保留；
10. 向用户返回发布 URL。
