# moma skill hub api GET_moma-cli-api_skill_download

> **Prerequisites:** Please read `../../moma-shared/SKILL.md` to understand login, permission handling, and high-risk write confirmation.

按编码 `skillId` 下载技能包（zip）。`versionId` 为空时取当前最新版本。

**默认用途是安装**：下载到临时目录后，用 `npx skills@1.5.19 add … --copy` 安装到用户指定的项目位置与 Agent，完成后删除临时目录。仅当用户明确只要 zip 时，才落盘到用户指定路径并结束。

**安装文件夹名称**：必须以解压后 `SKILL.md` frontmatter 的 **`name`** 为准；目录名不一致时先重命名再安装。

## Recommended Commands

> `risk=high-risk-write`，必须用户确认后加 `--yes`。用 `--output` 落盘。

```bash
moma moma-skill-hub schema GET_moma-cli-api_skill_download --json

# 安装流程：下载到临时目录
moma moma-skill-hub api GET_moma-cli-api_skill_download \
  -q "skillId=personal_875" \
  --output /tmp/moma-skill-XXXX/skill.zip \
  --yes

# 指定版本
moma moma-skill-hub api GET_moma-cli-api_skill_download \
  -q "skillId=personal_875&versionId=1" \
  --output /tmp/moma-skill-XXXX/skill.zip \
  --yes

# 解压后读取 SKILL.md 的 name，将目录重命名为该 name，再安装
# 安装（必须 --copy；按用户选择追加 -g / -a）
npx skills@1.5.19 add /tmp/moma-skill-XXXX/extracted/<name> --copy -y -a cursor
npx skills@1.5.19 add /tmp/moma-skill-XXXX/extracted/<name> --copy -y -g -a '*'
```

## Options

| 字段 / 选项 | 是否必填 | 含义 |
|------------|---------|------|
| `skillId` | 必填 | 编码 ID，如 `personal_875` |
| `versionId` | 可选 | 版本 ID；不传则最新 |
| `--output <path>` | 强烈建议 | 保存为本地 zip；已存在文件不会覆盖 |
| `--yes` | 需要 | 确认执行 |

## 安装交互（必须）

先收集参数，再一次性确认：

### 安装位置（项目范围）

```text
请选择 Skill 的安装位置：
1. 当前项目
2. 全局（对本机用户生效，不绑定某个仓库）
3. 其他项目（可填多个，需提供各项目根目录的绝对路径）
```

可多选。选「其他项目」时必须拿到存在的项目根目录绝对路径。

### 目标 Agent

```text
请选择要安装到的 Agent（可多选，例如 cursor、claude-code）：
- 指定 Agent：直接回复名称（常用：cursor、claude-code、codex 等）
- 全部 Agent：回复「全局」——将对所有可识别的 Agent 执行安装
```

若选「全局」Agent，须提示：将对所有可识别 Agent 安装。

口语映射：`claude` → `claude-code`；其余以 `skills` CLI agent 名为准。

### 确认摘要

```text
即将安装 Skill：
- 技能：{skillName}（{skillId}）
- 安装目录名：以 SKILL.md 的 name 为准（安装时确定）
- 安装位置：{当前项目 / 全局 / 其他项目路径列表}
- 目标 Agent：{cursor, claude-code / 全部可识别 Agent}
确认后将：下载到临时目录 → 以 copy 方式安装 → 自动清理临时文件。
是否确认安装？
```

## Workflow

1. 确认安装意图与目标 `skillId`。
2. 询问安装位置 → 询问目标 Agent（选「全局」Agent 时给出提示）。
3. 展示确认摘要，等待用户同意（只确认一次）。
4. 创建临时目录，带 `--output` 与 `--yes` 下载 zip，解压并定位含 `SKILL.md` 的技能根目录。
5. **读取 `SKILL.md` 的 `name`**；若解压目录名与 `name` 不一致，重命名为 `name`。`$SKILL_PATH` 指向重命名后的目录。
6. 对每个安装位置分别执行 `npx skills@1.5.19 add "$SKILL_PATH" --copy -y …`：
   - 当前项目：在当前项目根执行，不加 `-g`，加对应 `-a`
   - 全局位置：加 `-g`，加对应 `-a`
   - 其他项目：`cwd` 设为该项目根，不加 `-g`，加对应 `-a`
   - 全部 Agent：`-a '*'`
7. 流程结束（无论成败）删除临时目录。
8. 汇总各位置安装结果，并告知安装目录名（`name`）；不要输出完整签名下载链接。

### 仅下载 zip

用户明确只要 zip 时：确认保存路径 → 下载 → 告知 zip 路径，不调用 `npx skills`。

## Notes

- 安装必须使用 `npx skills@1.5.19`，且必须 `--copy`，保证各位置独立、临时目录可安全删除。
- **安装文件夹名称 = SKILL.md 的 `name`**（不得用 zip 内随意目录名或 skillId 顶替）。
- 不要把临时目录或未安装的 zip 当作默认最终交付物。
- `--output` 目标文件已存在时 CLI 不会覆盖；需换路径或先处理旧文件。
- `skillId` 可来自 `available-skills` / 用户指定。
