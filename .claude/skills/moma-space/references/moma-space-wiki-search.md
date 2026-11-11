# moma moma-space api POST_kebase_api_v1_wiki_search

该接口支持在一个或多个 Space 内检索已归纳的 Wiki 知识页面，适合主题综述、概念解释、和跨文档关系梳理；它与返回原始文档切片的 `kb-search_files` 是两条独立链路。

## Recommended Command

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

```bash
moma moma-space api POST_kebase_api_v1_wiki_search --json --data '{
  "task_id":"<TASK_ID>",
  "query":"核算规则",
  "space_ids":["<SPACE_ID>"],
  "page_types":["concept","document","index"],
  "folder_id":123,
  "include_descendants":true,
  "offset":0,
  "limit":20
}'
```

## 请求 body 参数

| 字段 | 是否必填 | 含义                                                  |
|------|---------|-----------------------------------------------------|
| `task_id` | 可选 | 调用方任务 ID，最长 200 字符；已有服务端 mint ID 时原样复用              |
| `query` | **必填** | Wiki 检索词，字面匹配机制，去除首尾空白后不能为空，最长 200 字符               |
| `space_ids` | **必填** | Space ID 数组，1～5 个；只能传 ID，不能传标题                      |
| `page_types` | 可选 | 页面类型过滤，例如 `concept`、`document`、`index`；不传或空数组表示不过滤  |
| `folder_id` | 可选 | Wiki 分类目录 ID；传入后 `space_ids` 必须只有一个 Space，`0` 表示根分类 |
| `include_descendants` | 可选 | 指定分类时是否包含所有后代分类，默认 `true`；`false` 只搜索直属页面           |
| `offset` | 可选 | 分页偏移量，默认 `0`                                        |
| `limit` | 可选 | 返回数量，默认 `20`，范围 1～100                               |

## 响应说明

- `items[].slug` 与 `items[].space_id` 是后续调用 [`wiki_page`](moma-space-wiki-page.md) 的定位参数。
- `items[].folder_id/category_path` 表示 Wiki 分类位置，可在结果过宽时用于选择分类并重新发起 scoped Search；它们不是 Space 原始资料目录 ID/路径。
- `summary` / `snippet` 是轻量归纳信息：可直接用于候选筛选和不要求细节的主题概览；它们不等于完整页面，也不能作为精确原文证据。只有当前问题需要详细正文且摘要不足时才调用 `wiki_page`。
- 多空间检索中部分空间不可访问时，继续处理 `accessible_space_ids` 的结果；Wiki 未开启的空间，停止 Wiki 链路；改用 `kb-search_files`。注意向用户说明 `permission_message`；不得悄悄扩大范围。
- `total > offset + items.length` 时，可增加 `offset` 继续分页；不要原样重复同一请求。

## Workflow

1. 只有空间标题时，先用 `GET_api_v1_tools_spaces` 精确映射为 Space ID；重名时让用户选择。
2. 将用户问题压缩为主题关键词；需要按页面类型收窄时才传 `page_types`。明确关键词直接 Search，不要机械地先读导航索引。
3. 开放探索或无法形成可靠关键词时，先用 [`wiki_navigate`](moma-space-wiki-navigate.md) 按层定位分类主题。
4. 调用 Wiki Search，根据标题、摘要、命中字段、分数挑选与query相关的内容和wiki页面。
5. 若需读取候选wiki页面完整内容，可进一步调用 `POST_kebase_api_v1_wiki_page` ；禁止根据标题自行拼 slug，也禁止无选择地批量读取全部结果。
6. 摘要或内容足以回答主题综述时直接整理，并明确这是 Wiki 归纳信息。
7. 用户要求精确数字、条款、步骤、原话或来源证据时，根据页面的 `source_refs/chunk_refs` 或待核实问题，再调用 `POST_api_v1_tools_kb-search_files` 定向检索原始切片。
8. Wiki 无命中、目标空间未开启 Wiki，或页面内容不足时，降级到 `kb-search_files` 原始切片搜索。Wiki 未命中不表示原始文档没有相关内容。

## 检索边界

- Wiki Search 当前是对 `title`、`slug`、`summary`、`aliases`、`content` 的字面匹配及字段加权排序，不是向量语义搜索。
- Wiki 页面是跨原始文件整理后的主题页，适合“是什么、有哪些、关系、全貌、入口”等问题。
- `kb-search_files mode=content` 返回原始文档切片，适合指定文件/目录、精确事实和可核验依据。
- 两条链路保持独立；不得把 Wiki 结果伪装成原始切片，也不得把两个接口拼成不存在的统一 API。

## 错误处理

| 情况 | Agent 处理                                                                  |
|------|---------------------------------------------------------------------------|
| 所有空间均不可访问 | 返回空结果和权限说明；停止 Wiki 链路，不绕过权限                                               |
| 目标空间未开启 Wiki | 改用 `kb-search_files` 原始切片搜索，并向用户说明降级原因                                    |
| `items` 为空 | 若尚未导航，先 Navigate 一次，根据导航内容改写query；仍无结果则转 `kb-search_files`，禁止多轮盲猜      |
| Wiki 分类目录不存在 | 回到 `wiki_navigate` 重新取得 folder ID，不猜 ID、不改用 Space 文件夹 ID                  |
| 参数校验失败 | 修正 `space_ids/page_types/folder_id/include_descendants/offset/limit`，禁止猜测字段 |

## Notes

- 本接口为只读操作，不使用 `--dry-run` 或 `--yes`。
- 不要用本接口找原始资料文件名、列目录或定位具体文件；这些场景分别使用 `kb-search_files mode=file_name`、`files_children` 或 `files_query`。
