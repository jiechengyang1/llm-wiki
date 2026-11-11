# moma moma-space api POST_api_v1_tools_file_presigned_url

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

为指定文件返回一个 presigned S3 GET URL，Agent 凭此 URL 直接下载文件原始内容。适用于所有文件类型（文本、图片、PDF、Office 等）。

> **注意：** 服务端需配置 S3 presign 能力；未配置时返回错误。

## Recommended Commands

先调用接口获取 presigned URL 并保存响应，再提取 `url` 字段用 curl 下载文件。curl 失败时（如代理返回 400 等错误），改用 `scripts/download_file.sh` 中的 urllib 方案。

```bash
mkdir -p /tmp/.moma-tmp && moma moma-space api POST_api_v1_tools_file_presigned_url --json --data '{"filepath":"docs/report.pdf","space_root":"<SPACE_root>","task_id":"<TASK>"}' > /tmp/.moma-tmp/resp.json
URL=$(python3 -c "import sys,json; print(json.load(sys.stdin)['url'])" < /tmp/.moma-tmp/resp.json) && curl -sSfL -o "/tmp/.moma-tmp/report.pdf" "$URL"
```

## Request Body

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `filepath` | **必填** | 文件相对路径；无前导 `/`；无 `@/kespace` 前缀 |
| `space_root` | **必填** | SPACE id |
| `task_id` | **必填** | MomaAgent 使用本轮 prompt 的 mint id；Claude Code 仅有文本远端引用且未给 id 时，生成一个短 id 并全轮复用 |

## POST_api_v1_tools_file_presigned_url的响应结构

```json
{
  "success": true,
  "url": "https://moma.ke.com/kespace/storage/proxy/...?AWSAccessKeyId=...&Signature=...&Expires=...",
  "bucket": "<bucket-name>",
  "key": "<object-key>",
  "expires_in": 604800
}
```

| 字段 | 含义 |
|------|------|
| `success` | 是否成功 |
| `url` | presigned S3 GET URL；在 `expires_in` 秒内有效，凭此直接 GET 下载 |
| `bucket` | S3 bucket 名称（仅供参考，无需手动使用） |
| `key` | S3 对象 key（仅供参考） |
| `expires_in` | URL 有效期（秒），通常为 604800（7 天） |

## Workflow

### 通用下载流程

1. 调用 `POST_api_v1_tools_file_presigned_url` 获取 `url`，并通过管道直接下载到本地。
2. 根据文件类型处理内容：
   - **文本文件**（`.md`、`.txt`、`.csv`、`.json` 等）：用 Read 工具直接读取下载后的本地文件。
   - **图片**（`.png`、`.jpg`、`.webp` 等）：用 Read 工具视觉读取本地文件。
   - **PDF**：用 Read 工具读取本地文件（支持多页视觉读取）。
   - **Office 文档**（`.xlsx`、`.docx`、`.pptx` 等）：下载后根据需要用合适工具处理。
3. 处理完成后删除本地临时文件，不得长期保留。

### 下载目录规范

- 临时文件必须存放于 `/tmp/.moma-tmp/`；目录不存在时先 `mkdir -p` 创建。
- 文件名使用原始文件名或加短随机后缀，避免冲突。
- 每次任务完成后立即删除下载的临时文件。

### 清理前二次检查

删除前必须确认以下两点，任一不满足则停止删除并告知用户：

1. **路径前缀**：目标路径必须以 `/tmp/.moma-tmp/` 开头；禁止删除该目录之外的任何文件。
2. **文件来源**：仅删除本轮任务中由 `file_presigned_url` 下载的文件；禁止删除目录下其他文件。

```bash
# 正确示例：删除前先确认路径
TARGET="/tmp/.moma-tmp/report.pdf"
if [[ "$TARGET" == /tmp/.moma-tmp/* ]]; then
  rm "$TARGET"
else
  echo "路径异常，拒绝删除：$TARGET"
fi
```

## 错误响应

| code | 含义 | Agent 处理 |
|------|------|-----------|
| `FILE_NOT_FOUND` | 文件不存在 | 检查相对路径 / SPACE id；必要时 `files_children` 或 `search_files` |
| `PERMISSION_DENIED` | 无读权限（终局） | **停止，不重试**；告知找管理员/owner |
| `PATH_TRAVERSAL_BLOCKED` | 路径越界 | 改用相对路径，勿带绝对路径或 `..` |
| `S3_PRESIGN_NOT_CONFIGURED` | 服务端未配置 presign | 停止并告知用户，不重试 |
| `NOT_AUTHENTICATED` / 凭据失效 | 未登录或 token 过期 | 提示"第三方插件 → Space → 安装/更新授权"；停止业务调用 |

## Notes

- **curl 失败时 fallback 到 `urllib`**：Step 1 的 curl 下载遇到任何错误（400、网络问题等），直接执行 Step 2 的 urllib 方案，无需判断具体错误类型。
- presigned URL 本身包含鉴权参数，**禁止**将完整 URL 打印到聊天上下文或日志中（可能含敏感签名信息）。
- URL 有效期内（`expires_in` 秒）可直接使用，无需额外鉴权头。
- 此接口只负责生成下载 URL，不做内容解析；文件内容处理由下载后的本地工具完成。
- `filepath` 不要带前导 `/`；空间解析规则与其他文件类 API 一致。
- 禁止把下载的临时文件当持久副本或上传到其他服务。
