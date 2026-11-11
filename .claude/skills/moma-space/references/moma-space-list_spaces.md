---
name: moma-space-list_spaces
description: 列出当前登录用户可访问的知识空间;返回 SPACE id 作为后续读写操作的 space_root / space_id
metadata:
  type: reference
---

# moma moma-space api GET_api_v1_tools_spaces

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

列出当前登录用户可访问的知识空间（KnowledgeSpace）。返回的 **SPACE id** 是后续所有读写操作的 `space_root` / `space_id`。

> **页面场景例外：** 新页面生成、导入、克隆或从素材转页时，目标 Space **只能**按 [`moma-space-list_user_spaces.md`](moma-space-list_user_spaces.md) 调用固定 `GET_api_v1_tools_storage_space_list-user-spaces` 并解析；禁止用本接口或 `POST_api_v1_tools_storage_spaces`。已有页面编辑沿用节点返回的 `spaceId`。本 reference 仅描述非页面场景的通用列空间能力。

## Recommended Commands

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

```bash
# 列出可访问空间
moma moma-space api GET_api_v1_tools_spaces --json

# 按关系过滤（可选）
moma moma-space api GET_api_v1_tools_spaces --json --query "relation=owner"
```

仅当 CLI 返回 unknown api 时，允许一次 `moma moma-space list --json` 排障。

## Options

```text
--query <querystring>   GET query，格式：key1=v1&key2=v2
--data <json-string>    本 API 为 GET，不要用 --data
```

query 参数：

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `relation` | 可选 | 按 RELATION 过滤：`personal` / `owner` / `admin` / `member` / `worker` / `other` |

## 响应结构

成功时返回空间列表（形态以 CLI 当前返回为准）。Agent 必须从中提取：

| 字段 | 含义 |
|------|------|
| SPACE id（首列 / `id` / `space_id`） | **后续所有 API 的 `space_root` / `space_id`** |
| TITLE / `title` / `name` | 展示名；仅用于映射，不要当 space_root |
| OWNER | 空间所有者 |
| RELATION | 当前用户与空间的关系 |

`RELATION=other` 可表示当前用户以无成员角色的访客身份读取 `plaza`
公共空间；它不等于无权限。是否可操作应以 API 的 RBAC 结果为准，
其中 plaza 访客仅可读，不能修改正式 Space 文件。

### 成功响应示例（示意）

```json
{
  "spaces": [
    {
      "id": "space-xxxxxxxx",
      "title": "团队文档",
      "relation": "owner"
    }
  ]
}
```

若 CLI 返回表格文本，取 **第一列 SPACE id**，不要用标题列。

### 错误响应

| code / 情况 | 含义 | Agent 处理 |
|-------------|------|-----------|
| `NOT_AUTHENTICATED` / `MOMA_TOKEN_INVALID` / 凭据 missing、expired / Gateway auth failure | 登录态不可用 | `@/kespace` 或 Space 元数据场景按 `moma-space/SKILL.md` 的认证分流提示“第三方插件 → Space → 安装/更新授权”；停止业务 API，不要求终端登录 |
| `PERMISSION_DENIED` | 无权限（少见，列表本身已过滤） | 转述错误，不重试、不绕过 |
| 空列表 | 当前用户无可读空间 | 告知用户；不要编造 SPACE id |

## Workflow（仅非页面场景）

以下 workflow 仅用于非页面场景。页面新建目标 Space 改用 [`moma-space-list_user_spaces.md`](moma-space-list_user_spaces.md)；已有页面编辑沿用节点返回的 `spaceId`。

1. 非页面任务中，用户提到共享知识库 / `@/kespace/<标题>/...` / 未给出 SPACE id 时，**先**调用本 API。
2. 用用户说的标题/昵称在结果中映射 SPACE id：
   - 唯一命中 → 使用该 id。
   - 多个命中 → 列出候选让用户选择。
   - 无命中 → 说明当前账号看不到该空间，请用户确认名称或申请权限。
   - 上下文已经给出 Space ID → 直接使用，不再按标题重新映射。
3. 后续 `file_presigned_url` / `write_*` / `search_files` 等一律传 SPACE id。
4. 不要尝试用 `execute_command`、SQL、或其它环境变量去查「别人的空间」。

## Notes

- `space_root` 与 upload/delete 的 `space_id` 取值相同，都是 SPACE id。
- 标题、昵称、别名、用户口头空间名 **都不能** 直接当 `space_root`，除非它与 SPACE id 列完全一致。
- 本接口只能看到当前登录用户有权限的空间。
- 创建空间用 `POST_api_v1_tools_storage_spaces`，**不要**用它列空间。
