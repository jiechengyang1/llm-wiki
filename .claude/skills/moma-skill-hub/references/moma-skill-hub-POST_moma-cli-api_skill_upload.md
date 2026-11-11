# moma skill hub api POST_moma-cli-api_skill_upload

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, and high-risk write confirmation.

上传本地技能 zip 到技能中心。**本 Skill 仅支持 `source=personal`（个人技能）。**

## Recommended Commands

> `risk=high-risk-write`。业务摘要**只确认一次**，用户同意后直接带 `--yes` 执行；**不要**先 `--dry-run` 再二次确认。

```bash
moma moma-skill-hub schema POST_moma-cli-api_skill_upload --json

moma moma-skill-hub api POST_moma-cli-api_skill_upload --json \
  -F "file=/Users/wangdi/Documents/chengyu-jielong11.zip" \
  -d '{"source":"personal","displayName":"成语接龙","displayDescription":"随便描述","versionDesc":""}' \
  --yes
```

## Options

| 选项 | 说明 |
|------|------|
| `-F "file=<绝对路径>"` | multipart 上传技能 zip（必填） |
| `-d '{...}'` | 其它表单字段，单个 JSON 字符串 |
| `--yes` | 确认执行高风险写操作（业务确认后必须带上） |

`-d` 字段：

| 字段 | 是否必填 | 含义 |
|------|---------|------|
| `source` | 本 Skill 固定 | 必须为 `personal` |
| `spaceId` | space 时必填 | 本 Skill 不走 space，不要传 |
| `displayName` | 建议填写 | 展示名称 |
| `displayDescription` | 建议填写 | 展示描述 |
| `versionDesc` | 可选 | 版本说明 |
| `tags` | 可选 | 标签，逗号分隔 |

## 确认协议（只确认一次）

调用前向用户展示并得到确认（这是唯一确认；确认后不要再因 high-risk 二次询问）：

```text
上传文件：/Users/wangdi/Documents/chengyu-jielong11.zip
技能名称：成语接龙
技能描述：随便描述
是否确认上传？
```

- 上下文能判断出要上传的 zip 时，先展示路径让用户确认。
- 用户提供了 path / 名称 / 描述时，一并展示。
- 用户修改某一项后，**再次展示全量三项**，直到明确确认。
- 用户确认后**立刻**执行带 `--yes` 的上传命令，不要 `--dry-run`。

## 团队库限制

若用户明确要上传到 xx 技能库或团队库：回复 **目前仅支持上传到个人技能中，有相关需求请联系Moma团队进行升级**，不要调用本接口。

## Workflow

1. 确认上传意图；拒绝团队库 / space 目标。
2. 收集绝对路径、`displayName`、`displayDescription`，一次确认（改项则重展全量）。
3. `source=personal`，用户同意后立刻带 `--yes` 直调。
4. 若返回 HTTP 未知等错误：提醒用户**确认当前终端是否有文件目录访问权限**。

## Notes

- Content-Type 为 `multipart/form-data`；用 `-F` + `-d`，与 replace 相同。
- 成功时可汇报返回的编码 `skillId`、`skillName`；不要输出完整签名 `downloadUrl`。
