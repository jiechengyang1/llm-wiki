# 查询本地已安装技能（npx skills list）

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` for shared safety rules when needed.本能力为**本地查询**，不调用 Moma API，也**不**使用 `GET_moma-cli-api_skill_all-installed`。

使用 `npx skills@1.5.19 list`（别名 `ls`）查看本机已安装到各 Agent 的技能。用户可指定 **Agent**、**当前/其他项目** 或 **全局**。

## Recommended Commands

```bash
# 当前项目
npx skills@1.5.19 list --json

# 全局
npx skills@1.5.19 list -g --json

# 按 Agent 过滤（可与 -g 组合）
npx skills@1.5.19 list -a cursor --json
npx skills@1.5.19 list -g -a cursor -a claude-code --json

# 其他项目：在该项目根目录下执行（不加 -g）
# cwd = /absolute/path/to/other-project
npx skills@1.5.19 list --json
```

优先使用 `--json`，便于解析。

## Options

| 选项 | 含义 |
|------|------|
| `-g, --global` | 只查全局安装 |
| 不加 `-g` | 只查当前 cwd 对应的项目安装 |
| `-a, --agent <names...>` | 按 Agent 过滤（如 `cursor`、`claude-code`） |
| `--json` | JSON 输出 |

> 用户要「当前项目 + 全局」时：分别执行一次不加 `-g` 与一次 `-g`，合并后展示。

## JSON 输出示例

```json
[
  {
    "name": "moma-skill-hub",
    "path": "/path/to/.agents/skills/moma-skill-hub",
    "scope": "project",
    "agents": ["Cursor", "Claude Code"]
  }
]
```

| 字段 | 含义 |
|------|------|
| `name` | 技能名（来自 SKILL.md `name`） |
| `path` | 安装路径 |
| `scope` | `project` 或 `global` |
| `agents` | 已关联 Agent（多为展示名；展示时可原样输出，卸载时需映射回 `--agent` 值） |

## Workflow

1. 确认查询本地已安装意图。
2. 收集范围与 Agent（用户已说明则跳过询问）：
   - 范围：当前项目 / 全局 / 其他项目（绝对路径）/ 全部（当前项目+全局）
   - Agent：可选
3. 按范围执行 `npx skills@1.5.19 list … --json`。
4. 按输出格式展示；空列表则告知暂无，`共 0 条`。
5. **禁止**调用 `GET_moma-cli-api_skill_all-installed`。

## 输出格式

```text
技能名称：{name}
安装范围：{project|global}
安装路径：{path}
已安装 Agent：{agents 逗号分隔}
```

多条用 `---`，末尾 `共 {N} 条`。

## Notes

- 固定版本：`npx skills@1.5.19`。
- 口语 `claude` → `--agent claude-code`；详见主 Skill「Agent 名称映射」。
- 本能力只读本地文件系统，不涉及 Moma 登录（除非用户同时做推荐/下载等 API 操作）。
