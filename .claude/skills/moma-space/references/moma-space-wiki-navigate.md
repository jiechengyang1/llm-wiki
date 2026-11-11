# moma moma-space api POST_kebase_api_v1_wiki_navigate

逐层浏览空间 Wiki 的知识分类和当前分类直属页面，用于了解空间 Wiki 知识框架、回答全局/分类概览、确定 Wiki Search 的字面匹配 query 或收窄检索范围。Navigate 返回的概括、分类和轻量页面信息本身可以直接用于框架类回答。
注意：本接口读取的是 Wiki 归纳页分类树，不是 Space 中用户上传的原始文件和文件夹的物理目录。

## Recommended Command

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

```bash
moma moma-space api POST_kebase_api_v1_wiki_navigate --json --data '{
  "task_id":"<TASK_ID>",
  "space_id":"<SPACE_ID>",
  "folder_id":0,
  "page_types":["concept","document","entity"],
  "folder_offset":0,
  "folder_limit":50,
  "page_offset":0,
  "page_limit":50
}'
```

## body 参数

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `task_id` | 可选 | 调用方任务 ID；有服务端 mint ID 时全轮原样复用，以串联 Navigate/Search/Page 检索记录 |
| `space_id` | **必填** | 单个 Space ID，不能传标题 |
| `folder_id` | 可选 | 当前 Wiki 分类 ID；默认 `0` 表示根分类 |
| `page_types` | 可选 | 只过滤页面条目与页面计数，例如 `concept/document/entity` |
| `folder_offset` | 可选 | 直属子分类分页偏移量，默认 `0` |
| `folder_limit` | 可选 | 直属子分类数量，默认 `50`、最大 `100` |
| `page_offset` | 可选 | 直属页面分页偏移量，默认 `0` |
| `page_limit` | 可选 | 直属页面数量，默认 `50`、最大 `100` |

## 响应语义

- `current_folder`：当前 Wiki 分类；根节点为 `null`。
- `breadcrumbs`：从顶层分类到当前分类的路径。
- `index_page`：当前分类对应的轻量 index 页引用；可能为 `null`，避免与列表内容重复。
- `child_folders`：当前分类的直属子分类和分页信息。
- `pages`：当前分类直属、已发布、未删除且非 index 的 Wiki 页面和分页信息。
- 子分类中的 `direct_page_count/subtree_page_count` 用于判断是停留当前层还是继续向下展开。

目录只有子分类、没有直属页面时，`pages.total=0` 且 `index_page` 可能为 `null`，但 `child_folders` 仍然有效。禁止因此判断分类不存在。

## 推荐决策链路

1. 问题已有明确稳定关键词时直接 `wiki_search`，不要机械地先 Navigate。
2. 询问空间整体内容、主要主题或知识框架时，从 `folder_id=0` 开始 Navigate；依据根概括、分类名称、页面数量和轻量页面摘要总结组织回答，必要时进一步展开分类获取更多框架结构信息，避免逐个调用读取`pages.items`的页面详情。
3. 开放探索或无法形成可靠检索关键词时，通过Navigate逐层了解知识框架，根据分类名称展开相关分支，选择合适的关键词、 检索范围（Wiki `folder_id`） 传给 `wiki_search`，通常设置 `include_descendants=true`。
4. `wiki_page` 只用于具体问题确实需要wiki页详情且 Navigate/Search 摘要不足的情况；一次只读取少量相关页面，需要原文证据时再转 `kb-search_files`。
5. 只有明确需要列出全部 Wiki 分类或页面时，才增加 offset 遍历全部分页，并分批总结。

## 与 Space 原始资料目录的区别

| Wiki 分类导航                              | Space 原始资料目录 |
|----------------------------------------|-------------------|
| 知识归纳分类，服务与知识框架与主题理解、 Wiki Search 范围收窄  | 用户上传文件/文件夹的物理存储结构 |
| 使用 `wiki_navigate`，返回 Wiki `folder_id` | 使用 `files_children/files_query`，返回 Space 文件夹或文件 ID |
| 路径对应 Wiki 页面分类                         | 路径对应可下载、读取或编辑的原始文件 |

两套 ID 和路径完全独立，禁止交叉传参。


- “列出 `@/kespace/项目空间/制度` 下有哪些 PDF” → Space 原始资料目录：`files_query/files_children`。
- “读取报销规范.pdf 并找住宿费原文” → Space 文件接口和 `kb-search_files`。
- “特定实体/概念的说明或综述性问题” → 本接口定位 Wiki `folder_id` 或 主题词query → `wiki_search`。

## Token 控制

- 单次默认最多 50 个子分类和 50 个页面，上限分别为 100；`pages.items` 是轻量导航信息，不是待逐项读取的页面队列。
- 不预加载完整分类树，不默认遍历全部分页。
- Navigate 的概括与轻量摘要足以满足当前问题时直接回答；不要仅因页面存在或担心遗漏而随意调用 `wiki_page` 获取大量页面信息。

## 错误处理

| 情况 | 处理方式                            |
|------|---------------------------------|
| Wiki 分类目录不存在 | 回到父分类重新 Navigate；不能猜 folder ID  |
| Wiki 未开启或无权限 | 停止 Wiki 链路；改用 `kb-search_files` |
| 当前层没有页面但有子分类 | 按需继续探索相关子分类                 |
| 分类和页面超过本页上限 | 仅在当前问题确有需要时增加对应 offset          |
| Gateway 没有本 apiName | 停止调用，说明 Gateway 尚未同步；不能自行拼接口    |

本接口为只读操作，不使用 `--dry-run` 或 `--yes`。
