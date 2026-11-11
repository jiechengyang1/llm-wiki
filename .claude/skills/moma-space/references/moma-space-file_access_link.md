# moma moma-space api GET_api_v1_tools_file_access-link

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

根据文件 ID 获取可在 MOMA Space 前端打开的文件访问链接。接口只返回访问链接，不返回文件正文，也不用于下载原文件。

## Recommended Command

> **必须添加 `--json`。** 命令里的 apiName 必须是完整 Gateway 名；本 reference 已写清字段时直接 `api`，不要先 `schema`/`list`/`--help`。

```bash
moma moma-space api GET_api_v1_tools_file_access-link --json --query "fileId=<FILE_ID>"
```

## Query 参数

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `fileId` | **必填** | 文件 ID；使用引用元数据或 `GET_api_v1_tools_files_query` 返回的 `file_id` 值 |

- 本接口是 GET，请使用 `--query` / `-q`，不要使用 `--data` / `-d`。
- Gateway 参数名是 camelCase `fileId`，禁止改成 `file_id`。
- `fileId` 必须作为一个完整参数原样传入，不要把文件路径、文件名或 Space ID 当作 `fileId`。

## 响应结构

成功时直接返回 URL 字符串，不是带 `url` 字段的 JSON 对象：

```json
"https://<space-frontend>/<SPACE_ID>?fileId=<FILE_ID>"
```

该 URL 是面向用户的 Space 前端文件访问链接，可以直接展示给用户。不要把它当作文件内容，也不要用它替代 `POST_api_v1_tools_file_presigned_url` 下载原文件。

## Workflow

1. 用户明确要求“文件访问链接 / 文件页面链接 / 在 Space 中打开文件”时使用本接口。
2. 获取文件 ID：
   - 引用元数据已经提供 `file_id` / 文件 ID：直接使用，不再查询。
   - 仅有 `@/kespace/<space>/<relative_path>` 或 Space ID + path：先按 `files_query` 流程确定 Space ID，再调用 `GET_api_v1_tools_files_query` 获取 `file_id`。
   - 只有空间标题时，先用 `GET_api_v1_tools_spaces` 精确映射为 Space ID；重名时让用户选择。
3. 调用本接口并检查 stdout、stderr 与退出码。成功时将返回的 URL 字符串展示给用户。
4. 若用户实际要求下载、读取或解析原文件，不调用本接口；按 [`file_presigned_url`](moma-space-file_presigned_url.md) 流程处理。

## 错误与异常处理

| 情况 | Agent 处理 |
|------|-----------|
| `fileId` 缺失或为空 | 停止并先解析文件 ID，不得用路径或文件名代替 |
| 文件不存在 / 无权访问 | 停止并转述业务错误；无权限时让用户联系 Space 管理员/owner，不重试、不绕过 |
| `NOT_AUTHENTICATED` / 凭据失效 | 按 `moma-space/SKILL.md` 的认证分流提示“第三方插件 → Space → 安装/更新授权”，停止业务调用 |
| 成功响应为空或不是 URL 字符串 | 说明未取得有效访问链接并停止；不要自行拼接前端地址 |

## Notes

- 该接口是只读操作，Gateway schema 的 `risk` 为 `read`，无需 dry-run 或 `--yes`。
- 访问链接与 presigned 下载 URL 用途不同：前者用于用户打开 Space 页面，后者用于 Agent 下载原始文件进行读取或处理。
- 不要手工拼接 Space 前端地址；始终使用接口返回值。
