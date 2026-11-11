# moma meeting api POST_api_gateway_meeting-assistant_summary_permission_application

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

申请查看会议纪要的权限，申请结果将通过企微消息通知会议组织者或管理员审批。

## Recommended Commands

```bash
# 查看该 API 参数结构
moma moma-meeting schema POST_api_gateway_meeting-assistant_summary_permission_application --json

# 申请会议纪要权限（传入会议 ID 和申请原因）
moma moma-meeting api POST_api_gateway_meeting-assistant_summary_permission_application --json -d '{"meetingInstanceId":"<meetingId>","applicationReason":"需要查看会议纪要"}'

# 申请会议纪要权限（不传申请原因）
moma moma-meeting api POST_api_gateway_meeting-assistant_summary_permission_application --json -d '{"meetingInstanceId":"<meetingId>"}'
```

## Options

```text
-d, --data <json-string>   传入 JSON body，格式：'{"key1":"v1","key2":"v2"}'
```

请求体参数：

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `meetingInstanceId` | **必填** | 会议实例 ID，通常来自会议列表返回值 |
| `applicationReason` | 可选 | 申请查看原因，例如"需要参考会议内容" |

## 响应格式

所有响应使用统一信封格式，判断 `errno` 决定业务状态：

### 成功（errno=0）

```json
{
  "errno": 0,
  "errmsg": "成功",
  "data": "申请会议纪要权限成功，请等待管理员审批"
}
```

### 会议不存在或已删除（errno=40002）

```json
{
  "errno": 40002,
  "errmsg": "会议不存在或已删除",
  "hint": "请检查传入的 meetingInstanceId 是否正确且有效；当前会议可能已被删除或尚未创建。修正参数后重新调用。",
  "retryable": false,
  "data": null
}
```

### 无法获取会议主持人信息（errno=50002）

```json
{
  "errno": 50002,
  "errmsg": "无法获取会议主持人信息",
  "hint": "当前会议没有有效的主持人信息，或主持人未绑定企微账号，无法发送审批通知；请确认会议已配置主持人后重新申请。不要用相同参数重试。",
  "retryable": false,
  "data": null
}
```

### 申请会议纪要权限失败（errno=50003）

```json
{
  "errno": 50003,
  "errmsg": "申请会议纪要权限失败",
  "hint": "企微消息服务暂时不可用或配置异常，无法发送审批通知；请稍后重试。如果持续失败，联系管理员确认企微消息配置。",
  "retryable": true,
  "data": null
}
```

### 服务异常（errno=50001）

```json
{
  "errno": 50001,
  "errmsg": "服务异常信息",
  "hint": "会议或企微消息下游服务暂时不可用，请稍后重试；如果持续失败，携带接口名和会议ID联系会议助手服务负责人排查。",
  "retryable": true,
  "data": null
}
```

## Agent 对不同 errno 的响应规则

| errno | 含义 | Agent 行为 |
|-------|------|-----------|
| `0` | 成功 | 告知用户权限申请已提交，等待管理员审批 |
| `40002` | 会议不存在或已删除 | 告知用户会议不存在，检查 meetingInstanceId 是否正确，修正后重试 |
| `50002` | 无法获取会议主持人信息 | 告知用户该会议没有有效的主持人信息，建议联系管理员确认会议配置 |
| `50003` | 申请会议纪要权限失败 | 告知用户企微消息服务异常，稍后重试（retryable=true）；持续失败建议联系管理员 |
| `50001` | 服务不可用 | 告知用户服务暂不可用，稍后重试（retryable=true） |

## Workflow

1. 确认场景：用户查看会议内容时遇到 `errno=40301`（无权限），或用户明确要求申请查看某个会议的纪要权限。
2. **必须先与用户确认**：告知用户申请后需等待审批，确认用户同意再操作。
3. 确认目标 `meetingInstanceId`；如果用户没有提供，先查询会议列表让用户选择。
4. 确认 `applicationReason`（可选）：如果用户没有提供则不传。
5. 如参数不明确，先执行 `moma moma-meeting schema POST_api_gateway_meeting-assistant_summary_permission_application --json`。
6. 执行提交命令，使用 `-d` 传入 JSON body。
7. 判断 `errno`：
   - **`errno=0`**：告知用户"权限申请已提交，请等待管理员审批"。
   - **`errno=40002`**：检查 `meetingInstanceId` 参数是否正确，告知用户会议不存在，修正后重试。
   - **`errno=50002`**：告知用户该会议没有有效的主持人信息，建议联系管理员确认会议配置；不要重试。
   - **`errno=50003` 且 `retryable=true`**：告知用户服务异常，稍后可以重试。
   - **`errno=50001` 且 `retryable=true`**：告知用户服务暂不可用，稍后重试。
8. 向用户确认是否需要再次查看会议内容（权限申请已提交后暂无即时效果）。

## Notes

- 该接口是**写入操作**，Agent **不得**在用户未明确确认的情况下自动调用。
- 权限申请提交后不等同于即时获得权限，需要等待会议组织者或管理员审批，不能立即重试查看会议内容。
- 申请通过后，审批结果会通过企微消息通知申请人。
- 该接口内部会通过企微消息通知会议组织者处理审批。
