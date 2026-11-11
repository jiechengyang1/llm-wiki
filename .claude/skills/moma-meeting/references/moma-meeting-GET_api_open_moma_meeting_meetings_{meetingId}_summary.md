# moma meeting api GET_api_open_moma_meeting_meetings_{meetingId}_summary

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, update notices, and security rules.

获取指定会议的智能纪要。

## Recommended Commands

> **必须添加 `--json`。** 本 Skill 的所有 `moma moma-meeting list/schema/api` 命令都必须添加 `--json`。

```bash
# 查看该 API 参数结构
moma moma-meeting schema GET_api_open_moma_meeting_meetings_{meetingId}_summary --json

# 获取智能纪要
moma moma-meeting api GET_api_open_moma_meeting_meetings_{meetingId}_summary --json -p "meetingId=<meetingId>"
```

## Options

```text
-p, --path-params <params>  路径参数，格式：key1=v1&key2=v2
```

路径参数：

| 字段 | 含义 |
|------|------|
| `meetingId` | 会议实例 ID，通常来自会议列表返回值 |

## Workflow

1. 确认目标会议 ID；如果用户没有提供，先查询会议列表。
2. 如参数不明确，先查看 `gateway schema`。
3. 执行命令。
4. 返回会议 ID、标题、纪要正文、生成状态和版本。
5. 如无纪要或权限不足，明确说明 CLI 返回的状态，不伪造内容。

## Notes

- 当前用户必须具备该会议会后查看权限。
- `generateState` 是纪要生成状态，具体枚举以 gateway schema 或 CLI 返回为准。
- 纪要可能包含会议敏感信息，输出时遵守 `moma-shared` 的敏感信息处理规则。
