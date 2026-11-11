# moma skill hub api POST_moma-cli-api_skill_replace

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, and high-risk write confirmation.

用本地 zip 更新（替换）已有技能。`skillId` 为编码格式 `{source}_{原始ID}`。**本 Skill 仅允许更新 personal 技能。**

## Recommended Commands

> `risk=high-risk-write`。业务摘要**只确认一次**，用户同意后直接带 `--yes` 执行；**不要**先 `--dry-run` 再二次确认。

```bash
moma moma-skill-hub schema POST_moma-cli-api_skill_replace --json

moma moma-skill-hub api POST_moma-cli-api_skill_replace --json \
  -F "file=/Users/wangdi/Documents/chengyu-jielong11.zip" \
  -d '{"skillId":"personal_875","displayName":"cli测试","displayDescription":"这是一个更新测试","versionDesc":""}' \
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
| `skillId` | 必填 | 编码 ID，如 `personal_875` |
| `displayName` | 可选 | 展示名称 |
| `displayDescription` | 可选 | 展示描述 |
| `versionDesc` | 可选 | 版本说明 |

## 个人技能限制

- 仅允许更新 `personal_*` 技能。
- 若 `skillId` 含 `space` 或 `skill_square`：提示 **仅允许更新个人Skill数据！**，不要调用本接口。

### skillId 来源

- `available-skills`：直接用返回的 `skillId`。
- `all-installed`：若无编码 `skillId`，拼接 `{skillSource}_{sourceSkillId}`（仅当 `skillSource=personal` 时允许继续）。

## Workflow

1. 确认更新意图与目标 skill（来自列表或用户给出的编码 ID）。
2. 校验为 personal；非 personal 则停止并提示。
3. 确认 zip 绝对路径与展示字段；向用户展示摘要并**一次确认**（改项则重展全量，直到确认）。
4. 用户同意后**立刻**带 `--yes` 直调，不要 `--dry-run`，不要再问高风险确认。
5. 失败时转述非敏感错误，并检查文件路径权限。

## Notes

- Content-Type 为 `multipart/form-data`；CLI 用 `-F` + `-d` 组装，无需手工设 Content-Type。
- 不要输出返回中的完整签名 `downloadUrl`。
