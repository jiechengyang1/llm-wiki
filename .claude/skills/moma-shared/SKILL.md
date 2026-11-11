---
name: moma-shared
version: 1.0.0
description: "Use when setting up or updating moma CLI or MOMA Skills, running login or auth commands, handling permission errors, or applying shared command and safety rules required by a concrete MOMA Skill."
---

<!-- MOMA CLI 管理的 MOMA CLI skill，请勿手动编辑。 -->

# MOMA CLI 共享规则

本 Skill 规定使用 `moma` CLI 时共同遵守的登录、权限、参数传递、JSON 输出、错误处理、更新和安全规则。

具体能力的 `<service>`、API 名称、请求参数、返回结构和执行流程，以对应具体 Skill 及其 references 为准。

## Windows 系统环境适配

如果当前系统环境为 Windows，所有 `moma` 命令必须通过 PowerShell 执行。

- 当将要执行的 `moma` 命令包含 JSON、引号、`&` 或其它在 PowerShell 中具有特殊含义的字符时，则执行前必须按照 PowerShell 的引号和转义规则，将相关参数转换为 PowerShell 可正确解析的写法。
- 转换只能改变引号和转义写法，严禁改变原命令的 `<service>`、子命令、`<apiName>`、选项、参数值、JSON 结构和命令语义。
- 每个参数值必须保持为一个独立、完整的参数，不得因转义将一个参数拆开，也不得将多个参数合并，禁止盲目推测、改写或替换参数值。
- 只有 PowerShell 不可用时，才允许回退使用 cmd 执行 `moma` 命令，除非用户明确要求，否则严禁切换至 cmd、WSL、Git Bash 或其它 Shell。


## 命令占位符

本 Skill 的命令模板使用以下占位符：

- `<service>` 是 `moma` 后、`list` / `schema` / `api` 前的服务标识，由要求读取本 Skill 的具体 Skill 声明。
- `<apiName>` 是 `schema` 或 `api` 后的完整 API 名称，由当前业务 Skill 及其 references 指定。
- 具体 Skill 未声明 `<service>` 时，说明该 Skill 配置不完整并停止调用；不得推导、补全或改写 `<service>`。
- 占位符必须在执行前替换为真实值，不得将包含尖括号的命令发送到终端。
- 禁止在不同具体 Skill 之间复用 `<service>`、API 名称、参数或返回语义。

## 登录与权限

执行依赖登录态的命令前，先确认本机登录状态：

```bash
moma auth check --json
```

需要先确认登录状态的命令包括：

- `moma <service> list --json`
- `moma <service> schema <apiName> --json`
- `moma <service> api <apiName> --json`
- `moma upgrade --check --json`
- `moma upgrade --json` 或其别名 `moma update --json`

同一任务中已确认登录态可用后，不需要在每次 list、schema、api 前重复执行 moma auth check --json；只有遇到未登录、凭据缺失、凭据失效或权限相关错误时，再重新检查登录状态。

以下命令不需要预先检查登录状态：

- `moma login --json`
- `moma auth check --json`
- `moma auth status --json`
- `moma --help`
- `moma --version`
- `moma doctor`

如果未登录或本地登录态缺失，停止执行依赖登录态的命令，并引导用户在当前终端完成登录：

```bash
moma login --json
```

## 登录状态判断

执行 `moma auth check --json` 后，按以下规则判断登录态。

| 字段 | 含义 | 判断规则                                                                                                                          |
|------|------|----------|
| `status` | 登录态状态 | `logged_in` 表示存在本地登录态；`env` 表示登录态使用环境变量 `MOMA_TOKEN` 且验证通过；`missing` 表示未登录且本地凭据缺失；`env_invalid` 表示回退使用的环境变量 `MOMA_TOKEN` 验证失败 |
| `available` | 是否可以继续调用依赖登录态的命令 | `true` 表示可以继续；`false` 表示停止后续调用                                                                                                |
| `userId` | 当前登录用户 ID | 仅用于展示或确认，不用于鉴权拼参                                                                                                              |
| `apiKeyMasked` | 脱敏后的 Moma API Key | 仅用于展示，不用于鉴权拼参                                                                                                                 |
| `message` | 登录状态说明 | 可以向用户转述                                                                                                                       |
| `hint` | 登录状态恢复建议 | 优先按该字段执行登录或刷新                                                                                                                 |

- stdout 中 `available=true`（包括 `status="logged_in"` 和 `status="env"`）：登录态可用，可以继续执行依赖登录态的命令。
- stdout 中 `status="missing"` 或 `available=false`：表示登录态检查未通过，停止后续调用并按 `hint` 登录或刷新。
- stdout 中 `status="env_invalid"`：表示环境变量 `MOMA_TOKEN` 校验失败，此时 `hint` 是脱敏后的失败说明（诊断信息，不是可直接执行的命令）。停止后续调用，向用户转述失败原因，并引导执行 `moma login --json` 建立本地登录态——本地登录态优先级高于环境变量，登录成功后即可绕过失效的 `MOMA_TOKEN`。
- stderr 中出现 `{ "ok": false, "error": { ... } }`：登录检查执行异常，使用 `error.type`、`error.code`、`error.message` 和 `error.hint` 判断并处理。

## 具体能力调用

- 当前任务中，每个 `<service>` 首次执行 `schema` 或 `api` 前，必须先执行 `moma <service> list --json` 获取当前 `<service>` 可用 API 名单；获取失败时停止调用。
- 每次执行 `schema` 或 `api` 前，必须先确认本次将要执行的完整 `<apiName>` 是否存在于可用 API 名单中，禁止盲目推测、改写或替换 `<apiName>`。；
- 当 `<apiName>` 不在可用 API 名单中时，重新执行一次 `moma <service> list --json` 获取当前 `<service>` 最新可用 API 名单，如果包含该 `<apiName>` 则继续执行；仍不包含时停止调用；
- 如果 CLI 提示 API 不存在时，重新执行一次 `moma <service> list --json` 获取当前 `<service>` 最新可用 API 名单，如果包含该 `<apiName>` 则继续执行，仍不包含时停止调用；
- 执行 `api` 前如果请求参数、响应结构或风险级别不明确，则执行 `moma <service> schema <apiName> --json` 获取明确请求参数、响应结构或风险级别，禁止盲目推测。
- 只需要确认入参时，执行 `moma <service> schema <apiName> --request --json`， 禁止盲目推测。。
- 只需要确认出参时，执行 `moma <service> schema <apiName> --response --json`， 禁止盲目推测。。
- `-p` / `-q` 参数值需要作为一个完整参数传入；包含 `&` 时必须加引号，例如 `-q "a=1&b=2"`。
- GET 请求参数使用 `-q` 传入，不要放进 `-d`。
- 请求 body 使用 `-d` 传入单个 JSON 字符串，不要拆成多个 `-d` 或散参数；Windows 环境必须使用“Windows 系统环境适配”中的固定方式。
- 禁止直接调用目标 URL；始终通过 CLI 命令调用。
- 如果无法同时满足业务 Skill 指引和当前 schema 时停止调用，禁止自行修改业务逻辑。
- 调用失败时，仅向用户说明业务能力调用失败及处理建议，禁止输出敏感鉴权信息、HTTP 请求地址、方法、参数、请求头、请求体、curl、完整命令或其它请求上下文。

## 命令执行与结果处理

命令支持时优先追加 `--json`。

所有 `moma <service> ...` 命令必须作为宿主直接命令执行工具中的**顶层进程**运行。禁止通过远端业务 API `execute_command` / `execute_code`、Python/Node subprocess、`os.system`、`sh -c`、`shell=true` 等包装层再次调用 `moma`。这是命令可审计性约束：必须保留原始命令、stdout、stderr 和退出码；适用通用协议时还要保留请求预演与真实请求之间的参数绑定。不要表述成“所有包装方式都必然吞掉 exit 10”。

执行 `moma ... --json` 后，必须同时检查 stdout、stderr 和退出码。

- stdout：命令正常结果、状态结果或业务响应。即使退出码非零，也要读取并按内容处理。
- stderr：命令执行错误。
  - `{ "ok": false, "error": { ... } }`：基础命令错误。
  - `{ "status": "error", "code": ... }`：Gateway CLI 错误。
  - 执行 `moma <service> api` 时，其它内容表示业务接口返回的原始错误响应。

`auth check` 登录态不可用、`doctor` 检查失败、升级或卸载部分成功时，会在 stdout 返回完整结果，同时使用非零退出码；不得只根据退出码丢弃结果。

任何情况下都不得输出 Moma API Key、AccessToken、RefreshToken 或完整鉴权头。

## 更新检查

MOMA CLI 支持同时检查 CLI 与 MOMA Skills 更新。

只检查更新，不执行安装或同步：

```bash
moma upgrade --check --json
```

执行更新时使用：

```bash
moma update --json
```

`moma update` 是 `moma upgrade` 的别名。

规则：

- `moma upgrade --check --json` 只检查 CLI 与 MOMA Skills 是否存在更新，不执行安装或同步。
- `moma update --json` 会执行 CLI 与 MOMA Skills 更新；JSON 输出中会分别展示 CLI 与 MOMA Skills 的更新结果。
- CLI 版本与 MOMA Skills 版本是两个独立版本，不要强行认为二者一致。

## 页面生命周期窄范围例外

仅当具体业务 Skill 已加载，且页面生成、导入、克隆或编辑任务已通过 `moma-space/page/entry.md` 建立具体页面上下文时，用户对整个页面生命周期的请求构成该窄范围流程的预授权。Database、附件、关系和发布操作必须服务于该具体页面任务；独立资源管理不适用本例外。对目标、接口和业务参数均已明确的 API 直接执行；`risk: "write"` / `risk: "high-risk-write"` 的写调用第一次就携带 `--yes`，不运行请求预演、不展示同意预览，也不等待额外同意。若意外收到退出码 `10` 或 `GATEWAY_CONFIRMATION_REQUIRED`，使用相同 API 和完全相同的业务参数补 `--yes` 直接重试一次。

目标、接口或参数不明确时，仍须做必要的意图解析、API 名单核对或 schema discovery，禁止猜测。登录、权限、敏感信息、未知 API/参数校验、顶层进程和安全临时目录规则不受此例外影响。除该页面路由外，所有场景继续遵守下方安全规则与通用协议。

## 安全规则

- 禁止输出 Moma API Key、AccessToken、RefreshToken、完整 `Authorization` 请求头、完整 `Moma-Token` 请求头、完整 `Moma-Auth` 请求头或其它密钥、token、cookie、鉴权头。
- 除上述页面生命周期窄范围例外外，写入、删除、批量操作或其它可能产生业务副作用的 API，必须核对用户意图。
- 除上述页面生命周期窄范围例外外，危险请求使用请求预演选项生成预览。

## 高风险操作的审批协议（exit 10）

moma CLI 对写入/高风险写操作（`risk: "write"` / `risk: "high-risk-write"`）通常有强制同意门禁；上述页面生命周期窄范围例外直接使用 `--yes`。

除上述页面生命周期窄范围例外外，当 `risk: "write"` 或 `risk: "high-risk-write"` 时，本次命令执行必须完成以下通用流程：

**在原命令末尾追加 `--dry-run` 生成预览 → 展示预览 → 获得明确确认 → 移除 `--dry-run` 并追加 `--yes` 发起真实调用**

当命令为写入/高风险写操作（`risk: "write"` / `risk: "high-risk-write"`）且未追加 `--yes` 时，CLI 将以退出码 10 结束，并向 stderr 输出以下结构化错误：

```json
{
  "status": "error",
  "code": "GATEWAY_CONFIRMATION_REQUIRED",
  "message": "API \"POST_api_xxx\" 风险级别为 write，需要确认后才能执行",
  "hint": "请先在原命令末尾追加 --dry-run 预览本次调用影响，确认无误后追加 --yes 执行",
  "risk": {
    "level": "write",
    "action": "moma <service> api <apiName>"
  }
}
```

满足以下任一条件时，识别为审批门禁：

- 进程退出码为 `10`。
- stderr JSON 中的 `code` 为 `GATEWAY_CONFIRMATION_REQUIRED`。

识别门禁时，同时读取退出码、stdout 和 stderr；不得因为退出码非零而忽略结构化错误。

退出码 `10` 只表示 CLI 拒绝执行未携带放行参数的高风险操作。页面生命周期窄范围例外按上文用相同参数补 `--yes` 重试一次；其他场景继续执行下方通用流程，不得直接追加 `--yes`。

### 判断是否需要通用流程

如果尚未明确本次执行命令的风险级别时，执行以下命令获取：

```bash
moma <service> schema <apiName> --json
```

读取输出中的 risk，按以下规则处理：

- risk 为 read：可以直接执行。
- risk 为 write 或 high-risk-write：页面生命周期窄范围例外直接加 `--yes`，其他场景进入通用流程。
- risk 为 null、空字符串或纯空白字符串：按 read 处理。
- 其它非空值：停止执行，不得追加 --yes。

注意：
- 禁止盲目推断或假设 risk 值；
- 如果已经明确获取本次调用的风险级别，可以直接使用该值判断是否需要通用流程，无需再次执行命令重复获取；
- 如果 risk 字段缺失或无法识别，必须执行 `moma <service> schema <apiName> --json` 获取 risk 字段；

### 通用流程

1. **生成预览**

  - 以原调用命令为基础，保持 `<service>`、`<apiName>` 和所有业务参数不变。
  - 确保预览命令不包含 `--yes`、`--dry-run` 或 `--dry_run`。
  - 如果原命令包含 `-o` / `--output`，暂存并移除该选项。
  - 在命令末尾追加 `--dry-run` 并执行。

2. **生成确认提示**

  - 同时检查预览命令的退出码、stdout 和 stderr。
  - 预览失败，或 stdout 中 `api[0].risk` 无法识别时，停止执行，不得追加 `--yes`。
  - 预览成功时，根据具体 Skill 和预览结果生成简短确认提示，用自然语言说明将执行的操作、影响对象、预期变化和风险，只展示会影响用户决定的业务信息。
  - 只允许使用用户诉求、预览结果和具体 Skill 中能够确认的信息生成简短确认提示，禁止盲目推测未确认的业务含义。
  - 禁止展示真实请求地址、鉴权请求头、curl 、完整调用命令、API 名称、risk 枚举、请求参数或执行机制。

3. **等待用户确认**

  - 等待用户通过 UI 确认卡或语言作出与最近一次预览绑定的明确决定。
  - 成功完成的预览工具轨迹可能触发宿主展示 UI 确认卡；退出码 `10` 本身不会触发确认，也不表示确认卡已经展示。
  - 宿主未提供确认卡时，使用语言请求用户明确确认。
  - 用户明确同意执行刚刚说明的操作后，进入第 4 步。
  - 用户拒绝、未明确同意或无法确认回复对应哪次预览时，停止执行。
  - “好的”“继续”“你弄吧”等无法明确绑定本次预览的回复不算确认。

   宿主可能使用以下固定文本传递 UI 确认结果：

  - `同意执行（--yes）`：表示用户同意执行最近一次预览，进入第 4 步。
  - `不同意（--no）`：表示用户拒绝执行，立即停止。

   `--no` 只表示用户拒绝，不是需要传给 CLI 的命令行选项。不得假设所有宿主都使用相同的确认文案。

4. **发起真实调用**

  - 用户明确同意后，以最近一次预览命令为基础重新构造命令。
  - 保持 `<service>`、`<apiName>` 和所有业务参数不变。
  - 移除 `--dry-run` / `--dry_run`，恢复暂存的 `-o` / `--output`，并追加 `--yes`。
  - Agent 只执行一次重新构造的调用命令。
  - 业务参数发生变化时，原确认立即失效；不得执行真实调用，返回第 1 步重新生成预览并再次确认。

### 禁止事项

- 除页面生命周期窄范围例外按上文重试一次外，不得根据退出码 `10` 自动追加 `--yes`。
- 除页面生命周期窄范围例外不需要预览或额外同意外，不得在预览成功前请求用户确认。
- 不得把 `GATEWAY_CONFIRMATION_REQUIRED` 当成网络、鉴权或权限错误。
- 通用流程不得同时使用 `--dry-run` 和 `--yes` 发起真实调用；页面生命周期窄范围例外不执行预演。
- 不得在用户确认后修改业务参数。
- `--dry-run` 是 CLI 选项，body 中的 `dry_run` 是业务字段；是否修改业务字段以具体 Skill或 reference 为准。
- 预览失败或 `risk` 为非空未知值时，停止执行，不得追加 `--yes`。
- 不得通过 shell、subprocess 或其它包装层绕过原始命令执行。


### 如何识别一条命令需要通用流程

- `moma <service> schema <apiName> --json` 返回 `"risk": "read"`：可直接执行。
- `moma <service> schema <apiName> --json` 返回 `"risk": "write"` 或 `"risk": "high-risk-write"`：页面生命周期窄范围例外直接携带 `--yes`，其他场景按本通用协议处理。
- `risk` 未知，或 dry-run 返回 `risk: "unknown"`：停止，不要追加 `--yes`。
- `moma <service> api <apiName> --json` 返回 `GATEWAY_CONFIRMATION_REQUIRED`：页面生命周期窄范围例外按上文重试一次，其他场景进入通用流程。
