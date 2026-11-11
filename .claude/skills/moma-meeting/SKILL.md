---
name: moma-meeting
version: 1.3.0
description: "MOMA meeting：会议助手开放能力，支持查询本人会议、获取会议转写下载链接、获取智能纪要、申请会议纪要权限。当用户需要查会议列表、拿会议转写、读取会议纪要或申请查看权限时使用。"
metadata:
  requires:
    bins: ["moma"]
  cliHelp: "moma --help"
---

# 会议助手

**CRITICAL — 本 Skill 的 `<service>` 固定为 `moma-meeting`。所有命令必须使用 `moma moma-meeting ...`。**
**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../moma-shared/SKILL.md`](../moma-shared/SKILL.md)，其中包含登录、权限处理、更新和安全规则**

## 快速决策

- 用户要查询自己一段时间内的会议、按标题/主持人/状态筛选会议 → 使用 `moma moma-meeting api GET_api_gateway_meeting-assistant_meeting_search --json`（注意 `meetingType` 必填）
- 用户要获取某个会议的转写文本或转写下载链接 → 使用 `moma moma-meeting api GET_api_gateway_meeting-assistant_transcript_records --json`
- 用户要获取某个会议的智能纪要、会议总结、会议摘要 → 使用 `moma moma-meeting api GET_api_gateway_meeting-assistant_materials_infos --json`（需加 `includeSmartSummary=true`）
- 用户要获取会议的材料和基本信息 → 使用 `moma moma-meeting api GET_api_gateway_meeting-assistant_materials_infos --json`
- 用户查看会议纪要或转写时遇到无权限提示，经用户确认后需要申请权限 → 使用 `moma moma-meeting api POST_api_gateway_meeting-assistant_summary_permission_application --json`，传入 `meetingInstanceId` 和 `applicationReason`
- 如果用户只说"我的会议"但没有时间范围，默认先查询近期会议（meetingType=4）；如用户需要精确范围，先确认开始和结束时间。
- 如果用户要获取转写或纪要但没有给会议 ID，先查询会议列表，让用户确认目标会议。
- 如果用户查看会议纪要时提示无权限（40301），经用户确认后可调用申请会议纪要权限接口提交审批。
- **写入类限制**：本 Skill 当前仅包含读取和权限申请两类能力。申请会议纪要权限是写入操作，执行前必须先确认用户意图。不包含删除、同步、审批或发送操作。

## 核心概念

- **当前用户**：由 Moma CLI 登录态和 gateway 注入的当前员工身份决定；业务 Skill 不手工拼接 `X-Moma-CLI-UCID` 或其它鉴权头。
- **会议 ID**：会议实例 ID，用于获取转写和智能纪要；通常来自会议列表返回的 `meetingId`。
- **会议类型（meetingType）**：**必填参数**，决定了查询的会议范围：
  - `1` = 进行中（正在进行的会议）
  - `2` = 未开始（尚未开始的预约会议）
  - `3` = 历史（已结束的会议）
  - `4` = 近期会议（进行中 + 未开始的合集）
  - `5` = 取消（已取消的会议）
  - > 查询上周/上月的会议，请使用 `meetingType=3`（历史）。
- **会议状态**：会议列表中的 `meetingStatus` 表示会议进度，`1=会议中`、`2=未开始`、`3=会议结束`；`meetingStatusName` 是对应中文名。
- **转写可用性**：会议列表中的 `hasTranscription` 只表示转写内容已生成，不代表当前用户一定有查看权限。
- **纪要可用性**：会议列表中的 `hasSmartSummary` 只表示智能纪要已生成，不代表当前用户一定有查看权限。
- **转写下载链接**：转写接口（`transcript_records`）在 `includeDownloadUrls=true` 时返回腾讯会议转写下载链接列表 `downloadUrls`，不是直接返回逐字稿正文。

## 业务规则

- **`meetingType` 是必填参数**，查询时必须传入，不可省略。
- 查询会议列表时，单次时间范围最大 90 天；不要为了"近一年"等大范围请求直接一次性查询。
- 时间字段 `startTime`、`endTime` 必须作为 GET query 的顶层参数传入，使用秒级或毫秒级 Unix 时间戳；不要包成 `req` 对象、不要用 JSON body、不要手工拼业务 URL。
- 单日查询必须按北京时间 `Asia/Shanghai` 计算当天边界：`startTime=当天 00:00:00`，`endTime=次日 00:00:00 - 1 秒`。例如查询 2026-06-04，应使用秒级 `startTime=1780502400&endTime=1780588799`，或毫秒级 `startTime=1780502400000&endTime=1780588799000`。
- 查询会议列表支持分页，默认页码通常从 1 开始；`pageSize` 最大 100。
- 查询会议列表按会议开始时间排序，`sortOrder` 可使用 `asc` 或 `desc`。
- 获取转写和获取智能纪要都会实时校验当前用户对会议的会后查看权限；列表中的存在标记不能替代权限校验。
- 无权限时只转述 CLI 返回的非敏感错误信息，不猜测权限模型，也不建议绕过权限。
- 转写接口内部由业务服务使用会议 host 或 creator 调腾讯会议获取下载链接，调用方不需要也不应该传入腾讯会议 operator 信息。
- **权限申请**：申请会议纪要权限时，必须传入 `meetingInstanceId`（会议实例ID），可选传入 `applicationReason`（申请原因）。申请通过后需等待管理员审批，不能即时生效。
- **写入操作**：申请会议纪要权限是写入操作，执行前必须先确认用户意图；不要未经用户确认就自动提交申请。

## 命令

优先使用已封装的 `moma` CLI 业务命令。本 Skill 的所有 `moma moma-meeting list/schema/api` 命令都必须添加 `--json`。

```bash
# 查看服务已接入 API（重要：先执行此命令确认可用 API）
moma moma-meeting list --json

# 查看各 API 参数结构
moma moma-meeting schema GET_api_gateway_meeting-assistant_meeting_search --json
moma moma-meeting schema GET_api_gateway_meeting-assistant_transcript_records --json
moma moma-meeting schema GET_api_gateway_meeting-assistant_materials_infos --json
moma moma-meeting schema POST_api_gateway_meeting-assistant_summary_permission_application --json

# 查询会议列表（meetingType 必填）
moma moma-meeting api GET_api_gateway_meeting-assistant_meeting_search --json -q "meetingType=<1-5>&startTime=<timestamp>&endTime=<timestamp>&pageNum=1&pageSize=100&sortOrder=desc&keyword=<keyword>&host=<host>"

# 获取转写内容或下载链接
moma moma-meeting api GET_api_gateway_meeting-assistant_transcript_records --json -q "meetingId=<meetingId>&includeDownloadUrls=true"

# 获取会议材料和信息（可同时获取智能纪要）
moma moma-meeting api GET_api_gateway_meeting-assistant_materials_infos --json -q "meetingInstanceIds=<meetingId>&includeSmartSummary=true"

# 申请会议纪要权限
moma moma-meeting api POST_api_gateway_meeting-assistant_summary_permission_application --json -d '{"meetingInstanceId":"<meetingId>","applicationReason":"<申请原因>"}'
```

> **重要**：调用前必须先使用 `list` / `schema` 确认可用 API 和参数结构，不要直接根据 Swagger、operationId、path 或记忆拼命令。若 `list` 中展示的 apiName 与本文不同，以 CLI 返回为准。

## 工作流

### 查询本人会议

1. 确认用户要查询的 **meetingType**（会议类型）、时间范围、关键词、主持人、状态和分页要求。
2. 如果用户给的是自然语言日期，例如"六月四号"，先换算成北京时间当天的 `startTime/endTime`。
3. 如命令、参数或返回结构不明确，先执行 `moma moma-meeting list --json` 和 `moma moma-meeting schema GET_api_gateway_meeting-assistant_meeting_search --json`。
4. 执行查询命令；**`meetingType` 必须传入**，时间范围不能超过 90 天，页大小不能超过 100。query 必须使用顶层参数，例如 `-q "meetingType=3&startTime=1780502400&endTime=1780588799&pageNum=1&pageSize=100&sortOrder=asc"`。
5. 如果返回结果明显超出请求时间范围，不要直接对默认结果做本地过滤；应先检查是否误用了 `meetingType`、`req=`、`-d`、未加引号的 `&`，然后用正确引用的 `-q` 重试。
6. 输出会议标题、会议 ID、会议时间、主持人、会议状态、是否已有转写、是否已有智能纪要。
7. 如果用户后续要查看转写或纪要，保留并复用目标会议的 `meetingId`。

### 获取会议转写记录

1. 确认目标 `meetingId`；如果用户没有提供，先查询会议列表。
2. 如参数结构不明确，先执行 `moma moma-meeting schema GET_api_gateway_meeting-assistant_transcript_records --json`。
3. 执行读取命令，传入 `meetingId` 参数：
   - 默认返回转写文字内容（文本格式）
   - 加 `includeDownloadUrls=true` 返回下载链接列表格式
4. 如果返回 `status=READY`，输出 `downloadUrls`；如果返回 `EMPTY` 或无链接，明确说明暂无可用转写。
5. 如果返回权限不足，按 `moma-shared` 的权限处理规则转述，不推测或绕过。

### 获取会议材料与智能纪要

1. 确认目标 `meetingId`；如果用户没有提供，先查询会议列表。
2. 如参数结构不明确，先执行 `moma moma-meeting schema GET_api_gateway_meeting-assistant_materials_infos --json`。
3. 执行读取命令，传入 `meetingInstanceIds=<meetingId>`。
4. 如需同时获取智能纪要，加 `includeSmartSummary=true`。
5. 输出材料列表（如果有）、纪要标题、生成状态、版本和正文摘要；如用户明确要求完整纪要，可返回完整 `content`，但避免泄露无关敏感信息。
6. 如果返回权限不足或服务异常，按 CLI 返回内容处理，不伪造纪要。

### 申请会议纪要权限

1. 确认场景：用户尝试查看会议转写或智能纪要时返回 `errno=40301`（无权限），或用户明确要求申请查看某个会议纪要的权限。
2. **必须先与用户确认**：告知用户需要申请该会议的纪要查看权限，说明申请后会通知会议组织者审批，确认用户同意后再执行。
3. 确认目标 `meetingId`；如果用户没有提供，先查询会议列表让用户选择。
4. 确认申请原因（可选）：如果用户没有提供原因，可以不传；如有明确原因（如"需要参考会议内容"）则传入。
5. 如参数结构不明确，先执行 `moma moma-meeting schema POST_api_gateway_meeting-assistant_summary_permission_application --json`。
6. 执行提交命令，使用 `-d` 传入 JSON body：
   ```bash
   moma moma-meeting api POST_api_gateway_meeting-assistant_summary_permission_application --json -d '{"meetingInstanceId":"7409534133326162298","applicationReason":"需要查看会议纪要"}'
   ```
7. 判断响应：
   - **成功（errno=0）**：告知用户权限申请已提交，等待管理员审批。
   - **会议不存在（errno=40002）**：检查 `meetingInstanceId` 是否正确，会议可能已删除，修正后重试。
   - **无法获取主持人（errno=50002）**：告知用户该会议没有有效的主持人，建议联系管理员；不要重试。
   - **权限申请失败（errno=50003）**：告知用户消息服务异常，可稍后重试。
   - **服务异常（errno=50001）**：告知用户服务暂不可用，稍后重试。
8. 注意：权限申请提交后不等同于即时获得权限，需要等待会议组织者或管理员审批。

## 权限与错误处理

所有响应均采用统一格式：

```json
{
  "errno": 0,          // 业务状态码，0 表示成功
  "errmsg": "成功",     // 给用户的消息
  "hint": null,         // 给 Agent 的纠错建议（仅错误时有值）
  "retryable": null,    // 是否可重试（仅错误时有值）
  "data": { ... }       // 业务数据
}
```

### 错误码对照表

| errno | 含义 | hint（Agent 下一步操作指引） | retryable | Agent 处理方式 |
|-------|------|----------------------------|-----------|---------------|
| `40001` | 参数错误 | 请检查必填参数、时间戳单位、时间范围是否不超过90天，以及pageSize是否不超过100；修正参数后重新调用。 | `false` | 检查参数是否正确传入（meetingType 是否缺少、时间戳单位、时间范围是否超 90 天），修正后重试 |
| `40002` | 会议不存在或已删除 | 请检查传入的 meetingInstanceId 是否正确且有效；当前会议可能已被删除或尚未创建。修正参数后重新调用。 | `false` | 告知用户会议不存在，检查 meetingInstanceId 是否正确，修正后重试 |
| `40301` | 无权限访问会议内容 | 当前用户没有该会议会后内容查看权限，请让用户申请权限或联系会议组织者；不要重试或伪造他人身份。 | `false` | 告知用户无权限，建议联系会议组织者申请权限，不要重试 |
| `40402` | 当前会议暂无转写记录 | 当前会议暂无转写记录 | `false` | 明确告知用户该会议暂无转写记录，不要再请求转写内容 |
| `50001` | 服务暂不可用 | 会议、权限或腾讯会议下游服务暂时不可用，请稍后重试；如果持续失败，携带接口名、会议ID或时间范围联系会议助手服务负责人排查。 | `true` | 告知用户服务暂时不可用，稍后可以重试 |
| `50002` | 无法获取会议主持人信息 | 当前会议没有有效的主持人信息，无法发送审批通知；请确认会议已配置主持人后重新申请。不要用相同参数重试。 | `false` | 告知用户该会议没有有效的主持人信息，建议联系管理员确认会议配置 |
| `50003` | 申请会议纪要权限失败 | 企微消息服务暂时不可用或配置异常，无法发送审批通知；请稍后重试。如果持续失败，联系管理员确认企微消息配置。 | `true` | 告知用户消息服务异常，稍后可以重试；如果持续失败建议联系管理员 |

### Agent 对错误码的通用处理原则

- **`errno=0`**：请求成功，`data` 为业务数据；按对应接口的响应结构解析即可。
- **`errno=40001`**：Agent 应检查传入的参数是否正确，修正后重新调用。
- **`errno=40002`**：Agent 应告知用户会议不存在或已删除，检查 meetingInstanceId 是否正确，修正后重新调用。
- **`errno=40301`**：Agent 应告知用户权限不足，不要再请求该会议的内容。**不要**猜测权限模型、伪造身份或尝试绕过。
- **`errno=40402`**：仅在转写记录接口返回。Agent 应告知用户"当前会议暂无转写记录"，不要再请求转写内容或下载链接。
- **`errno=50001`** 且 **`retryable=true`**：Agent 应告知用户服务暂时不可用，稍后可以重试。不要立即重试同一请求（避免放大下游压力），也不要连续多次重试。
- **`errno=50002`**：仅申请会议纪要权限接口返回。Agent 应告知用户该会议没有有效的主持人信息，无法发送审批通知，建议联系管理员确认会议配置。
- **`errno=50003`** 且 **`retryable=true`**：仅申请会议纪要权限接口返回。Agent 应告知用户企微消息服务异常，请稍后重试。
- 如果 `hint` 字段有值，Agent 应优先参考 `hint` 内容指导下一步操作。

### 通用错误汇总

| 情况 | 处理方式 |
|------|----------|
| 未登录 / 凭据失效 | 按 `moma-shared` 引导 `moma login` |
| errno=40001 参数错误 | 检查 meetingType 是否传入、时间戳格式、时间范围是否超 90 天、pageSize 是否超 100 |
| errno=40002 会议不存在 | 检查 meetingInstanceId 是否正确，告知用户会议不存在或已删除 |
| errno=40301 权限不足 | 转述 hint 内容，告知用户联系会议组织者申请权限 |
| errno=40402 无转写记录 | 明确告知用户该会议暂无转写记录 |
| errno=50001 服务不可用 | 告知用户服务暂不可用，稍后重试（`retryable=true`） |
| errno=50002 无法获取主持人 | 告知用户该会议没有有效的主持人信息，建议联系管理员 |
| errno=50003 权限申请失败 | 告知用户消息服务异常，稍后重试（`retryable=true`） |
| 时间范围过大 | 提醒单次查询最大 90 天，建议拆分时间范围 |
| 业务服务不可用 | 说明当前只能确认服务不可用或调用失败，给出 CLI 返回的错误摘要 |

## 安全规则

- 不输出 Moma API Key、AccessToken、RefreshToken、完整 Authorization 头或其它敏感凭据。
- 不手工拼接鉴权头。
- 不直接调用业务服务 Swagger URL 或业务域名；尚未接入 `moma` CLI 的能力只标记为待接入，不写成可执行命令。
- **申请会议纪要权限是写入操作**，Agent 不得在用户未明确确认的情况下自动调用该接口。必须先告知用户申请后需等待审批，获得用户同意后再操作。

## References

- [查询本人会议](references/moma-meeting-GET_api_gateway_meeting-assistant_meeting_search.md)
- [获取会议转写记录](references/moma-meeting-GET_api_gateway_meeting-assistant_transcript_records.md)
- [获取会议材料与智能纪要](references/moma-meeting-GET_api_gateway_meeting-assistant_materials_infos.md)
- [申请会议纪要权限](references/moma-meeting-POST_api_gateway_meeting-assistant_summary_permission_application.md)
