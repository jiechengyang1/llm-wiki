# moma moma-space api POST_api_v1_tools_kb-search_files

> 接口名：`kb-search_files`。该接口由 SpaceKnowledgeBase 提供，用于搜索一个或多个空间内的文件内容或文件名。

## Recommended Commands

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

### 搜索指定文件内容

当问询指定了具体文件，可通过文件 ID `file_id` 直接检索目标文件的切片，**无需传 `space_ids`**，接口会先校验当前用户对这些文件的读权限。
（此类搜索最多返回1000个内容切片）

```bash
moma moma-space api POST_api_v1_tools_kb-search_files --json --data '{
  "task_id":"<TASK_ID>",
  "query":"核算规则",
  "mode":"content",
  "file_id":["7594759a-b6d8-4634-bd62-2ea44dd7c3bc"]
}'
```

> 当没有现成的 file_id 信息，需要基于文件的路径取得 `file_id` 时，使用`GET_api_v1_tools_files_query`


### 限定目录搜索

`directory` 为空间内目录路径。指定目录时只能传一个空间。
（此类搜索最多返回20个内容切片）

```bash
moma moma-space api POST_api_v1_tools_kb-search_files --json --data '{
  "task_id":"<TASK_ID>",
  "query":"API",
  "mode":"content",
  "space_ids":["<SPACE_ID>"],
  "directory":"/<space_title_or_id>/<folder relative_path>"
}'
```

### 单空间/多空间内容搜索

（此类搜索最多返回20个内容切片）

```bash
moma moma-space api POST_api_v1_tools_kb-search_files --json --data '{
  "task_id":"<TASK_ID>",
  "query":"核算指引",
  "mode":"content",
  "space_ids":["<SPACE_ID_1>","<SPACE_ID_2>"]
}'
```

### 按文件名搜索

```bash
moma moma-space api POST_api_v1_tools_kb-search_files --json --data '{
  "task_id":"<TASK_ID>",
  "query":"SPACE.md",
  "mode":"file_name",
  "space_ids":["<SPACE_ID>"],
  "page_size":500,
  "page_no":1
}'
```

#### 文件名搜索分页与自定义数量

`mode=file_name` 支持通过 `page_no` 翻页，并通过 `page_size` 指定每页返回数量。例如每页返回 100 条，第 2 页：

```bash
moma moma-space api POST_api_v1_tools_kb-search_files --json --data '{
  "task_id":"<TASK_ID>",
  "query":"SPACE.md",
  "mode":"file_name",
  "space_ids":["<SPACE_ID>"],
  "page_size":100,
  "page_no":2
}'
```

## body 参数

| 字段 | 是否必填 | 含义                                                                                                                                |
|------|---------|-----------------------------------------------------------------------------------------------------------------------------------|
| `task_id` | **必填** | MomaAgent 必须用本轮 prompt 的服务端 mint id，勿自行生成；Claude Code 只有文本 `@/kespace` / `Space ID + path` 且未给 id 时，生成一个短 id 并全轮复用。**不要靠它理解圈定范围** |
| `query` | **必填** | 搜索关键词；去除首尾空白后不能为空                                                                                                                 |
| `mode` | **必填** | `content`：内容检索；`file_name`：文件名检索                                                                                                  |
| `space_ids` | **必填\*** | 空间 ID 数组，至少包含一个；传 `file_id` 时可省略；                                                                                                |
| `file_id` | 可选 | 指定文件 ID 列表（**`list[str]`**，如 `["id1","id2"]`）；**禁止使用 `file_ids` 字段，接口不存在该字段**；仅 `content` 模式；传此参数时 `space_ids` 可不传，接口会先校验读权限，无权限返回 403 |
| `directory` | 可选 | 空间内目录路径，格式固定为`/<space_title_or_id>/<folder relative_path>` ；指定目录路径后 `space_ids` 只能有一个；与 `file_id` 互斥                             |
| `page_size` | `mode=file_name` 时可选 | 文件名搜索每页条数；用户可自定义，默认 `500`                                                                                                         |
| `page_no` | `mode=file_name` 时可选 | 文件名搜索页码，从 `1` 开始，默认 `1`                                                                                                           |

## 响应结构

成功响应由 Gateway 统一包装：

| 字段 | 含义 |
|------|------|
| `success` | 是否成功 |
| `data` | 搜索结果；内容搜索通常是对象，文件名搜索是文件条目数组 |
| `error` | 失败时的错误信息，成功时通常为 `null` |

## 内容完整性边界

`POST_api_v1_tools_kb-search_files` 的 `mode=content` 是相关切片检索，不是全文读取：

- 普通 Space 或目录范围搜索最多返回 20 条高相关切片；
- 明确传入 `file_id` 时，为了覆盖更多内容最多返回 1000 条高相关切片；
- 返回达到上限或低于上限，都不能据此断定已经覆盖文件全部切片、完整章节或全部上下文；
- 不得把切片拼接结果直接声称为“源文件全文”。

当用户要求文档全文、全文总结、完整上下文、逐章分析，或现有切片可能遗漏前后文时：

1. 从命中切片元数据取得关联的源文件 ID；
2. 确认该文件所属 Space 和相对路径；如果结果没有路径，使用已有引用元数据或 Space 文件导航/查询能力定位，禁止把文件 ID 当 `filepath`；
3. 调用 `POST_api_v1_tools_file_presigned_url` 获取下载链接；
4. 将原文件下载到 `/tmp/.moma-tmp/`，再根据文件类型读取全部内容；
5. 处理完成后按临时文件清理规则删除本轮下载文件。

## Workflow

1. `task_id` 全轮复用：MomaAgent 必须用本轮 prompt 的服务端 mint id，勿自行生成；Claude Code 只有文本 `@/kespace` / `Space ID + path` 且未给 id 时，生成一个短 id 并全轮复用。不要靠它理解圈定范围。
2. 只有空间标题时，先用 `GET_api_v1_tools_spaces` 精确映射为 Space ID；重名时让用户选择。
3. 话题问答、总结和探索使用 `mode=content`。
4. 查找文件名或 list files 使用 `mode=file_name`；需要翻页时传 `page_size` 和 `page_no`，默认分别为 `500` 和 `1`。
5. 有明确目录时，调用前必须完成以下检查：
   - `space_ids` 仅包含单个 Space ID；
   - `directory` 参数格式为 `/<space_title_or_id>/<folder relative_path>`，即"/空间标识/目录相对路径"；
   （任一条件不满足时，先修正参数，否则不得调用 API。）
6. 需要检索指定文件内容且已知具体文件 ID 时，传 `file_id`（`list[str]`，仅 `content` 模式），无需 `space_ids`；支持同时指定多个文件 ID。最多返回 1000 条相关切片，仍不等于文件全文。
7. 切片内容明显不足、或用户明确要求全文时，再根据切片关联的源文件 ID 定位所属 Space 和文件相对路径，调用 `file_presigned_url` 获取链接并下载原文件。

## Notes

- **`file_id` 是 `list[str]` 数组类型（如 `["id1","id2"]`）；不存在 `file_ids` 字段，禁止使用。**
- 内容搜索结果是固定数量上限内的相关切片，不是源文件全部内容；问题必须根据全文回答时转入 `file_presigned_url` 获取原文件下载链路。
- 搜索结果按当前用户权限过滤，不能借此绕过文件权限。
- `@cli.py`、`@src/cli.py` 等本地引用不调用此接口。
