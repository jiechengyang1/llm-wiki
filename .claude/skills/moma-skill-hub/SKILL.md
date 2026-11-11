---
name: moma-skill-hub
version: 1.4.0
description: "MOMA Skill Hub：技能中心开放能力。查询本地已安装技能（npx skills）；按用户需求推荐可用技能；更新/上传个人 skill；下载/安装/卸载 skill（支持当前项目、全局、其他项目与指定 Agent）。"
metadata:
  requires:
    bins: ["moma"]
  cliHelp: "moma --help"
---

# 技能中心

**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../moma-shared/SKILL.md`](../moma-shared/SKILL.md)，其中包含登录、权限处理、高风险写操作确认协议。**
**CRITICAL — 本业务 Skill 只能补充业务域规则，不得覆盖或放宽 `moma-shared` 中的登录、权限、敏感信息和高风险确认要求。**
**CRITICAL — `replace` / `upload` / `download` 均为 `high-risk-write`：业务参数只向用户确认一次；用户同意后直接带 `--yes` 执行。禁止先 `--dry-run` 再二次确认，禁止对同一操作反复询问「是否确认」。禁止在用户未同意时静默加 `--yes`。**
**CRITICAL — 安装 / 卸载通过 `npx skills@1.5.19` 操作本地文件：须先向用户确认范围，再执行；卸载可多选或全部。**

## 快速决策

| 用户意图 | 判断依据 | 调用方式 |
|---------|---------|---------|
| **查询已安装技能** | 问的是「我已经装了什么」，不涉及具体任务场景 | `npx skills@1.5.19 list`（**不**再调 all-installed 接口） |
| **推荐可用技能** | 描述了想做的事 / 需要的功能，问「用什么 skill」「有没有合适的技能」「帮我推荐」 | `GET_moma-cli-api_skill_available-skills` + 语义匹配 |
| **更新 / 替换 skill** | 要更新某个已有 skill（上下文来自可用列表或用户给出的 skillId） | `POST_moma-cli-api_skill_replace`（仅 personal） |
| **上传 skill** | 要上传本地 zip 到技能中心 | `POST_moma-cli-api_skill_upload`（仅 personal） |
| **下载 / 安装 skill** | 要下载或安装某个 skill 到本地 | `GET_moma-cli-api_skill_download` → 临时目录 → `npx skills@1.5.19 add … --copy` |
| **卸载 skill** | 要卸载 / 删除某个已安装 skill | `npx skills@1.5.19 list` 查位置 → 用户选择 → `npx skills@1.5.19 remove` |

### 意图识别：查询已安装技能

触发语示例：

- 「我安装了哪些技能」「我的技能列表」「我装了什么 skill」
- 「看看我已有的技能」「当前安装了哪些」
- 「看看全局装了什么」「cursor 里装了哪些 skill」「这个项目装了啥」

### 意图识别：推荐可用技能

触发语示例（核心是**用户有任务/场景需求，想找合适的 skill**）：

- 「我想发送企微消息，可以用什么 skill」
- 「有没有能处理 Excel 的技能」
- 「帮我推荐一个写代码审查的 skill」
- 「我想查会议转写，用哪个技能」
- 「有什么 skill 能帮我生成 PDF」
- 「find a skill for …」「推荐技能」「哪个 skill 适合 …」

### 意图识别：更新 skill

触发语示例：

- 「更新这个 skill」「替换 skill 文件」「把本地 zip 更新到 personal_875」
- 上下文刚查过可用列表，用户指定其中某个 skill 要更新

### 意图识别：上传 skill

触发语示例：

- 「上传这个 skill」「把 zip 上传到技能中心」「发布我的个人 skill」

### 意图识别：下载 / 安装 skill

触发语示例：

- 「下载这个 skill」「安装这个 skill」「把 skill 拉到本地」「装到 cursor / claude」

### 意图识别：卸载 skill

触发语示例：

- 「卸载这个 skill」「删除本地 skill」「把 xxx 技能卸掉」
- 「从 cursor 里移除这个 skill」「取消安装」

**区分要点：**

- 用户问的是**本地已装资产** → 走「查询已安装技能」（`npx skills list`）。
- 用户问的是**能力匹配**（想做某事、需要某功能）→ 走「推荐可用技能」。
- 若同时出现（「我装的技能里有没有能发企微的」），先查本地已安装列表，再在结果中筛选；不要直接走全量推荐。
- **更新**针对技能中心已存在的 personal skill；**上传**是新建个人 skill；**安装/卸载**操作本机 Agent 目录。不要混淆。

## 核心概念

- **业务 service**：`moma-skill-hub`，对应本 Skill 目录 `moma-skill-hub`。
- **CLI 服务名**：`moma-skill-hub`，Moma API 命令使用 `moma moma-skill-hub ...`。
- **本地技能管理**：安装、查询已安装、卸载一律使用 **`npx skills@1.5.19`**（固定此版本）。
- **当前用户**：由 Moma CLI 登录态和 gateway 注入的当前员工身份决定；业务 Skill 不手工拼接鉴权头。
- **已安装技能（本地）**：通过 `npx skills list` 在本机项目 / 全局 / 指定 Agent 下发现的技能。
- **可用技能**：当前用户有权限查看/使用的技能池（个人技能、广场公开技能、有权限的团队空间技能），来自 available-skills 接口。
- **编码 skillId**：格式 `{source}_{原始ID}`，如 `personal_875`、`skill_square_447`。更新/下载必须使用该编码 ID。
- **个人技能**：`skillId` 以 `personal_` 开头。
- **团队 / 广场技能**：`skillId` 含 `space` 或 `skill_square`（当前**禁止**通过本 Skill 更新）。
- **安装目录名**：以解压后 `SKILL.md` frontmatter 的 **`name`** 为准（见安装流程）。

## 业务规则

- **查询已安装**：使用 `npx skills@1.5.19 list`，**禁止**再调用 `GET_moma-cli-api_skill_all-installed`。用户可指定 Agent、项目或全局；未指定时按下方工作流询问或默认查当前项目+全局。
- 推荐技能时固定传参：`pageNum=1&pageSize=300&roles=consumer&orderField=usedCount`。
- 推荐匹配仅使用 `skillId`、`skillName`、`description`；最多推荐 5 条，可以 0 条。
- **更新 skill 仅允许 personal**：若目标 `skillId` 含 `space` 或 `skill_square`，直接提示「仅允许更新个人Skill数据！」，不要调用 replace。
- **上传 skill 仅允许 personal**：`source` 默认 `personal`；若用户明确要上传到某某技能库/团队库，回复「目前仅支持上传到个人技能中，有相关需求请联系Moma团队进行升级」，不要调用 upload。
- `replace` / `upload` / `download` 均为 `high-risk-write`：**一次确认协议**——展示业务摘要并得到用户同意后，立即带 `--yes` 直调，不要 `--dry-run`，不要因 high-risk 再问第二遍。
- **安装 skill**：先收集「安装位置」和「目标 Agent」，再一次性确认；确认后下载到临时目录 → 按 `SKILL.md` 的 `name` 规范目录名 → `npx skills@1.5.19 add … --copy` → 删除临时目录。各安装位置彼此独立（copy，互不影响）。
- **卸载 skill**：先用 list 展示该技能已安装位置，让用户选择卸载哪些（可多选或全部），确认后再 `remove`。
- 不要向用户输出完整 `downloadUrl` 签名链接等敏感或过长内部地址（展示业务字段时除外）。
- multipart 接口用 `-F "file=<绝对路径>"` 传 zip，其它字段用单个 `-d '{...}'` JSON。

## Agent 名称映射

用户口语 → `npx skills` 的 `--agent` 值：

| 用户说法 | `--agent` |
|---------|-----------|
| cursor | `cursor` |
| claude / claude-code | `claude-code` |
| codex | `codex` |
| 其他 | 以 `skills` CLI 支持的 agent 名为准；不确定时用用户给出的原名 |

## 命令

本 Skill 的所有 `moma moma-skill-hub list/schema/api` 命令都必须添加 `--json`（下载落盘时 `--output` 与 `--json` 的组合以 CLI 实际支持为准；落盘优先保证 `--output` 与 `--yes`）。

```bash
# 查看服务已接入 API
moma moma-skill-hub list --json

# 推荐：查询可用技能
moma moma-skill-hub api GET_moma-cli-api_skill_available-skills --json -q "pageNum=1&pageSize=300&roles=consumer&orderField=usedCount"

# 本地已安装（优先 --json，便于解析）
npx skills@1.5.19 list --json
npx skills@1.5.19 list -g --json
npx skills@1.5.19 list -a cursor --json
npx skills@1.5.19 list -g -a cursor --json

# 更新个人 skill
moma moma-skill-hub api POST_moma-cli-api_skill_replace --json \
  -F "file=/absolute/path/to/skill.zip" \
  -d '{"skillId":"personal_875","displayName":"cli测试","displayDescription":"这是一个更新测试","versionDesc":""}' \
  --yes

# 上传个人 skill
moma moma-skill-hub api POST_moma-cli-api_skill_upload --json \
  -F "file=/absolute/path/to/skill.zip" \
  -d '{"source":"personal","displayName":"成语接龙","displayDescription":"随便描述","versionDesc":""}' \
  --yes

# 下载到临时目录（安装流程内部使用）
moma moma-skill-hub api GET_moma-cli-api_skill_download \
  -q "skillId=personal_875" \
  --output /tmp/moma-skill-XXXX/skill.zip \
  --yes

# 安装（务必 --copy；目录名已按 SKILL.md name 就绪）
npx skills@1.5.19 add /tmp/moma-skill-XXXX/extracted/<name> --copy -y -a cursor

# 卸载
npx skills@1.5.19 remove <skill-name> -a cursor -y
npx skills@1.5.19 remove <skill-name> -g -a cursor -y
```

> **重要**：调用 Moma API 前必须先使用 `list` / `schema` 确认可用 API 和参数结构。若 `list` 中展示的 apiName 与本文不同，以 CLI 返回为准。

## 工作流

### 查询已安装技能

1. 确认用户意图为查询**本地已安装**技能。
2. **收集过滤条件**（用户已说明则直接用；未说明可简短询问，或默认查「当前项目 + 全局」）：
   - **范围**：当前项目 / 全局 / 其他项目（需项目根目录绝对路径）/ 全部（当前项目+全局）
   - **Agent**（可选）：如 cursor、claude-code；未指定则不过滤 Agent
3. 执行对应命令（建议加 `--json`）：

```bash
# 当前项目
npx skills@1.5.19 list --json
# 可选：-a cursor

# 全局
npx skills@1.5.19 list -g --json

# 其他项目：将 cwd / working_directory 设为该项目根后再 list（不加 -g）

# 用户要「全部」：分别执行项目 list 与 -g list，合并结果后展示
```

4. 按「已安装技能输出格式」展示；多条用 `---`；末尾 `共 {N} 条`。
5. **不要**调用 `GET_moma-cli-api_skill_all-installed`。

### 推荐可用技能

1. 确认用户描述了任务场景或功能需求。
2. 执行可用技能查询（固定 pageSize=300 等参数）。
3. 从 `data.skills` 取 `skillId`、`skillName`、`description` 做语义匹配，最多 5 条。
4. 按「推荐技能输出格式」展示。

### 更新 skill（replace）

1. 确认用户要**更新**某个 skill，且上下文中该 skill 来自 `available-skills`（或用户给出了编码 `skillId`）。
2. **解析编码 skillId**：`available-skills` 直接用返回的 `skillId`（如 `personal_875`）。
3. **个人技能校验**：若 `skillId` 含 `space` 或 `skill_square`，停止并提示用户：**仅允许更新个人Skill数据！**
4. 确认本地 zip **绝对路径**，以及可选的 `displayName` / `displayDescription` / `versionDesc`。缺路径则向用户索取。
5. **一次确认**：向用户展示将要更新的摘要（skillId、文件路径、展示名、描述），等待显式确认。用户修改某一项则改完后再次展示全量摘要，直到确认。
6. 用户同意后**立刻**带 `--yes` 直调，**不要**先 `--dry-run`，**不要**再问「是否确认执行高风险写操作」：

```bash
moma moma-skill-hub api POST_moma-cli-api_skill_replace --json \
  -F "file=/Users/wangdi/Documents/chengyu-jielong11.zip" \
  -d '{"skillId":"personal_875","displayName":"cli测试","displayDescription":"这是一个更新测试","versionDesc":""}' \
  --yes
```

7. 根据返回 `code` / `message` 汇报结果；不要输出完整签名下载链接。

### 上传 skill（upload）

1. 确认用户要**上传** skill。
2. 若用户明确要上传到某某技能库 / 团队库 / space：回复 **目前仅支持上传到个人技能中，有相关需求请联系Moma团队进行升级**，停止。
3. **收集并确认参数**（必须得到用户确认后再调用）：
   - 上传文件：绝对路径（上下文能判断出则先展示给用户确认；用户提供了 path 则用用户的）。
   - 技能名称：`displayName`
   - 技能描述：`displayDescription`
4. 展示确认卡片样式文本：

```text
上传文件：/Users/wangdi/Documents/chengyu-jielong11.zip
技能名称：成语接龙
技能描述：随便描述
是否确认上传？
```

5. 若用户修改了某一项：只改那一项，**再次展示全量三项**，直到用户明确确认（这是唯一的确认轮次；确认后不再二次确认）。
6. `source` 固定传 `personal`。用户对上述摘要说确认后，**立刻**带 `--yes` 直调，**不要**先 `--dry-run`，**不要**再因 high-risk-write 额外询问：

```bash
moma moma-skill-hub api POST_moma-cli-api_skill_upload --json \
  -F "file=/Users/wangdi/Documents/chengyu-jielong11.zip" \
  -d '{"source":"personal","displayName":"成语接龙","displayDescription":"随便描述","versionDesc":""}' \
  --yes
```

7. 若调用返回 HTTP 未知错误、读文件失败、权限类错误等：提醒用户**确认当前终端是否有文件目录访问权限**，并转述 CLI 非敏感错误信息。

### 下载 / 安装 skill（download + install）

用户要「安装」或「下载到本地可用」时，走本流程（默认完成安装，不只留 zip）。若用户**明确只要 zip、不安装**，可只下载到其指定路径并结束。

#### 1. 确定目标 skill

确认安装意图，并确定编码 `skillId`（来自可用列表或用户指定）。

#### 2. 询问安装位置（项目范围）

```text
请选择 Skill 的安装位置：
1. 当前项目
2. 全局（对本机用户生效，不绑定某个仓库）
3. 其他项目（可填多个，需提供各项目根目录的绝对路径）
```

- 选 **1**：安装到当前工作目录所在项目。
- 选 **2**：使用 `npx skills` 的 `-g/--global`。
- 选 **3**：向用户索取一个或多个**项目根目录绝对路径**；路径无效或不存在则请用户修正后再继续。
- 用户可同时选择多种位置；每种位置独立执行一次 copy 安装，互不影响。

#### 3. 询问目标 Agent

```text
请选择要安装到的 Agent（可多选，例如 cursor、claude-code）：
- 指定 Agent：直接回复名称（常用：cursor、claude-code、codex 等）
- 全部 Agent：回复「全局」——将对所有可识别的 Agent 执行安装
```

**务必提示**：若选择「全局」Agent，将对当前环境中**所有可识别的 Agent** 进行安装。

- 指定 Agent：组装 `-a <name>`（可多个）。
- 全部 Agent：使用 `-a '*'`。

#### 4. 一次确认

```text
即将安装 Skill：
- 技能：{skillName}（{skillId}）
- 安装目录名：以 SKILL.md 的 name 为准（安装时确定）
- 安装位置：{当前项目 / 全局 / 其他项目路径列表}
- 目标 Agent：{cursor, claude-code / 全部可识别 Agent}
确认后将：下载到临时目录 → 以 copy 方式安装 → 自动清理临时文件。
是否确认安装？
```

用户修改任一项后，重新展示全量摘要，直到确认。确认后**不要**再因 high-risk 二次询问。

#### 5. 下载到临时目录并安装

用户确认后立即执行：

1. 创建临时目录（如 `mktemp -d`），下载 zip：

```bash
moma moma-skill-hub api GET_moma-cli-api_skill_download \
  -q "skillId=personal_875" \
  --output "$TMP_DIR/skill.zip" \
  --yes
```

2. 解压到临时目录，定位含 `SKILL.md` 的技能根目录。
3. **安装文件夹名称（必须）**：读取该目录下 `SKILL.md` frontmatter 的 **`name`** 字段，记为 `$SKILL_NAME`。
   - 若当前解压目录名与 `$SKILL_NAME` 不一致，**先重命名**为 `$SKILL_NAME`，再安装。
   - 后续 `npx skills add` 的路径必须指向重命名后的目录；最终落到各 Agent 下的文件夹名也以该 `name` 为准（CLI 会对非法字符做 sanitize）。
4. **必须**使用 `npx skills@1.5.19`，且**必须**加 `--copy`。加 `-y` 跳过交互提示。
5. 按用户选择的每个安装位置分别执行（失败互不影响，继续其余位置，最后汇总）：

```bash
# 当前项目（在当前项目根目录执行，不加 -g）
npx skills@1.5.19 add "$SKILL_PATH" --copy -y -a cursor

# 全局安装位置（加 -g）
npx skills@1.5.19 add "$SKILL_PATH" --copy -y -g -a cursor

# 其他项目（cwd 设为该项目根目录，不加 -g）
npx skills@1.5.19 add "$SKILL_PATH" --copy -y -a cursor

# 全部 Agent：-a '*'
npx skills@1.5.19 add "$SKILL_PATH" --copy -y -a '*'
npx skills@1.5.19 add "$SKILL_PATH" --copy -y -g -a '*'
```

6. **无论成功或失败**，安装流程结束后删除临时目录。不要把临时路径当作最终交付物。
7. 向用户汇报各位置结果，并说明安装目录名（`name`）；不要输出完整签名下载链接。

#### 仅下载 zip（不安装）

仅当用户明确只要 zip 时：询问保存路径 → 一次确认 → 带 `--output` 与 `--yes` 下载 → 告知 zip 路径。不要默认解压安装。

### 卸载 skill（remove）

1. 确认用户要**卸载**某个技能，并确定技能名（优先使用 `SKILL.md` 的 `name` / `npx skills list` 中的 `name`；用户给的展示名需先在已安装列表中解析）。
2. **查找已安装位置**（默认查当前项目 + 全局；用户指定其他项目则一并查）：

```bash
npx skills@1.5.19 list --json
npx skills@1.5.19 list -g --json
# 其他项目：在对应项目根执行 list --json
```

3. 过滤出目标技能的条目；若无匹配，告知用户未找到并结束。
4. **展示已安装位置**供选择（编号列表）：

```text
技能「{name}」当前安装位置：
1. [项目] {projectRoot或.} | Agent：cursor, claude-code | 路径：{path}
2. [全局] | Agent：cursor | 路径：{path}
请选择要卸载的项（可多选，如 1,2；也可回复「全部」）：
```

5. 用户选择后，展示确认摘要（只确认一次）：

```text
即将卸载：
- 技能：{name}
- 卸载范围：{所选编号对应的位置摘要}
是否确认卸载？
```

6. 用户确认后，对每一项执行对应 `remove`（加 `-y`）：

```bash
# 项目范围 + 指定 Agent
npx skills@1.5.19 remove <skill-name> -a cursor -a claude-code -y

# 全局范围 + 指定 Agent
npx skills@1.5.19 remove <skill-name> -g -a cursor -y

# 该位置下全部 Agent：-a '*'
npx skills@1.5.19 remove <skill-name> -a '*' -y
npx skills@1.5.19 remove <skill-name> -g -a '*' -y
```

- 其他项目：在对应项目根目录执行（不加 `-g`）。
- JSON 里的 `agents` 可能是展示名，执行 remove 前映射回 `--agent` 值（见「Agent 名称映射」）。
- 多项失败互不影响，最后汇总结果。

## 输出格式

### 已安装技能输出格式

```text
技能名称：{name}
安装范围：{project|global}
安装路径：{path}
已安装 Agent：{agents 逗号分隔}
```

多条用 `---` 分隔，末尾 `共 {N} 条`。若用户指定了筛选条件，可在开头注明（如「范围：全局；Agent：cursor」）。

### 推荐技能输出格式

```text
技能名称：{skillName}
技能描述：{description}
推荐理由：{简述为何匹配用户需求，一两句话即可}
[点击试一试](https://moma.ke.com/skills-hub?tab=team&skillId={skillId末段})
```

多条用 `---` 分隔。

`skillId` 链接取下划线分隔的最后一段：`skill_square_447` → `447`。

## 权限与错误处理

业务响应统一格式：

```json
{
  "code": 0,
  "message": "",
  "data": { ... }
}
```

### Agent 对响应的通用处理原则

- **`code=0`**：成功，按对应接口结构解析。
- **`code` 非 0**：转述 `message`，不要伪造结果。
- 上传/更新/下载：业务摘要确认通过后，调用时**必须已带 `--yes`**，避免触发 `GATEWAY_CONFIRMATION_REQUIRED` 造成二次确认。若仍收到 exit 10，说明漏加了 `--yes`，补上后重试，不要再向用户问一遍。
- CLI 层未登录等：按 `moma-shared` 处理。
- 上传/更新时文件读失败或 HTTP 未知错误：提醒确认终端对文件目录的访问权限。
- `npx skills@1.5.19` 失败：转述非敏感错误；确认 Node/npm 可用；路径与 Agent 名是否正确。安装流程的临时目录仍须清理。

### 通用错误汇总

| 情况 | 处理方式 |
|------|----------|
| 未登录 / 凭据失效 | 按 `moma-shared` 引导 `moma login`（仅 Moma API 场景） |
| 更新非 personal skill | 提示「仅允许更新个人Skill数据！」 |
| 上传到团队库 / 技能库 | 提示「目前仅支持上传到个人技能中，有相关需求请联系Moma团队进行升级」 |
| `code` 非 0 | 转述 `message` |
| 高风险写操作 | 业务摘要确认一次后直接 `--yes` 执行，禁止 dry-run 来回确认 |
| 文件路径/权限问题 | 提醒确认当前终端是否有文件目录访问权限 |
| 其他项目路径无效 | 请用户提供存在的项目根目录绝对路径 |
| `npx skills` 失败 | 转述错误；检查 Node/npm、路径与 Agent 名；安装时清理临时目录 |
| 卸载目标不存在 | 告知未找到该技能的本地安装记录 |
| 推荐无匹配 | 告知暂未找到匹配技能 |
| 本地无已安装技能 | 告知当前筛选条件下暂无已安装技能，`共 0 条` |

## 安全规则

- 不输出 Moma API Key、AccessToken、RefreshToken、完整 Authorization 头或其它敏感凭据。
- 不手工拼接鉴权头。
- 不直接调用业务服务 Swagger URL 或业务域名。
- 写入类操作（更新、上传、下载/安装、卸载）必须先完成一次业务确认再执行；不要 dry-run 二次确认。
- 不要静默对非 personal 目标执行 replace。
- 安装必须使用 `--copy`；临时下载目录在流程结束后必须删除。
- 安装目录名必须来自 `SKILL.md` 的 `name`。
- 查询已安装禁止改走 all-installed 接口。

## References

- [查询本地已安装技能](references/moma-skill-hub-GET_moma-cli-api_skill_all-installed.md)
- [查询可用技能并推荐](references/moma-skill-hub-GET_moma-cli-api_skill_available-skills.md)
- [更新个人技能](references/moma-skill-hub-POST_moma-cli-api_skill_replace.md)
- [上传个人技能](references/moma-skill-hub-POST_moma-cli-api_skill_upload.md)
- [下载与安装技能](references/moma-skill-hub-GET_moma-cli-api_skill_download.md)
- [卸载技能](references/moma-skill-hub-skills-remove.md)
