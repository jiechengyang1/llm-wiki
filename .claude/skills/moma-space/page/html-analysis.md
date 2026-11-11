# HTML 与需求分析合同

在生成、编辑、导入或克隆前，先把用户意图和来源 HTML 归一化为 [`page-analysis-schema.md`](page-analysis-schema.md)。分析是只读步骤，不替代真实 schema discovery，也不是授权流程。

## 1. 输入

```bash
python3 page/analyze_page.py \
  --html '<temporary-workdir>/source.html' \
  --intent '<用户原始需求>'
```

`--html` 和 `--intent` 至少提供一个。HTML 来自普通 URL 时用宿主下载能力；来自 Space 节点时，先用 `GET_api_v1_tools_files_query` 查询精确相对路径，再用 `POST_api_v1_tools_file_presigned_url` 获取 URL 并下载到 `/tmp/.moma-tmp/`。不得输出完整 URL；处理完成后仅在校验目标路径以 `/tmp/.moma-tmp/` 开头且文件确由本轮下载后删除，否则停止删除。

## 2. 合并证据

分析器合并而不是抢占式匹配以下证据：

1. 用户是否明确要求保存、维护、查询、筛选、分页、增删改或共享持续数据；
2. 当前入口 `window.__SPACE_PAGE__.database` 及实际 SDK 方法；
3. `database_id` 字面量、常量和对象属性；
4. form、input、select、textarea、submit 与字段名；
5. table 表头、`data-field`、模板占位符；
6. 重复卡片、列表、网格和内联数组；
7. fetch/XHR/外部数据源信号；
8. 图片、样式、脚本、字体等资源引用。

任何单个 table 或重复结构都不能自动证明需要 Database。

## 3. Database 需求级别

| level | 判据 | 默认路由 |
|---|---|---|
| `strong` | 当前 SDK；明确要求持久化/维护；提交表单保存；记录 CRUD | dynamic |
| `medium` | form、筛选、分页、结构化数据与后续维护语义同时存在 | 按用户意图选 readonly/readwrite |
| `weak` | 只有表格、卡片、列表或可结构化展示 | static |
| `none` | 报告、专题、叙事、一次性展示 | static |

动态页进一步区分：

- 只查询、筛选、排序、分页、看板：`database-readonly`；
- 新增、更新、删除或表单提交后持久化：`database-readwrite`。

当证据已足够时直接路由，不为了技术选型增加额外询问。

## 4. 字段推断

字段名优先级：

```text
真实 getSchema Property.name
→ form name
→ data-field
→ label/表头
→ 稳定文本
```

类型推断只生成候选 schema：

- 多个合法数字值 → `{ number: 0 }`；
- select → `{ select: { options: [...] } }` 候选；
- 多值标签 → `{ multi_select: { options: [...] } }` 候选；
- 其他 → `{ text: "" }`。

生成读写代码前必须按 [`database/page-database.md`](database/page-database.md) 读取或创建真实 schema。不得把推断结果冒充已有 Database 的真实字段。

## 5. 当前 SDK 和 ID 提取

只识别当前 SDK。动态来源中提取全部唯一 Database ID，不能只取第一个。主要信号包括：

```javascript
const DATABASE_ID = "db_001";
await db.query({ database_id: DATABASE_ID });
await db.getSchema({ database_id: "db_002" });
```

输出的 `sdk.database_ids` 是后续复制与 remap 的输入。未提取到字面 ID 时，分析结果降低 confidence，克隆流程必须从配置或实际节点关系中获得真实 ID，不能生成占位 ID。

## 6. 输出使用

- static → [`static-page-flow.md`](static-page-flow.md)；
- database-* → [`data-page-flow.md`](data-page-flow.md)；
- import/clone → [`import-clone-flow.md`](import-clone-flow.md)；
- 资源清单 → [`resource-normalization.md`](resource-normalization.md)；
- 上传前运行 current-only SDK 和资源检查器。

分析 JSON 是临时中间产物。发布成功并取得 URL 后一并清理。
