# 卸载本地技能（npx skills remove）

> **Prerequisites:** 本能力操作本机文件系统，不调用 Moma 卸载接口。执行前须向用户展示已安装位置并确认卸载范围。

用户要卸载某个技能时：先查出该技能的全部本地安装位置，让用户选择卸载哪些（可多选或全部），确认后再执行 `npx skills@1.5.19 remove`。

## Recommended Commands

```bash
# 查找安装位置
npx skills@1.5.19 list --json
npx skills@1.5.19 list -g --json

# 按选择卸载（务必 -y，避免交互卡住）
npx skills@1.5.19 remove <skill-name> -a cursor -y
npx skills@1.5.19 remove <skill-name> -g -a cursor -y
npx skills@1.5.19 remove <skill-name> -a '*' -y
npx skills@1.5.19 remove <skill-name> -g -a '*' -y
```

其他项目：在对应项目根目录执行 list / remove（不加 `-g`）。

## Options（remove）

| 选项 | 含义 |
|------|------|
| `<skill-name>` | 技能名（与 list 的 `name` / SKILL.md `name` 一致） |
| `-g, --global` | 从全局范围卸载 |
| `-a, --agent <names...>` | 从指定 Agent 卸载；`'*'` 表示该范围内全部 Agent |
| `-y, --yes` | 跳过 CLI 确认提示（业务侧已单独确认过） |

## 交互文案

### 展示已安装位置

```text
技能「{name}」当前安装位置：
1. [项目] {projectRoot或.} | Agent：cursor, claude-code | 路径：{path}
2. [全局] | Agent：cursor | 路径：{path}
请选择要卸载的项（可多选，如 1,2；也可回复「全部」）：
```

### 确认摘要

```text
即将卸载：
- 技能：{name}
- 卸载范围：{所选位置摘要}
是否确认卸载？
```

## Workflow

1. 确认卸载意图与目标技能名。
2. 默认 list 当前项目 + 全局；用户指定其他项目则一并查询。过滤出该 `name`。
3. 无匹配 → 告知未找到，结束。
4. 编号展示已安装位置，等待用户多选或「全部」。
5. 展示确认摘要；用户同意后按项执行 `remove -y`（映射好 `-g` / `-a` / cwd）。
6. 汇总成功/失败；不要重复二次确认。

## Notes

- 固定版本：`npx skills@1.5.19`。
- list JSON 中 `agents` 可能是展示名（如 `Claude Code`），remove 前映射为 `claude-code` 等（见主 Skill「Agent 名称映射」）。
- 多项卸载彼此独立；单条失败不阻断其余项。
- 卸载不是 Moma `high-risk-write`，但仍须完成一次业务范围确认后再执行。
