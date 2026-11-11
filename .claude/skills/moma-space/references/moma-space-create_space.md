# moma moma-space api POST_api_v1_tools_storage_spaces

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

创建一个新的知识空间（团队空间或个人空间）。成功后直接返回新空间的完整详情，形状与 [`list_spaces`](moma-space-list_spaces.md)
单条空间记录一致，**snake_case** 字段（`tags[]` 内部元素除外，见下）。

这是**持久化写操作**，会新建一条空间记录并把当前登录用户写成该空间的 `admin`；必须遵守 `moma-shared`
的高风险写审批协议（`--dry-run` → 展示预览 → 明确确认 → `--yes`），具体 `risk` 级别以
`moma moma-space schema POST_api_v1_tools_storage_spaces --json` 返回为准，不要自行假设。

## Recommended Commands

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；决策树短名不能直接当 api 参数。本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`（首次调用前仍需按 `moma-shared` 先跑一次 `moma moma-space list --json` 核对该 apiName 确实存在）。

```bash
# 建团队空间：先 dry-run 预览
moma moma-space api POST_api_v1_tools_storage_spaces --json --dry-run --data '{
  "name":"算法组资料库",
  "description":"组内共享资料",
  "space_type":"public",
  "space_category":"default"
}'

# 用户明确确认后
moma moma-space api POST_api_v1_tools_storage_spaces --json --yes --data '{
  "name":"算法组资料库",
  "description":"组内共享资料",
  "space_type":"public",
  "space_category":"default"
}'

# 带业务标签（tags[] 内部字段是 camelCase，不随外层转 snake_case）
moma moma-space api POST_api_v1_tools_storage_spaces --json --dry-run --data '{
  "name":"算法组资料库",
  "space_type":"public",
  "tags":[{"tag":"house","relBizKey":"abc123"}]
}'
```

## Options

```text
--data <json-string>   POST JSON body
--dry-run              预览本次创建（新空间名称、类型等）
--yes                  用户明确确认后执行
```

### body 参数（JSON，snake_case）

| 字段 | 是否必填 | 默认值 | 含义 |
|------|---------|--------|------|
| `name` | **必填** | - | 空间名称，1~255 字符 |
| `description` | 可选 | `null` | 空间描述；传空串原样存空，不会补默认文案 |
| `space_type` | 可选 | `public` | `personal` / `public` / `plaza`（`plaza` 已弃用，等同 `public`）。传 `personal` 建个人空间，其余（含空白）建团队空间 |
| `space_category` | 可选 | `default` | `default` / `executive` / `appraisal` / `app` / `moma_video`。**只有 `default` 能发布**，其余类型建出来发不出去 |
| `tags` | 可选 | `null` | 业务标签数组，见下；只有创建接口收这个字段 |

`tags[]` 元素（**这层字段是 camelCase**）：

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `tag` | **必填** | `house`（房源）/ `customer`（客源） |
| `relBizKey` | 可选 | 关联业务 key，最长 64 字符 |

## 响应结构

`201`，直接返回新空间详情：

| 字段 | 含义 |
|------|------|
| `id` | 空间 id，即后续所有操作的 `space_root` / `space_id` |
| `title` | 空间名称（对应入参 `name`） |
| `description` | 空间描述 |
| `owner` / `usercode` | 所有者展示名 / 工号（当前登录用户） |
| `created_at` | 创建时间，`yyyy-MM-dd HH:mm:ss`，不是 ISO-8601 |
| `space_type` | `personal` / `team`（由入参 `space_type` 映射而来） |
| `members` / `admins` | 成员 / 管理员列表；创建者作为 `admin` 出现在 `admins` 里 |
| `workers` / `line_leaders` / `center_leaders` / `department_leaders` / `team_leaders` / `hrbps` | 恒为空数组 |
| `readable` / `editable` / `deletable` / `addable` / `downloadable` | 当前操作人对该空间的权限位 |
| `is_executive` / `is_published` / `is_review_space` | 是否高管 / 已发布（创建后恒 `false`） / 评审空间 |
| `subscriber_count` / `is_subscribed_by_me` | 恒为 `0` / `false` |
| `kind` | `personal_moma` / `project` |

### 成功响应示例

```json
{
  "id": "sp_123",
  "title": "算法组资料库",
  "description": "组内共享资料",
  "owner": "张三 (zhangsan)",
  "usercode": "zhangsan",
  "created_at": "2026-09-17 10:00:00",
  "state": 1,
  "space_type": "team",
  "members": [],
  "admins": [
    { "id": 1, "space_id": "sp_123", "user": "张三 (zhangsan)", "usercode": "zhangsan", "state": 1, "role": "admin", "scope_folder_id": "" }
  ],
  "workers": [], "line_leaders": [], "center_leaders": [], "department_leaders": [], "team_leaders": [], "hrbps": [],
  "readable": true, "editable": true, "deletable": true, "addable": true, "downloadable": true,
  "secret_level": "low",
  "is_executive": false,
  "is_published": false,
  "is_review_space": false,
  "subscriber_count": 0,
  "is_subscribed_by_me": false,
  "kind": "project"
}
```

新空间的 `id` 之后可直接作为 `space_root` / `space_id` / `space_ids` 使用，无需再调 `list_spaces` 映射。

### 错误响应

| code / 场景 | 含义 | Agent 处理 |
|------|------|-----------|
| `GATEWAY_CONFIRMATION_REQUIRED` | 需确认（exit 10） | 按 `moma-shared`：dry-run → 展示 → 明确同意 → `--yes` |
| `name` 未传或空白 | 校验失败 | 提示用户补充空间名称，不得代填 |
| `name` 超过 255 字符 | 校验失败 | 提示用户精简名称 |
| `space_type` 传了但不是 `personal`/`public`/`plaza` | 校验失败 | 更正取值后重试 |
| `space_category` 传了但不合法 | 校验失败 | 更正为 `default`/`executive`/`appraisal`/`app`/`moma_video` |
| `tags[].tag` 不是 `house`/`customer` | 校验失败 | 更正标签取值 |
| `tags[].relBizKey` 超过 64 字符 | 校验失败 | 精简后重试 |
| `PERMISSION_DENIED` / 账号已离职 | 鉴权侧拒绝 | **停止，不重试**；提示用户核对账号状态 |

## Workflow

1. 创建前向用户确认：空间名称、`space_type`（个人 / 团队）、是否需要设置 `space_category`（默认空间才能发布）、是否需要 `tags`。不得替用户默认猜测名称。
2. `--dry-run` 展示将创建的空间名称、类型、分类，获得用户明确同意后再加 `--yes`；「好的/你弄吧」不算确认。
3. 若用户后续改了任何 body 字段（比如换了名字），原确认失效，重新 dry-run。
4. 创建成功后，把响应里的 `id` 记下来作为该空间后续所有读写操作的 `space_root` / `space_id`，不要再拿 `title` 去做模糊匹配。
5. 需要发布空间时，先确认 `space_category` 是否为 `default`；非 `default` 分类建出来无法发布，需提示用户或重新创建。

## Notes

- 操作人身份（对应业务接口的 `ke-user-id`）由网关根据登录态自动注入，Agent 不需要、也不应尝试自行拼接该请求头。
- `admins` / `members` / `is_executive` 作为入参**不接受**：创建接口不收这些字段，成员授权只会写入创建者一条 `admin` 记录；高管空间改走 `space_category`。
- `tags` 在空间建完之后单独落库；标签写入失败不代表空间创建失败，若怀疑标签未生效可用 `files_query` / 后续管理面接口核实，不要重复调用本接口重建空间。
- 本接口建的是团队 / 个人知识空间，与文件夹层级的 `write_file` / `upload_batch` 无关，不要混用。
