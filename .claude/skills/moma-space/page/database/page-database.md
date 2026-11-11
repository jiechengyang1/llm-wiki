# Agent 构建期 Database CLI

本流程中的已明确 API 直接调用；写操作首次调用即携带 `--yes`。

本文件供 Agent 通过 `moma-space` CLI 创建和维护 Database。页面浏览器运行时使用 [`database-sdk-contract.md`](database-sdk-contract.md)。

CLI 请求字段与页面 SDK 字段都使用 snake_case，但两层调用方式不同：Agent 使用 Gateway 命令，HTML 使用注入的 JavaScript SDK。

## 1. 参数真源

常用 API 直接使用本文示例。参数结构不确定、接口新增或 CLI 报字段错误时，通过当前 `moma-space` 注册信息取得实时合同：

```bash
moma moma-space list
moma moma-space schema <FULL_API_NAME>
moma moma-space describe <FULL_API_NAME> \
  --request '{"body":{...}}' \
  --json
```

- `list` 返回当前注册 API 名；
- `schema` 返回 request body、query、multipart 和 response schema；
- `describe` 用实际请求结构验证参数映射；请求体放在 `body` 中；
- multipart 文件继续通过 `--file 'file=<local-path>'`（`field=path` 格式，字段名固定 `file`）传入，不写进 JSON body；
- 取得正确结构后调用 `moma moma-space api <FULL_API_NAME> ...`；持久化写调用首次直接携带 `--yes`。

## 2. 创建和读取 schema

创建 Database 时除目标 Space 和表结构外，应在 `schema` 中传 `"parent_id":"<project_folder_id>"`，使 Database 归入工程目录，与 HTML、Markdown 保持内聚；创建成功后保存响应中的真实 `database_id`、`database_name` 和 `parent_id`。`database_name` 是真实 Database 名，页面运行期 SDK 仍通过 `database_id` 调用；最终 HTML 和项目文档同时记录真实 ID 与名称。

```bash
moma moma-space api POST_api_v1_tools_storage_table_create-database \
  --data '{
    "schema": {
      "space_id": "<space_id>",
      "title": "项目任务",
      "parent_id": "<project_folder_id>",
      "properties": [
        {"name":"任务名称","config":{"text":""}},
        {"name":"完成状态","config":{"checkbox":false}},
        {"name":"截止日期","config":{"date":{}}},
        {"name":"优先级","config":{"select":{"options":[
          {"text":"高","style":1},
          {"text":"中","style":2},
          {"text":"低","style":3}
        ]}}},
        {"name":"工时","config":{"number":{}}}
      ]
    }
  }' \
  --yes \
  --json

moma moma-space api POST_api_v1_tools_storage_table_get-database-schema \
  --data '{"database_id":"db_abc123"}' \
  --json
```

新 MOMA Space 页面创建 Database 时，在 `schema` 中传 `"parent_id":"<project_folder_id>"`，使 Database 落在工程目录内。每个 property 需要 `name` 和单一 `config` 类型。

**config 类型以后端 schema 为准**，区分标量与对象，传错类型会报 `INVALID_REQUEST`：

| config 类型 | 后端类型 | 创建时写法 |
|---|---|---|
| `text` | string | `{"text":""}` |
| `email` | string | `{"email":""}` |
| `phone_number` | string | `{"phone_number":""}` |
| `checkbox` | boolean | `{"checkbox":false}` |
| `date` | object | `{"date":{}}` |
| `number` | object（子字段 `decimal_places`/`use_separate`/`display_type`，均可省略） | **`{"number":{}}`**，不能写 `{"number":0}` |
| `currency` | object（子字段 `currency_symbol`/`decimal_places`/`use_separate`，均可省略） | **`{"currency":{}}`**，不能写 `{"currency":0}` |
| `select` | object（`options` 数组） | `{"select":{"options":[{"text":"高","style":1}]}}` |
| `multi_select` | object（`options` 数组） | `{"multi_select":{"options":[{"text":"研发","style":1}]}}` |
| `url` | object（`text`/`link`，均可省略） | `{"url":{}}` |
| `image`/`attachment`/`person` | object | `{}` 内按子字段，创建时通常 `{"image":{}}` 等 |

`number`/`currency` 的 config **必须是对象**，写成数字或字符串会被后端拒绝；`decimal_places`、`use_separate`、`display_type`、`currency_symbol` 都是选填子字段，省略时后端用默认值。

## 3. 字段操作

```bash
moma moma-space api POST_api_v1_tools_storage_table_add-field \
  --data '{"database_id":"db_abc123","property":{"name":"负责人","config":{"text":""}}}' \
  --yes \
  --json

moma moma-space api POST_api_v1_tools_storage_table_update-field \
  --data '{"database_id":"db_abc123","field_id":"field_001","property":{"name":"任务优先级"}}' \
  --yes \
  --json

moma moma-space api POST_api_v1_tools_storage_table_delete-field \
  --data '{"database_id":"db_abc123","field_id":"field_001"}' \
  --yes \
  --json
```

字段操作后用 `POST_api_v1_tools_storage_table_get-database-schema` 取得当前真实 schema。

### 读取 schema 的返回

`get-database-schema` 返回 `{ id, parent_id, title, properties }`：`id` 即 `database_id`，`parent_id` 是 Database 所属父目录 ID（创建时未传 `parent_id` 则为空字符串），`properties` 是含服务端生成 `id` 的完整字段列表。编辑已有页面或定位 Database 归属工程目录时，可用 `parent_id` 核对其父文件夹，无需再另行查询文件树。

`create-database` 返回 `{ database_id, database_name, space_id, parent_id, property_count, properties }`：`database_id` 是页面运行期 SDK 使用的真实 ID；`database_name` 是创建后的真实 Database 名；`parent_id` 回显创建时传入的父目录 ID（未传则为空字符串），用于验证 Database 已归入目标工程目录。

### 删除 Database

删除整个 Database（数据表及其全部记录、字段），仅按 `database_id` 定位，不需要 `space_id` 或 `parent_id`。删除不可逆；仅在页面生命周期的删除目标明确时直接调用，首次携带 `--yes`：

```bash
moma moma-space api POST_api_v1_tools_storage_table_delete-database \
  --data '{"database_id":"db_abc123"}' \
  --yes \
  --json
```

返回 `{"database_id":"db_abc123","deleted":true}`。`delete_batch` 只能按文件路径删文件/文件夹，不能删 Database；Database 必须按 `database_id` 使用本接口删除。

## 4. PropertyValue

| 类型键 | 示例 |
|---|---|
| `text` | `{"text":"季度复盘"}` |
| `number` | `{"number":25}` |
| `currency` | `{"currency":1234.56}` |
| `select` | `{"select":"高"}` |
| `multi_select` | `{"multi_select":["重点","本周"]}` |
| `date` | `{"date":"2026-10-31"}` |
| `checkbox` | `{"checkbox":true}` |
| `url` | `{"url":{"text":"官网","link":"https://example.com"}}` |
| `email` | `{"email":"a@example.com"}` |
| `phone_number` | `{"phone_number":"13000000000"}` |
| `image` | `{"image":{"images":[{"title":"封面","imageUrl":"https://..."}]}}` |
| `attachment` | `{"attachment":[{"name":"报告.pdf","attachmentId":"att_1","fileType":"application/pdf","fileSize":10240,"mediaType":"file"}]}` |
| `person` | `{"person":[{"id":"uid123"}]}` |

写入字段名和类型以当前 schema 为准。

## 5. 批量记录操作

每批 1–100 条：

```bash
moma moma-space api POST_api_v1_tools_storage_table_batch-add-records \
  --data '{"database_id":"db_abc123","records":[{"任务名称":{"text":"编写接口文档"},"完成状态":{"checkbox":false},"优先级":{"select":"高"}}]}' \
  --yes \
  --json

moma moma-space api POST_api_v1_tools_storage_table_batch-update-records \
  --data '{"database_id":"db_abc123","records":[{"record_id":"190000000000000001","properties":{"完成状态":{"checkbox":true}}}]}' \
  --yes \
  --json

moma moma-space api POST_api_v1_tools_storage_table_batch-delete-records \
  --data '{"database_id":"db_abc123","record_ids":["190000000000000001"]}' \
  --yes \
  --json
```

## 6. 构建期读取

```bash
moma moma-space api POST_api_v1_tools_storage_table_get-record \
  --data '{"database_id":"db_abc123","record_id":"190000000000000001"}' \
  --json

moma moma-space api POST_api_v1_tools_storage_table_query-database-records \
  --data '{"database_id":"db_abc123","filter":{"and":[{"property":{"property":"完成状态","checkbox":{"equals":false}}}]},"sorts":[{"property":"截止日期","direction":"ascending"}],"page_size":100}' \
  --json

moma moma-space api POST_api_v1_tools_storage_table_get-database-content \
  --data '{"database_id":"db_abc123"}' \
  --json
```

Agent 查询 `page_size <= 100`。响应 `has_more=true` 时，将 `next_cursor` 作为下一次请求的 `cursor`。

## 7. 多 Database 克隆

克隆动态页时先由 `analyze_page.py` 提取全部源 ID。对每个 ID 独立读取 schema，并以目标 `"space_id":"<space_id>"` 创建目标 Database，创建请求传 `"parent_id":"<project_folder_id>"`，使目标 Database 落在工程目录内。再以 `page_size <= 100` 分页读取并以 1–100 条分批写入。生成完整 old→new mapping 后使用 `remap_database_ids.py` 一次性替换，禁止链式替换和旧 ID 残留。

## 8. Page ↔ Database 关系发现

关系 API 必须先出现在 `moma moma-space list`，再用 `schema/describe` 获取实时合同。当前列表没有明确 link/list/unlink API 时，按 [`../page-database-relation.md`](../page-database-relation.md) 只维护最终 HTML 中的真实运行期 ID，不调用私有 HTTP，也不把节点层级当关系。

## 9. 交给页面运行期

把真实 Database ID 写进 HTML。页面从 `window.__SPACE_PAGE__.database` 调用 SDK。查询使用 `database_id`、`cursor`、`page_size`，返回 `next_cursor`、`has_more`；记录结构为 `{ record_id, fields }`。新增使用 `record`，更新使用 `properties`。具体合同见 [`database-sdk-contract.md`](database-sdk-contract.md)。
