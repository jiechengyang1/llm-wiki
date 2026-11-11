# moma meeting api GET_api_gateway_meeting-assistant_transcript_records

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

获取指定会议的腾讯会议转写下载链接或转写文本内容。

## Recommended Commands

> **必须添加 `--json`。** 本 Skill 的所有 `moma moma-meeting list/schema/api` 命令都必须添加 `--json`。

```bash
# 查看该 API 参数结构
moma moma-meeting schema GET_api_gateway_meeting-assistant_transcript_records --json

# 获取转写下载链接（includeDownloadUrls=true 返回下载链接）
moma moma-meeting api GET_api_gateway_meeting-assistant_transcript_records --json -q "meetingId=<meetingId>&includeDownloadUrls=true"

# 获取转写文字内容（不加 includeDownloadUrls 默认返回完整转写文本）
moma moma-meeting api GET_api_gateway_meeting-assistant_transcript_records --json -q "meetingId=<meetingId>"
```

## Options

```text
-q, --query <querystring>   追加 query string，格式：key1=v1&key2=v2
```

query 参数：

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `meetingId` | **必填** | 会议实例 ID，通常来自会议列表返回值 |
| `includeDownloadUrls` | 可选 | `true` 返回下载链接格式；`false`（默认）返回转写文字内容 |

## 响应格式

所有响应使用统一信封格式，判断 `errno` 决定业务状态：

### 成功（errno=0）— 默认模式（纯文本，includeDownloadUrls=false）
`data` 为转写完整文字内容（String）：

```json
{
  "errno": 0,
  "errmsg": "成功",
  "data": "转写文字内容..."
}
```

### 成功（errno=0）— 下载链接模式（includeDownloadUrls=true）
`data` 为 MomaTranscriptionResp 对象：

```json
{
  "errno": 0,
  "errmsg": "成功",
  "data": {
    "meetingId": "会议实例ID",
    "status": "READY",
    "version": "latest",
    "downloadUrls": ["https://..."],
    "hint": null,
    "retryable": null
  }
}
```

| data 字段 | 含义 |
|-----------|------|
| `meetingId` | 会议实例 ID |
| `status` | 转写状态：`READY`（已就绪）、`EMPTY`（暂无） |
| `version` | 版本号 |
| `downloadUrls` | 腾讯会议转写下载链接列表（Array） |

> `status=READY` 有下载链接；`status=EMPTY` 或 `downloadUrls` 为空数组，表示暂无可用转写。

### 无转写记录（errno=40402）

当会议没有生成转写时，无论文本模式还是下载链接模式，均返回此错误码：

```json
{
  "errno": 40402,
  "errmsg": "当前会议暂无转写记录",
  "hint": "当前会议暂无转写记录",
  "retryable": false,
  "data": null
}
```

| 字段 | 值 | 含义 |
|------|-----|------|
| `errno` | `40402` | 无转写记录 |
| `errmsg` | "当前会议暂无转写记录" | 用户可见消息 |
| `hint` | "当前会议暂无转写记录" | Agent 指引 |
| `retryable` | `false` | 重试无意义，不要再请求转写 |
| `data` | `null` | 无业务数据 |

> **Agent 处理**：收到 `errno=40402` 时，明确告知用户"该会议暂无转写记录"，不要再请求该会议的任何转写内容或下载链接。

### 权限不足（errno=40301）

```json
{
  "errno": 40301,
  "errmsg": "无权限访问会议内容",
  "hint": "当前用户没有该会议会后内容查看权限，请让用户申请权限或联系会议组织者；不要重试或伪造他人身份。",
  "retryable": false,
  "data": null
}
```

> **Agent 处理**：告知用户无权限，建议联系会议组织者申请权限，不要重试。

## Agent 对不同 errno 的响应规则

| errno | 含义 | Agent 行为 |
|-------|------|-----------|
| `0` | 成功 | 按业务逻辑处理 data |
| `40001` | 参数错误 | 检查参数（meetingId 是否传入等），修正后重新调用 |
| `40301` | 权限不足 | 告知用户无权限，建议联系组织者，不重试 |
| `40402` | 暂无转写记录 | 告知用户该会议暂无转写记录，不重试 |
| `50001` | 服务不可用 | 告知用户服务暂不可用，稍后重试（retryable=true） |

## Workflow

1. 确认目标会议 ID；如果用户没有提供，先查询会议列表。
2. 如参数不明确，先执行 `moma moma-meeting schema GET_api_gateway_meeting-assistant_transcript_records --json`。
3. 执行命令。
4. 判断 `errno`：
   - **`errno=0`**：成功，按业务逻辑处理：
     - 文本模式：`data` 为转写文字，展示给用户。
     - 下载链接模式：检查 `data.status`，`READY` 则展示下载链接；`EMPTY` 说明暂无可用转写。
   - **`errno=40402`**：告知用户"当前会议暂无转写记录"。
   - **`errno=40301`**：告知用户无权限。
   - **`errno=50001`**：告知用户服务暂不可用，稍后重试。

## Notes

- 该接口返回的下载链接是腾讯会议转写下载链接，不是逐字稿正文。
- 业务服务内部会使用会议 host 或 creator 查询腾讯会议转写；Agent 不需要也不能传入腾讯会议 operator 信息。
- 当前用户必须具备该会议会后查看权限，权限不足返回 `errno=40301`。
- 错误响应中的 `hint` 和 `retryable` 字段指导 Agent 下一步操作：`hint` 是下一步建议，`retryable` 指示是否应重试。
