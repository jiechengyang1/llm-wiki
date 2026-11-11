---
name: moma-space-list_user_spaces
description: 页面新建时通过固定接口解析目标空间;返回真实 SPACE id 作为后续 space_root / space_id
metadata:
  type: reference
---

# moma moma-space api GET_api_v1_tools_storage_space_list-user-spaces

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

本接口专用于新页面生成、导入、克隆或从素材转页时解析目标 Space。它是这些页面新建场景中目标空间的唯一来源；即使用户已经给出 Space ID 或标题，也必须调用本接口，并从响应中的 space 列表解析真实 ID。已有页面编辑不调用本接口重新默认选择，而是沿用 `node-info` 或 `files_query` 节点结果中的 `spaceId`。

## Recommended Command

固定命令必须原样使用；`pageQuery` 必填，固定查询第一页、每页 100 项：

```bash
moma moma-space api GET_api_v1_tools_storage_space_list-user-spaces \
  --query 'pageQuery={"page_no":1,"page_size":100}' --json
```

不要改用 `GET_api_v1_tools_spaces` 或用于创建空间的 `POST_api_v1_tools_storage_spaces`。不得直接信任外部提供的 ID，不得从标题或其他文本构造 ID。

## Query 参数

| 字段 | 是否必填 | 含义 |
|---|---:|---|
| `pageQuery` | 必填 | JSON 字符串；页面目标空间解析固定为 `{"page_no":1,"page_size":100}` |

## 响应处理

不要假设或编造完整响应 envelope 名称。从响应中的 space 列表按返回顺序处理，每个 space 至少关注：

| 字段 | 用途 |
|---|---|
| 真实 ID | 后续所有 `space_id` / `space_root` 的唯一取值 |
| 标题 | 用户指定标题时做精确匹配 |
| `mode` | 用户未指定 Space 时筛选 `mode == "team"` |

## 目标 Space 匹配算法

1. **用户指定 Space ID：** 只在返回项的真实 ID 中做精确匹配。匹配后仍取该返回项的真实 ID；不得直接采用请求外部的 ID。
2. **用户指定 Space 标题：** 按标题做精确匹配。仅一项匹配时取该返回项的真实 ID；同标题多项时停止并报告，不询问用户选择。
3. **用户未指定 Space：** 按返回顺序过滤 `mode == "team"` 的 space，选择第一项，不询问。
4. 选中后，后续创建工程目录、Database、上传 HTML、写文件等页面操作的 `space_id` / `space_root` 必须始终使用该返回项的真实 ID。

## 停止条件

| 情况 | Agent 处理 |
|---|---|
| space 列表为空 | 停止并报告当前没有可用于页面新建的可见 Space；不得编造 ID |
| 用户指定 ID 未匹配 | 停止并报告指定 Space 不存在或当前账号不可见；不得直接使用该外部 ID |
| 用户指定标题无匹配 | 停止并报告指定标题不存在或当前账号不可见；不得猜测相近标题 |
| 用户指定标题匹配多项 | 停止并报告存在同标题多项；不询问、不取第一项 |
| 用户未指定且没有 `mode == "team"` | 停止并报告没有可用 team space；不询问、不回退个人空间 |
| 登录或权限错误 | 按 `moma-space/SKILL.md` 的认证与权限规则停止处理，不绕过 |

## Notes

- 返回顺序只用于“用户未指定 Space”时选择第一个 `mode == "team"` 的 space；标题重名时不得用顺序消除歧义。
- 标题仅用于映射，不得作为 `space_id` / `space_root`。
- 页面新建后续请求不得省略 `space_id`；`upload-node` 的页面场景必须传选中返回项的真实 ID。
- 已有页面编辑以节点返回的 `spaceId` 为准，不因未给 Space 而运行本接口的默认选择算法。
