# moma moma-space api POST_kebase_api_v1_wiki_page

读取一个确有必要的 Wiki 页面的完整内容和来源引用，用于具体主题的详细解释或补足摘要总结缺失的信息；不用于搜索、猜测页面地址或遍历空间知识框架。

## Recommended Command

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

```bash
moma moma-space api POST_kebase_api_v1_wiki_page --json --data '{
  "task_id":"<TASK_ID>",
  "space_id":"<SPACE_ID>",
  "slug":"concept/accounting-rule"
}'
```

## body 参数

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `task_id` | 可选 | 调用方任务 ID；与本轮 Navigate/Search 原样复用，以串联服务端检索记录 |
| `space_id` | **必填** | Wiki Navigate 响应顶层或 Wiki Search 命中项中的 Space ID，最长 40 字符 |
| `slug` | **必填** | Wiki Navigate 的 `pages.items[]` 或 Wiki Search 命中项中的页面 slug，最长 150 字符 |

从 Navigate 选择页面时，使用同一响应顶层的 `space_id` 与该 `pages.items[]` 的 `slug`；从 Search 选择页面时，使用同一命中项的 `space_id + slug`。禁止使用 Space 标题代替 ID、根据标题自行拼 slug，或跨结果组合参数。

## 响应结构

成功时返回页面详情，主要字段如下：

| 字段 | 含义                                       |
|------|------------------------------------------|
| `space_id` / `slug` / `title` | 页面定位和标题                                  |
| `page_type` / `category` / `path` | 页面类型、分类和路径                               |
| `content` | Wiki 完整正文                                |
| `summary` / `aliases` | 页面摘要和别名                                  |
| `source_refs` | 来源文件引用，通常含 `space_file_id`、`file_name` 等 |
| `chunk_refs` | Wiki 生成时关联的原始切片引用                        |
| `in_links` / `out_links` | Wiki 页面关系：本页被哪些页面引用 / 本页引用了哪些页面          |
| `version` / `updated_at` | 页面版本和更新时间，可忽略                     |

## Workflow

1. 先根据 [`wiki_navigate`](moma-space-wiki-navigate.md) 的页面条目或 [`wiki_search`](moma-space-wiki-search.md) 的命中项判断摘要总结是否足够；足够回答时停止，不调用本接口。
2. 只有具体问题需要详细内容且摘要不足时，选择少量相关页面，按上述定位规则传入 `space_id + slug`；禁止把 Navigate 的 `pages.items` 或 Search 的全部结果逐项读取。
3. 用 `content` 回答具体概念、主题细节或关系问题，并明确内容来自 Wiki 归纳页。
4. 如用户要求精确数字、条款、步骤、原话或来源证据：
   - 优先使用 `source_refs[].space_file_id` 形成 `kb-search_files` 的 `file_id` 数组；
   - 以待核实的具体事实作为 `query`，调用 `mode=content`；
   - `chunk_refs` 可辅助判断引用来源，但必须以原始切片检索结果为准，不自行猜测切片读取接口。
5. Wiki 页面之间的链接只用于继续导航；需要读取链接页时，应先确认其 slug 出现在当前返回的链接信息或新的 Wiki Search 结果中。

## 错误处理

| 情况 | Agent 处理                                                                          |
|------|-----------------------------------------------------------------------------------|
| 403 / `PERMISSION_DENIED` | 停止读取该 Space；不重试、不绕过                                                               |
| 404 / Wiki 页面不存在 | 检查slug是否提取正确，仍不存在则转 `kb-search_files`，不能盲猜 slug                                   |
| 页面非 published 或已删除 | 按不存在处理，不尝试管理 API 或历史版本接口                                                          |
| `source_refs` 为空 | 可以回答 Wiki 综述；若用户要求原文证据，改用问题本身在目标 Space 执行 `kb-search_files` 搜索，并说明无法从该wiki页定向来源文件 |

## Notes

- 本接口为只读操作，不使用 `--dry-run` 或 `--yes`。
- Wiki 页面正文是归纳内容，不等价于原始文件逐字表述。
- `page_type=index` 的目录页面只是当前分类的落地页，不代表完整分类树；需要发现或展开分类时使用 `wiki_navigate`，不要靠猜 index slug 导航。
- 禁止把 `summary/snippet` 当完整页面，禁止把 Wiki 页面的 `path` 当 Space 文件路径传给文件下载接口。
- 用户需要来源文件时，基于明确的 `source_refs[].space_file_id` 使用 `file_access_link`方法获取在线预览链接；需要下载原文件时使用 `file_presigned_url`方法获取原文件下载链接。
