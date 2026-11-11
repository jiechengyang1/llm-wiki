---
name: moma-data
description: "moma data：查询指标、Hive、模型、奥丁、Excel 和报告组件资产；通过云端 CLI 创建、预览、发布数据资产，配置 Hive 定时同步、分片及索引；管理个人 supabase 实例。用户请求取数、创建资产、发布或调整资产同步配置时使用。"
---

# 使用准则

**CRITICAL — 本 Skill 的 `<service>` 固定为 `moma-data`。所有命令必须使用 `moma moma-data ...`。**
**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../moma-shared/SKILL.md`](../moma-shared/SKILL.md)，其中包含登录、权限处理、更新和安全规则。**
**CRITICAL — 本业务 Skill 只能补充业务域规则，不得覆盖或放宽 `moma-shared` 中的登录、权限、敏感信息和高风险确认要求。**
**CRITICAL — 获取数据时必须先调用资产接口获取 #{data_asset}，再决定取数 flow。创建/发布资产、配置/执行同步走下面的资产管理流程；个人 supabase 实例管理走 `personal supabase core flow`，这两种意图不经过取数资产匹配。**

# 创建资产、发布及同步配置

用户要求「把 SQL/指标保存为资产」「创建资产并发布」「设置定时、分片、重试或索引」「立即同步」时，先读 [`reference/data_asset_management/index.md`](reference/data_asset_management/index.md)，使用 `/moma-data/cli/asset-management` 的云端 API。

接口按操作分类，按需阅读：

| 操作 | 接口参考 |
|---|---|
| 查询 | [资产列表](reference/data_asset_management/query/list_assets.md)、[资产详情](reference/data_asset_management/query/get_asset.md) |
| 创建 | [权限预检](reference/data_asset_management/create/precheck.md)、[Hive](reference/data_asset_management/create/create_hive.md)、[Hive 草稿回写](reference/data_asset_management/create/update_hive.md)、[指标](reference/data_asset_management/create/create_metric.md)、[模型](reference/data_asset_management/create/create_data_model.md)、[奥丁取数](reference/data_asset_management/create/create_odin_fetch.md)、[Excel 上传](reference/data_asset_management/create/upload_excel.md)、[Excel 保存](reference/data_asset_management/create/create_excel.md) |
| 发布 | [安全告知](reference/data_asset_management/publish/requirements.md)、[候选检测](reference/data_asset_management/publish/preflight.md)、[发布资产](reference/data_asset_management/publish/publish_asset.md) |
| 同步 | [读取配置](reference/data_asset_management/sync/get_config.md)、[保存定时/分片/索引](reference/data_asset_management/sync/configure.md)、[立即执行](reference/data_asset_management/sync/run.md)、[执行状态](reference/data_asset_management/sync/status.md) |

- 交付环境使用 `moma moma-data api <apiName> --json`；不要调用本地 `node dist`、`asset create` 等 TS 子命令，它们不随云端 CLI 部署。
- 新建资产：数据源权限预检 → 当前参数查询预览 → 保存草稿；用户要求发布时再按参考完成安全告知、候选检测及发布。不能把已有同名资产的查询结果作为新资产预览。
- Hive 保存或回写时由服务端以当前用户身份重新预览并写入快照，不需要也不采信请求里的 `response`、`preview_verified`；指标的 targets/params 变化后重新查询，不能虚构 `response`。
- Hive 支持定时、全量/增量、时间/取模分片、索引、重试及通知；指标只做预览、保存、发布，不设置或执行同步。
- 保存草稿、发布、开启定时任务、立即同步是不同动作，按用户意图执行；安全告知及检测风险需要按接口返回处理，不能自动勾选确认。
- 这套通用创建接口独立于个人数据专家的确认卡导入流程；不要用 `/cli/data-assets/hive-query` 代替普通 Hive 保存。

# 获取数据方式（必须按顺序执行，不可跳步）

以下 Step 仅适用于取数意图；资产管理按上节执行。

**个人 supabase 实例管理（与资产查询完全独立，优先判断）**：

判断用户的操作意图是否为对**个人 supabase 实例**进行操作（建表、改表、创建函数、执行 migration、管理 Storage 桶、查询个人实例表结构等）→ 若是，**直接进入 `personal supabase core flow`**，跳过以下所有 Step。

## Step 0：【必做，任何情况不可跳过】先获取数据资产列表

在做任何其他操作之前，**必须先**获取数据资产，记为 #{data_asset}，获取方式二选一：

**方式 A（上下文中已有 asset_id）**：用户明确提供了资产 ID，或上下文中已缓存过 asset_id → 参照 reference/data_asset/data_asset_by_ids.md，直接按 ID 批量拉取，跳过全量列表拉取。⚠️ **查询参数名是 `ids`（不是 `asset_id` 或 `asset_ids`）**，示例：`-q "ids=101,202,303"`。

**方式 B（常规情况）**：参照 reference/data_asset/data_asset_accessible.md 调用接口，获取当前用户所有可访问的数据资产列表。

然后尝试将用户需求与 #{data_asset} 中的资产做语义匹配（参照 `data asset core flow` 中的 Step1 匹配规则）：

- **命中资产** → **无论用户输入是否包含"奥丁"、"odin"、UUID 等关键词，一律直接进入 `data asset core flow`，绝对禁止走下面的路由判断**
- **未命中资产** → 按下面的关键词路由规则选择对应 flow

## Step 1：未命中资产时，按关键词路由

仅当 Step 0 未匹配到任何资产时，才按以下规则路由：

1、当用户明确谈及指标、魔方、index、metric等关键信息、或者输入获取数据的需求中包含数字时，需要使用`index api use core flow`获取数据；

2、当用户输入包含sql、表名等相关的内容时，推荐使用`hive api use core flow`获取数据;

3、当用户输入包含数据模型、数据模型Id时，推荐使用`model api use core flow`获取数据;

4、当用户输入包含奥丁、odin时候，或类似`aed93402-24ba-4cdd-a53c-260939014547`这样长字串时，推荐使用`odin_fetch api use core flow`;

5、以上均无法匹配时，通过 AskUserQuestion 询问用户希望通过哪种方式获取数据（指标查询 / Hive SQL / 数据模型 / 奥丁取数）。


# 命令格式

```bash
moma <service> api <apiName> --json [options]
```
| 选项 | 格式 | 说明 |
|------|------|------|
| `-p` | `key1=v1&key2=v2` | 路径参数 |
| `-q` | `key1=v1&key2=v2` | Query string，多个字段拼在一起传 |
| `-d` | `'{"key":"val"}'` | 请求 body，所有字段合并为**一个** JSON 字符串 |
| `-H` | `Key:Value` | 请求头，可多次使用 |

调用 `moma moma-data api` 查询指标列表、维度、枚举值和指标数据时，必须追加 `--json`，以便稳定解析接口原始返回内容。

# data asset core flow 

## Step1：尝试匹配出与用户取数需求的相关资产

用户已 @ / 指定组件资产 ID 时，以该组件为准，不得改选源模型。by-ids 无返回、无授权或查询失败时停止该组件取数，不进入关键词兜底。页面入口为「奥丁报告 → 报告名 → 组件资产」；目录分组不改变资产授权。

**资产匹配原则：按照以下优先级依次尝试，一旦命中即停止向下匹配（优先级：team_name > tag > name/description）**

**数据来源**：使用当前上下文中的 #{data_asset} 列表（`by_team` / `by_tag` / `untagged` 三组），若上下文中不包含资产列表，需先参照 reference/data_asset/data_asset_accessible.md 调用接口获取。

**去重说明**：`by_tag` 与 `untagged` 中同一资产可能出现多次（同一资产打了多个标签），以 asset_id 去重后再进行下一步。

---

**情况1**：如果用户诉求能通过 `by_team[].team_name` 命中，提取对应 team 下的 `items`，记为 #{data_asset_list}

（允许同时匹配多个 team_name）

举例：
```
user: "获取数据分析团队下所有数据"
agent: 发现 by_team 中 team_name="数据分析团队" 命中，提取其 items，记为 #{data_asset_list}
```

**情况2**：若情况1无法命中，尝试通过 `by_tag[].tag` 匹配，提取对应标签下的 `items`，记为 #{data_asset_list}

（允许同时匹配多个 tag）

举例：
```
user: "获取业绩分析下所有数据"
agent: 发现 by_tag 中 tag="业绩分析" 命中，提取其 items，记为 #{data_asset_list}
```

**情况3**：若情况1和情况2均无法命中，将 `by_tag[].items`、`untagged`、`by_team[].items` 合并后按 asset_id 去重，再通过 `name`、`description` 字段与用户需求做语义匹配，提取最相关的资产记为 #{data_asset_list}

**兜底**：若三种情况均无法匹配到任何资产，通过 AskUserQuestion 询问用户希望通过哪种方式获取数据（指标查询 / Hive SQL / 数据模型 / 奥丁取数），再按对应的 core flow 继续执行。

---

## Step2：根据匹配的资产列表获取实际的数据

根据 #{data_asset_list} 中每条资产的 `asset_type`，决定使用哪个 core flow 获取数据。

**组件选择**：report_component 优先用户明确选中的组件；同名组件核对 report_id/report_name，不明确时只问一次。不要因为报告名命中就查询所有组件或源模型。

**多资产处理**：若 #{data_asset_list} 包含多条资产，依次逐条获取数据，汇总后一并呈现给用户；若资产数量较多（>3条），先通过 AskUserQuestion 让用户确认是否全部获取。

**公共注意事项**：从资产命中后发起的查询，必须把该资产的 `asset_id` 带到对应查询指令里。不是从资产命中、直接查模型 / Hive / 指标 / 奥丁时，不要传 `asset_id`。

| 资产类型 | 查询指令 |
|---|---|
| data_model（同步或异步） | `model_query` / `model_query_async` 带 `asset_id` |
| hive（意图 A 取数、意图 B 探查都算） | `execute-sql` 带 `asset_id`；下载同一个 `queryId` 时也带这个 `asset_id` |
| metric | `index_query` 带 `asset_id` |
| odin_fetch | 预览和全量下载都带 `asset_id` |

**⚠️ CRITICAL — 取数路径速查表（每次进入 Step2 必须对照此表，禁止偏离）**：

| asset_type | supabase 快照 | 取数 flow |
|---|---|---|
| hive | ✅ 优先走 | hive api use core flow（快照不可用时回落） |
| odin_fetch | ✅ 优先走 | odin_fetch api use core flow（快照不可用时回落） |
| **data_model** | ✅ **优先走（若已同步）** | **model api use core flow（快照不可用时回落）** |
| **metric** | ❌ **无快照，严禁尝试** | **直接走 index api use core flow** |
| excel | ✅ 只有快照 | supabase snapshot core flow（不能回落实时） |
| **report_component** | ❌ 无独立快照 | **只走 `POST_moma-data_cli_report-components_query`** |

---

### asset_type = "report_component"

必须先读 [`reference/report_component/report_component_query.md`](reference/report_component/report_component_query.md)。
组件是已发布看板的版本化查询引用，即使源模型已同步到 Supabase，也不能改查源表。

- 复用本回合 detail.query_body 的目录 asset_id 和 version，按 detail.filters 组织 selections；lite 列表或详情缺失时先按 ID 获取详情，不猜版本。
- detail.source_sync 仅供前端 @ 选择守卫使用；Agent 不基于该字段输出额外同步提示。
- 只用 `moma moma-data api POST_moma-data_cli_report-components_query --json`，body 为 asset_id/version/selections；筛选枚举用同一接口的 option_filter。
- 原始结果读取 data.rows/data.columns，按列标签、原单位展示；restricted=true 如实说明行级范围无数据，truncated=true 不能当作全量再聚合。
- 401/403/409/503 或业务错误立即按实际错误说明；不能换创建人身份、查 owner-table/model、supabase-tables 或直连 Supabase。
- 登录规则沿用 moma-shared。用户在数据资产页点击「获取有权限的报告 / 刷新报告」后，已录入且发布的报告组件会进入个人「奥丁报告」目录；无需维护人逐个分享。读取目录不会扫描 Odin。每次取数仍实时校验当前访问者的 Odin 报告 view 权限，并继承源资产行级规则；应用/助手绑定范围继续生效。目录缓存不代表实时授权。

---

### asset_type = "metric"

> ❌ **无 supabase 快照，直接走 `index api use core flow`，禁止尝试 supabase snapshot core flow。**

参照 `index api use core flow` 获取数据，复用 `detail` 中的参数：
- `targets`：直接作为查询的 targets 入参
- `params`：作为查询参数的基础（dateType、dim 等可直接复用），**包括 filter 字段也直接复用，不要重新构造 statistical_name 筛选**

**注意**：
- `end_date` 需根据当前调用时间生成最新日期，不复用 detail 中保存的旧 end_date
- `asset_id` 必须带到 index_query。不是从资产命中的指标查询不传
- 判断统计口径：检查 `detail.custom_mapping.periodMode`
  - `periodMode === "general"`（通用周期）：指标按自然日历统计，**不含 `statistical_name` 维度**，直接用时间范围查询即可，禁止向 filter 中追加 `statistical_name` 条件
  - `periodMode === "business"` 或字段不存在（业务口径，默认）：需在 filter 中保留 `statistical_name` 条件，已包含在保存的 `params.filter` 内

---

### asset_type = "hive"

**优先走 `supabase snapshot core flow`**（已同步则优先走它，见该 flow 的判定）；快照不可用时才回落到 `hive api use core flow` 场景A 处理。

**⚠️ 先检查 `allow_probe`**：若资产的 `allow_probe == 0`，**禁止走意图B（探查）**，也**禁止从 supabase snapshot core flow 回落到实时取数**；快照不可用时应告知用户"该资产已禁止探查原始数据源，请联系资产负责人开启 supabase 同步后再查询"，流程终止。

**根据用户意图二选一，不可混用：**

**意图A（取数）**：用户要获取数据、查看结果、导出 → `⚠️ CRITICAL：detail.raw_sql` 即等同于"用户已提供完整 SQL"，直接进入场景A执行，**严禁走场景B重新探测表结构**。复用 `detail` 中的参数：
- `raw_sql`：直接作为 #{sql}，跳过 Step1/Step2/Step3，从格式化 SQL 开始执行
- `odin_cluster`：透传到 execute-sql 的集群参数
- `asset_id`：**必传**，带到 execute-sql；缺失则以当前用户权限执行，可能因无直接表权限而失败

**意图B（探查）**：`allow_probe == 1` 且用户明确表达想探查表结构、查看字段、自定义筛选条件、了解数据分布等（如"这张表有哪些字段"、"帮我看下明细"、"我想自己筛一下"）→ 从 `raw_sql` 中提取主表名（FROM 子句第一张非 dim 表）作为 #{table_code}，**直接跳入 `hive api use core flow` Step2**（跳过 Step1 表匹配，已知表名），按用户需求重新构造 SQL。

**注意**：
- 意图A：若用户未指定时间范围，且 raw_sql 中的分区条件是**硬编码日期**（如 `pt='20260901'`），需根据当前时间自动修改为最新分区；**若分区条件已是 Odin 变量形式**（如 `pt='${-1d_pt}'`、`pt='${-2d_pt}'`），说明用户意图已通过变量表达，**直接使用原 SQL，禁止替换**，除非用户明确反馈数据不对
- 意图不明确时，默认走意图A（取数），不要主动切到意图B
- 从这份资产出发的 execute-sql，意图 A 和意图 B 都要带 `asset_id`。意图 B 自己构造 SQL 时也不能拿掉

---

### asset_type = "data_model"

**优先走 `supabase snapshot core flow`**（已同步则优先走它，见该 flow 的判定）；快照不可用时才回落到 `model api use core flow`，复用 `detail` 中的参数：
- `model_id`：目标模型 ID
- `cluster_type`：上游集群类型，需按 model_list.md 的映射规则转换为 `odinCluster`（`default/finance/hfc → public`，`secret → high_confidential`）
- `query_params`：作为查询参数的起点，可按用户需求进一步调整

**注意**：回落到 `model_query` 或 `model_query_async` 时，必须带这个资产的 `asset_id`。

---

### asset_type = "odin_fetch"

**优先走 `supabase snapshot core flow`**（已同步则优先走它，见该 flow 的判定）；快照不可用时才回落到 `odin_fetch api use core flow`，`detail` 为数组，每条包含：
- `request_id`：奥丁取数请求 UUID
- `date_params`：日期参数，可作为参考，但需结合用户当前需求重新确认时间范围

**注意**：`asset_id` 必须携带到查询指令中

---

### asset_type = "excel"

Excel 资产的数据源是用户上传的 xlsx/csv 文件；发布时后端将文件解析同步到用户 supabase 的 `excel_{asset_id}` 表，agent 通过 `supabase snapshot core flow` 读取该表取数。

**Excel 的同步模型**：

- **发布触发同步**：资产发布时后端异步触发一次同步任务，同步过程用户可见 `sync_status`
- **`enabled` 恒为 0**：Excel 表示"无定时任务"；资产可用性判断只看 `sync_status`
- **失败自动回退发布态**：同步失败时后端把 `data_asset.state` 从 2 回退到 1（草稿），并 DROP 属主实例上的半成品表；重试路径是资产负责人在资产页**重新发布**，agent 直接引导用户去重新发布

**Step1 拿表名之后按 `sync_status` 分派**：

| `sync_status` | 语义 | agent 动作 |
|---|---|---|
| `success` | 同步已就绪 | 继续 Step2 摸列名、Step3 查数据 |
| `running` / `pending` | 同步进行中 | 告知用户"资产同步进行中，请稍等 xx 秒后重试"，流程终止 |
| `failed` | 同步失败，资产已回退到草稿态 | 告知用户"资产同步失败：{error_message}，请让资产负责人检查后重新发布"，流程终止 |
| `tables` 为空 | 从未同步成功 | 同 `failed` 处理 |

从 `detail` 复用：

- `file_name` / `file_type`（`xlsx` / `xls` / `csv`）/ `sheet_name`：识别数据源，向用户说明数据来自哪个文件的哪个 sheet
- `column_definitions`：字段结构数组，每项 `{name, orig_name, type}`
  - `name`：入库到 supabase 的字段名（中文原名经 pypinyin 拼音化，如 `yue_fen`）
  - `orig_name`：原始列名（可能是中文，如 `月份`）
  - `type`：`str` / `int` / `float` / `bool`
  - **展示给用户时用 `orig_name`；查询 `table-rows` / `table-aggregate` 时用 `name`**
- `row_count`：解析时的总行数

**要点**：

- `asset_id` 必须携带到查询指令中
- 目标表名形如 `excel_{asset_id}`（区别于 `excel_asset_{id}`）；实际以 `data_asset_supabase_tables` 返回的 `target_table` 为准
- 若 `warnings` 里出现 `EXCEL_COMPLEX_LAYOUT`（合并单元格），后端已按"第一层维度"扁平化解析，结果只包含首层信息；如用户认为结果与预期有偏差，提示"该 Excel 结构复杂，建议资产负责人重上传扁平二维表"

# supabase snapshot core flow

适用范围：**`hive` / `odin_fetch` / `data_model` / `excel` 四类资产**（`metric` / `report_component` 没有独立快照表，不要走本 flow；组件只走专用查询接口）。

这四类资产的数据会以不同节奏同步到 supabase 快照表。**优先查快照**，理由：

- **快**：一次 REST 查询即得，不用提交 Odin 任务再轮询；
- **不要求你对原表有权限**：快照是以资产负责人身份同步的，你只需对**资产**有权限；
- 行级数据权限由服务端自动注入，你不需要也不能自己加。

报告导入的模型默认仅保存元数据、不自动同步；@ 看板组件必须调用 report_component 接口，不能因模型无快照而阻止组件实时查询。普通资产仍沿用以下快照流程。

四类资产的同步节奏不同：`hive / odin_fetch / data_model` 走定时同步（`enabled=1 + crontab`），`excel` 走"发布即同步"（`enabled=0` 是正常态，同步在发布时一次性触发）——所以下面 Step1 的判断要按类型分开。

## Step1: 拿表名 & 判断快照可用

must refer to reference/data_asset/data_asset_supabase_tables.md

传入 Step1 匹配到的 `asset_id`，从 `data.tables` 里判断——**规则因资产类型而异**：

**hive / odin_fetch / data_model**：

快照表的可用性由 `last_sync_at` 决定，而非 `sync_status`：`running`/`staged` 同步进行中目标表仍保有上一次完整数据；`failed`/`cancelled` 同步未完成但 staging 已清理、目标表同样完好——只要曾成功过一次（`last_sync_at` 非空），历史快照就可查。

- `tables` 为**空数组** → 该资产没开同步 → **回落**到对应实时取数 flow（`allow_probe==0` 时禁止回落，直接告知用户）
- `last_sync_at` 为空 → 从未同步成功，快照无数据 → **回落**到实时取数 flow（`allow_probe==0` 时禁止回落）
- `last_sync_at` 非空 → **历史快照存在，可查**，按 `sync_status` 决定提示语：
  - `success` → 数据完整最新，直接进入 Step2
  - `running` / `staged` → 正在更新中，告知用户"同步进行中，当前数据截至 {last_sync_at}"，仍进入 Step2
  - `failed` / `cancelled` → 上次同步未完成，告知用户"上次同步失败/已取消，当前数据截至 {last_sync_at}"，仍进入 Step2
  - `pending` → 等待执行，同 `failed`/`cancelled` 处理
- `enabled == 0` 且 `last_sync_at` 非空 → 同步已关闭，数据停止更新，告知用户后仍可查历史快照
- `last_sync_at` 明显早于用户要求的数据时点（用户说"今天/最新"但快照是几天前）→ 告知快照时间，并**回落**到实时取数 flow（`allow_probe==0` 时禁止回落）

**excel**（数据只在 supabase 快照表中；`enabled=0` 表示"无定时任务"，属于正常状态）：

Excel 每次发布触发一次同步；失败时后端自动 DROP 目标表并回退到草稿态，因此 `last_sync_at` 非空才代表快照可用。

- `sync_status == "success"` → 取 `target_table`，进入 Step2
- `sync_status ∈ (running, pending)` 且 `last_sync_at` 非空 → 重新发布中，历史版本可查，告知用户"同步进行中，当前数据为上一版本（{last_sync_at}）"，进入 Step2
- `sync_status ∈ (running, pending)` 且 `last_sync_at` 为空 → 首次同步尚未完成，告知用户"资产同步进行中，请稍等重试"，流程终止
- `sync_status == "failed"` 或 `tables` 为空 → 目标表已被 DROP，告知用户"资产同步失败：{error_message or '未同步成功'}，请让资产负责人检查后重新发布"，流程终止
- `last_sync_at` 对 excel 仅作版本信息展示，无需做时效性回落

⚠️ **`allow_probe==0` 时不得回落到实时取数**：快照不可用时应直接告知用户"该资产已禁止探查原始数据源，请联系资产负责人开启 supabase 同步后再查询"，流程终止。

odin_fetch 资产可能返回**多张表**，按 `config_desc` 匹配用户需求；分不清用 AskUserQuestion 让用户选，不要默认取第一张。

⚠️ 表名一律用返回的 `target_table`，**不要自己按 `hive_asset_{id}` / `excel_{id}` 拼**。

## Step2: 摸清列名

must refer to reference/data_asset/data_asset_table_rows.md

先查前 10 行看真实列名，**不要凭资产名或 raw_sql 猜列名**：

```bash
moma moma-data api GET_moma-data_cli_data-assets_table-rows --json \
  -q "asset_id=#{asset_id}&table=#{table}&select=*&limit=10"
```

记录真实列名，记为 #{columns}。若用户需求涉及的字段不在 #{columns} 里，告知用户该表无此字段。

## Step2.5: 构建列名中文映射

must refer to reference/data_asset/data_asset_table_columns.md

调用 `table-columns` 接口，直接从 Supabase 快照表的 `information_schema.columns` 获取列的 PostgreSQL 注释：

```bash
moma moma-data api GET_moma-data_cli_data-assets_table-columns --json \
  -q "asset_id=#{asset_id}&table=#{table}"
```

用返回的 `data` 数组构建 #{col_display_map}：
- `comment` 非空 → 用 `comment` 作为展示名
- `comment` 为空串 → 保留 `name`（英文列名）

```
#{col_display_map} = {col.name: col.comment if col.comment else col.name}
```

⚠️ 在 Step3 展示数据时，**必须用 #{col_display_map} 将列名替换为中文显示名**再呈现给用户；`name` 以 `sys_` 开头的同步元数据列（如 `sys_created_at`）过滤掉不展示。

## Step3: 按需求查数据

先判断要**明细**还是**聚合**，两条路用不同接口：

### 3a. 要明细行 → table-rows（PostgREST 语法）

语法表见 reference/data_asset/data_asset_table_rows.md：

- 选列：`select=col_a,col_b`；过滤：`city=eq.北京市`；排序：`order=stat_date.desc`
- **永远带 `limit`**（快照表可能几十万行）；需要分页用 `limit` + `offset`（这里支持 offset）
- 只要总行数：`select=count`

### 3b. 要聚合值 → table-aggregate

must refer to reference/data_asset/data_asset_table_aggregate.md

用户问「各城市总量」「按月趋势」「有多少家门店」这类**汇总**需求时走这条，让数据库算好只回传结果行：

```bash
moma moma-data api POST_moma-data_cli_data-assets_table-aggregate --json \
  -d '{"asset_id":#{asset_id},"table":"#{table}","dims":[{"field":"city"}],"metrics":[{"agg":"SUM","field":"cnt"}],"limit":50}'
```

⚠️ **不要用 table-rows 拉明细回来自己加** —— 快照表可能几十万行，拉回终端既慢又容易超限。仅支持单表聚合（无 JOIN / 子查询）；日期列是 TEXT（如 `20260814`）做时间粒度时必须给 `dateFormat`。

两条路的返回都是**行数组**（**没有** `list` 嵌套），以表格或摘要呈现给用户。

错误处理：`errmsg` 里的 `OWNER_ASSET_TABLE_*` / `ASSET_AGG_*` 错误码**原样透传给用户**，「无权 / 已下线 / 未同步完成 / 参数写错」是完全不同的后续动作，对照 reference 里的错误表处理。

# index api use core flow 

## Step1: 获取用户可访问指标列表 & 确定用户想查询的指标

获取这个人有权限的指标列表: must refer to reference/index/index_list_usage.md(这个是分页接口，无法精准匹配时，需要遍历获取所有指标)

指标匹配原则:

1、通过指标名、指标描述等，匹配出用户最相关的指标;

2、优先级原则

indexLevel字段代表指标等级：3——集团级、2——条线级、4——部门级、1——普通级，匹配优先级：3 > 2 > 4 > 1

authenticationStatus字段代表指标认证状态: 认证状态：1——已认证、2——认证中、3——未认证、4——撤销中，匹配优先级：1 > 2 > 3 > 4 

注意: 当无法精准匹配指标时，可以通过AskUserQuestion和用户沟通确认，直到确认完毕.

输出记录为: #{index_id}

## Step2: 获取指标纬度字段 & 纬度枚举

获取指定指标的枚举字段：must refer to reference/index/dims.md

获取指定指标枚举字段的枚举值：must refer to reference/index/dims_enum.md

### Step2.1: 聚合纬度的确定

当用户明确将数据按照某些纬度展开分析时，需要匹配获取到枚举字段中的dimCode

-example:
User: "获取二手单量业绩城市明细数据", 你需要匹配对应的枚举字段，用户是看业绩城市的明细数据，你需要通过 `dimName` 识别"业绩城市"对应的枚举字段，取其 `dimCode` 作为输出

示例输出： dims: ["performance_city_abbr_name"]，记为#{dims}

### Step2.2: 筛选条件的确定

当用户明确筛选某些数据时，需要结合用户需求和枚举字段列表匹配对应枚举字段：dimCode、dimTableCode;

通过枚举值列表，匹配出用户对应的枚举值 (因为用户可能打出wuhan、武汉、武汉市等，你必须找出字段对应的枚举值是啥)

-example:
User: "获取武汉二手单量数据", 你需要匹配出dimCode：performance_city_abbr_name、dimTableCode：dim_coo_leadercockpit_dimension_da， 同时根据dimCode、dimTableCode，获取枚举字段获取对应的枚举值，并匹配

示例输出：

filter: {"type":"and","fields":[{"type":"in","dimension":"performance_city_abbr_name","values":["武汉"]}]}, 记为#{filter}

## Step3: 查询指标数据 & 整理返回数据

在进行下述操作之前，you must refer to reference/index/index_query.md，去了解

### Step3.1 确定时间范围、时间粒度

#### Step3.1.1 时间范围

时间格式：`YYYYMMDD` 纯数字，不带横杠（如 `20111111`）。

-example(无时间诉求)
-用户的需求可能没有携带任何时间相关的描述，如：武汉单量数据, 比如当前时间为：2024-06-23，你只需要将时间范围转为[20240623]到[20240623]

-example(模糊时间诉求)
用户的需求可能是模糊的时间描述，如「今年」、「上个月」、「最近7天」等，你需要根据当前日期来转换成明确的时间范围：
用户的需求可能是明确的时间范围描述，如「2024年1月到3月」，你需要把它转换成时间格式「20240101」到「20240331」

-example(明确时间诉求)
user: "获取武汉二手新签单量今年趋势"，你需要明确用户查询时候的日期，然后转换成时间范围，比如当前日期是2024年6月10日，那么「今年」就转换成「20240101」到「20240610」
user: "获取武汉二手新签单量上个月趋势"，你需要明确用户查询时候的日期，然后转换成时间范围，比如当前日期是2024年6月10日，那么「上个月」就转换成「20240501」到「20240531」
user: "获取武汉二手新签单量最近7天趋势"，你需要明确用户查询时候的日期，然后转换成时间范围，比如当前日期是2024年6月10日，那么「最近7天」就转换成「20240603」到「20240610」

注意：如果你无法从用户的提问中判断出明确的时间范围，你可以使用AskUserQuestion问用户「请问您想查询哪个时间范围的数据？比如今年、上个月、最近7天，或者明确的时间范围等」，直到你拿到明确的时间范围为止。

示例输出："20240101"、"20240610", 记为#{start_date}、#{end_date}

#### Step3.1.2 时间粒度 

时间粒度为固定值："日", "周", "月", "季", "年"

用户的需求可能是模糊的时间粒度描述，如「今年数据」，这时你需要根据用户提问的时间范围来判断时间粒度，如果时间范围在一个月以内，默认日粒度；如果时间范围在一个以上，默认月粒度；只有当明确说了「周趋势」、「日趋势」、「季度趋势」时，才使用周、日、季度粒度
用户的需求可能是明确的时间粒度描述，如「月趋势」、「周趋势」、「日趋势」、「月级别」、「日级别」，这时你需要根据描述来确定时间粒度是月粒度

-example(明确时间粒度诉求)
user: "获取武汉二手新签单量今年的月趋势"，你需要根据描述来确定时间粒度是月粒度
user: "获取武汉二手新签单量今年的周趋势"，你需要根据描述来确定时间粒度是周粒度
user: "获取武汉二手新签单量今年的日趋势"，你需要根据描述来确定时间粒度是日粒度

示例输出："月"， 记为#{time_granularity}

### Step3.2 构造查询参数

1、确定dateType的值，根据time_granularity的值来确定dateType的值，time_granularity可能的值有：日、周、月、季、年，分别对应dateType的值为：1、2、3、5、6, 记为#{dateType}

2、确定pageNo、pageSize的值，默认pageNo为1，pageSize默认不传由接口控制（每页记录条目数：默认1000，最大2000，超2000以2000计算)，除非用户明确提出需要修改pageNo和pageSize的值，否则使用默认值，记为#{pageNo}、#{pageSize}

3、dim时间纬度的确定：根据{dateType}的值来确定dim中需要添加的时间维度，dateType=1时，dim必须加上date；dateType=2时，dim必须加上sun_dt；dateType=3时，dim必须加上month；dateType=5时，dim必须加上quarter；dateType=6时，dim必须加上year, 记为#{time_dim}

4、dim额外分析维度的确定：根据Step2.1输出的#{dims}列表中所有dimCode，以逗号分割的形式添加追加到dim字段，记为#{analyze_dim}

5、filter条件确定(包含：时间纬度筛选、额外纬度筛选), 记为#{filter}

**⚠️ 重要：`statistical_name` 筛选不可自动注入，必须来自资产的明确声明**

判断规则（按优先级）：
- **来自数据资产**（`data asset core flow` 跳转过来）：检查资产的 `custom_mapping.periodMode`
  - `periodMode === "business"` 或字段不存在 → **业务口径**，在 filter 中加入 `statistical_name` 粒度筛选
  - `periodMode === "general"` → **通用周期**，禁止加入 `statistical_name`
- **直接查询（无资产上下文）**：先带 `statistical_name` 查一次；若返回数据为空（`list` 长度为 0），则去掉 `statistical_name` 重试一次；以有数据的那次结果为准

> 理由：指标维度列表中出现 `statistical_name` 不代表该指标支持用它筛选，强行注入可能导致返回空数据。

时间纬度筛选（仅业务口径时追加）:

示例1： dateType=1，业务口径按日粒度统计：
```json
{
    "type": "and",
    "fields":
    [
        {
            "values": ["日"],
            "type": "in",
            "dimension": "statistical_name"
        }
    ]
}
```

额外纬度的筛选: 根据Step2.2输出的#{filter}列表中数据:

示例2： 业务口径 + 额外纬度筛选，dateType=3时：

```json
{
    "type": "and",
    "fields":
    [
        {
            "values": ["月"],
            "type": "in",
            "dimension": "statistical_name"
        },
        {
            "values": ["杭州"],
            "type": "in",
            "dimension": "performance_city_abbr_name"
        },
        {
            "values": ["事业部间"],
            "type": "in",
            "dimension": "brand_name"
        }
    ]
}
```

示例3： 通用周期 + 额外纬度筛选（无 statistical_name），dateType=1时：

```json
{
    "type": "and",
    "fields":
    [
        {
            "values": ["武汉"],
            "type": "in",
            "dimension": "performance_city_abbr_name"
        }
    ]
}
```

通用周期且无额外纬度筛选时，`filter` 字段可以不传。

Step3.2标准输出示例: 记为params

```json
{
  "startDate": "#{start_date}",
  "endDate": "#{end_date}",
  "dateType": "#{dateType}",
  "dim": "#{time_dim},#{analyze_dim}",
  "pageNo": "#{pageNo}",
  "pageSize": "#{pageSize}",
  "filter": "#{filter}"
}
```

### Step3.3 获取数据 & 整理数据

使用 index_query 指令获取数据。从资产命中进入时带 `asset_id`；不是从资产来的查询不传。

targets: #{index_id}
params:  #{params}
asset_id: 从资产命中时传入 #{asset_id}

⚠️ 返回是**双层 `data`**：数据在 `data.data`——行数据 `data.data.list`、列名映射 `data.data.mapping`（英文列名→中文，个别可能为空串）、编码映射 `data.data.codeMapping`；另需判中间层业务 errno（`data.errno` 为字符串 `"0"` 才成功）。**不要写成 `data.list`**。用 `data.data.mapping` 把英文列名换成中文再呈现；详见 reference/index/index_query.md「返回数据」。


# hive api use core flow

## 场景分流

hive 查询分为三种场景，需根据用户输入判断走哪条链路：

### 场景 A：用户已提供完整 SQL（或来自资产 detail.raw_sql）

用户直接给了一条 HiveQL 语句让执行，例如："帮我查一下这个sql：SELECT * FROM rpt.rpt_xxx WHERE pt='20260625' LIMIT 10"；**或由 `data asset core flow` 中 `asset_type = "hive"` 携带的 `detail.raw_sql` 跳转至此**，两者处理方式完全一致。

处理流程：先对用户 SQL 做格式化（多行合并单行、单引号转义为 `'\''`、去掉末尾分号，详见 reference/hive/Post_hive_execute-sql.md「调用前：SQL 格式化」），再调用 `POST_moma-data_hive_execute-sql` 执行。除格式化外不做任何额外处理（不补齐分区、不补齐 LIMIT、不校验权限）。

错误处理：
- 若返回 `errno=100`（表权限校验异常），从 errmsg 中提取无权限表名告知用户；
- 若返回 `errno=1`（相同 SQL 正在执行），告知用户到查询历史中查看；
- 详细错误处理参见 reference/hive/Post_hive_execute-sql.md 中的"常见错误处理"章节。

结果处理：执行完成后，同样进入 **Step4** 进行数据量判断（含自动触发异步下载逻辑），不跳过。

仅在用户明确提出要求时，才做额外处理（如补齐分区条件、调整 LIMIT、导出全量数据等）。

### 场景 B：用户描述取数需求，未提供 SQL

用户用自然语言描述需求，例如："帮我查武汉最近7天的新增房源数据"、"rpt_xxx 这个表有哪些字段"

处理流程：按 Step1 → Step2 → Step3 → Step4 完整流程执行。

### 场景 C：用户需要导出 / 下载查询结果

用户明确要求"导出""下载""存成 Excel/CSV""数据量大要全量文件"等，例如："把这个查询结果导出成 Excel"、"数据太多了帮我下载下来"。

处理流程：先通过 场景 A 或 场景 B 提交查询（execute-sql）拿到 data.queryId，再走 **Step5**（Step5.1 轮询任务进度至完成 → Step5.2 下载文件）。

---

## Step1: 获取用户有权限的表 & 确定用户想查询的表

获取用户有权限的 Hive 表列表：must refer to reference/hive/Get_hive_tables.md（分页接口，无法精准匹配时需遍历所有页）

表匹配原则：

1、通过 tableList[].name（中文名）、tableList[].description（描述）、tableList[].code（物理表名）匹配最相关的表；

2、匹配优先级：有明确业务场景描述的表（description 非空）> 公共模型/参照维表 > 临时表/测试表；

3、dbName 反映表的层级：rpt（应用层）> olap（集市层）> dim（维度层）> ods（贴源层），匹配时优先选择应用层或集市层的表。

注意：当无法精准匹配表时，可通过 AskUserQuestion 向用户确认，直到确认完毕。

输出记录表的 code（物理表名），记为：#{table_code}

## Step2: 获取表元数据 & 列信息

获取表元数据（含分区字段、负责人等）：must refer to reference/hive/Get_hive_table_metadata.md

提取 data.partitionColumn，为分区字段名（常见值为 pt），记为：#{partition_column}

获取表的列信息（含字段名、类型、注释等）：must refer to reference/hive/Get_hive_table_columns.md

提取 data 中每列的 name、dataType、comment，记为：#{columns}

### Step2.1: 获取表最新分区

获取指定表的最新 n 个分区值：must refer to reference/hive/Get_hive_latest-pt.md

- 将 #{table_code} 的值作为查询参数 `table_code` 传入，如 `-q "table_code=#{table_code}&n=1"`；
- 分区值（pt）通常为日期格式 yyyyMMdd（如 20260628），可直接用于 SQL WHERE 条件；
- 默认取最新 1 个分区，若用户需要多天数据，可调整 n 参数；
- 用户有明确时间范围诉求时，根据时间范围换算对应的分区数量。

提取最新分区值，记为：#{latest_pt}

示例输出（单个分区）：`WHERE pt = '20260628'`，记为：#{partition_filter}
示例输出（多个分区）：`WHERE pt >= '20260622' AND pt <= '20260628'`，记为：#{partition_filter}

### Step2.2: 确定查询字段

结合用户需求与 #{columns} 中的字段信息：

1、匹配用户提到的业务字段对应的列名（name），如果字段名不明确，优先通过 comment 匹配；
2、如果用户只需要汇总数据（如 count、sum），仅 SELECT 聚合表达式，不加明细字段；
3、如果用户提到"明细"、"详情"、"列表"，则需要 SELECT 相关明细字段；
4、如果用户需求涉及的字段在 #{columns} 中不存在，提示用户该表无此字段，并建议可能的替代字段或表。

输出 SELECT 字段列表，记为：#{select_fields}

### Step2.3: 确定筛选条件

结合用户需求与 #{columns} 中的字段信息，构造额外的 WHERE 筛选条件：

- 用户指定的筛选条件（如 city_name = '北京'），需匹配 #{columns} 中的列名；
- 如果用户提到的值无法直接匹配（如"武汉"对应 city_code 还是 city_name），通过字段 comment 判断；
- 若通过 comment 仍无法确定列名或取值格式（如"武汉" vs "武汉市"），用 AskUserQuestion 向用户确认，直到确认完毕，不要自行臆测。

输出额外 WHERE 条件，记为：#{extra_filter}

## Step3: 构造 SQL & 执行查询

### Step3.1 构造 HiveQL

将前述步骤的结果组装为完整的 HiveQL：

```sql
SELECT #{select_fields}
FROM #{table_code}
WHERE #{partition_filter}
  AND #{extra_filter}
LIMIT 200
```

注意：
- 默认加 LIMIT 200，防止大数据量返回；仅当用户明确提出更大数据量需求时才调整；
- 字符串字面量用单引号；
- 聚合查询需加 GROUP BY 子句（按非聚合的 SELECT 字段分组）；
- 列名中若有特殊字符，用反引号包裹；
- **Odin 引擎不支持 OFFSET**：禁止写 `LIMIT ... OFFSET ...` 或 `LIMIT m, n`（offset 形式），会直接报错。需要更多数据用 `LIMIT n` 调整规模或走导出流程。

完整 SQL 记为：#{sql}

### Step3.1.1 提交前自检（场景 B 自造 SQL 必做）

后端不做前置语法校验，SQL 由 Odin 引擎执行时才校验。为减少来回，提交前对照前面已取到的元数据自查（这是"对照 schema 自查"，非语法校验）：

- [ ] SELECT / WHERE / GROUP BY 里的字段都出现在 Step2 的 #{columns}（/table/columns 真实字段）中，无拼写臆造；
- [ ] WHERE 带了分区条件 #{partition_filter}，避免全表扫描；
- [ ] 有聚合函数时带了 GROUP BY（按非聚合的 SELECT 字段分组）；
- [ ] 带了 LIMIT（除非用户明确要全量）；
- [ ] 含特殊字符的列名用反引号包裹。

任一项不满足则回到对应 Step 修正后再提交。若提交后仍返回 errno≠0（语法/字段/类型错误），按 reference/hive/Post_hive_execute-sql.md「常见错误」把 errmsg 透传给用户并修正重试。

### Step3.2 执行查询

使用 execute-sql 指令提交查询：must refer to reference/hive/Post_hive_execute-sql.md

- sql 参数传入 #{sql}；
- 从资产命中进入（意图 A 或意图 B）时，必须带 `asset_id`；不是从资产来的 SQL 不传；
- 如需查询高密数据，传入 odin_cluster 参数值为 "high_confidential"。

## Step4: 整理返回数据

查询完成后：

1、提取 data.list 为查询结果行集合；

2、data.list 中的数值字段通常以字符串形式返回，做汇总/计算时需注意类型转换（如将字符串转为数字后求和）；

3、如果 data.warn 不为空，需将告警信息提示给用户；

4、**数据量判断（自动触发异步下载）**：

- 若 `data.list.length < 200`：数据已全量返回，直接展示，流程结束；
- 若 `data.list.length >= 200`：说明实际数据量可能超过当前返回量，**自动进入 Step5 异步下载流程**，无需询问用户，直接触发，并告知用户「检测到数据量较大（返回 N 条），已自动触发全量异步下载」；

5、将结果以易于阅读的格式（表格或摘要）呈现给用户；如果结果超出预期行数或关键数据缺失，可打印 data.queryId 供用户溯源。

## Step5: 异步结果查询 & 数据下载（按需）

适用场景：Step4 检测到 data.list.length = 200（数据量可能超限，自动触发）、用户明确要求导出文件、或 execute-sql 提交后任务异步执行需轮询状态再取数。

### Step5.1: 异步查询结果查询（轮询任务进度）

查询即席任务执行进度：must refer to reference/hive/Get_hive_query_progress.md

- queryId 取自 execute-sql 返回的 data.queryId；
- 提取 data.data.queryStatus 判断任务状态，轮询至完成（FINISHED）后再下载；
- odin_cluster 需与 execute-sql 提交时保持一致。

### Step5.2: 查询数据直接下载

确认任务状态为 FINISHED 后，直接调用下载接口将文件保存到本地：must refer to reference/hive/Get_hive_download.md

- queryId 取自 execute-sql 返回的 data.queryId；
- 本次查询从资产命中时，下载必须带同一个 `asset_id`；
- 默认下载 Excel 格式（fileType=4），文件名使用 `adhoc_<queryId>.xlsx`，保存到 `~/Downloads/` 目录；
- 如需查询高密数据，传入 odin_cluster 参数值为 "high_confidential"；
- 下载完成后，**必须验证文件有效性**（参照 reference/hive/Get_hive_download.md「下载后必须验证文件有效性」），确认非 JSON 错误响应后再告知用户路径及总行数；若验证失败，将 errmsg 完整告知用户。

---

# model api use core flow

奥丁数据模型基于 modelId 提供结构化取数能力：先选定模型，再按模型可用的维度（dimension）与度量（measure）组合查询数据。上游模型集群分 4 类（`default` / `finance` / `hfc` / `secret`），在查询侧统一收敛为两条路径——仅 `secret` 走高密 Host，其余共用默认公共 Host。

## Step1: 获取用户可访问模型列表 & 确定用户想查询的模型

获取当前用户有权限的模型列表：must refer to reference/model/model_list.md（分页接口，无法精准匹配时按 modelName 模糊检索或翻页遍历）

模型匹配原则：

1、通过 modelName 与用户自然语言匹配（如"业绩明细模型"、"新签订单模型"），优先精准包含关系；

2、结合 configType 判断（0-可视化模型 / 1-SQL 模型），若用户明确说要看"SQL 模型"，只在 configType=1 中匹配；

3、注意 clusterType 字段，本服务已在 list 侧派生出 `odinCluster`（`default/finance/hfc → public`，`secret → high_confidential`），**该值必须在后续 model_query 中原样透传**，不允许猜测或自行推断。

注意：当无法精准匹配模型时，可通过 AskUserQuestion 向用户确认，直到确认完毕。

按需辅助：若单靠 modelName 难以辨识模型语义，可 refer to reference/model/model_detail.md 拉取模型 SQL 与元信息辅助判断（非主流程必需）。

输出记录为：#{model_id}、#{odin_cluster}（来自 list 返回的 odinCluster 字段）

## Step2: 获取模型字段（维度 & 度量）

获取模型可用字段：must refer to reference/model/model_columns.md

关键处理：

1、`showStatus=1` 才是可用字段，`showStatus=0` 的字段一律忽略；

2、`columnType` 区分 `dimension`（维度，用于分组/过滤）与 `measure`（度量，用于聚合）；

3、**字段在 query 中的取值来源固定**（对齐 model_query.md 的 ColumnRef 协议，**不要混淆**）：

   - `columnId`（**必填**）= `model_columns` 返回的 **`modelColumnId`**（**不是** `oColumnInfo.column_id`，也**不是** `oColumnInfo.column_code`）；
   - `alias`（**推荐填**）= `modelColumnName`，决定结果集中的列名；
   - `oColumnInfo.column_code` 仅是元信息中的物理 SQL 列名，**用于辨识字段**（如与用户沟通字段语义、排查上游报错），**不直接作为 query 参数**。

### Step2.1: 聚合维度的确定

当用户明确将数据按照某些维度展开分析时，需要匹配到对应 `columnType=dimension` 字段的 `modelColumnId` 与 `modelColumnName`，构造对象元素 `{columnId, alias}`。

-example:
User: "获取业绩明细模型的城市维度数据", 你需要从 `columnType=dimension` 且 `showStatus=1` 的字段中匹配 `modelColumnName` 含"业绩城市"的字段，取其 `modelColumnId` 作为 `columnId`、`modelColumnName` 作为 `alias`。

示例输出（记为 #{dimensions}）：

```json
[
  {"columnId": 101, "alias": "业绩城市"}
]
```

### Step2.2: 度量字段的确定

用户查询的数值指标对应 `columnType=measure` 的字段，同样从 `modelColumnId` + `modelColumnName` 构造，但**元素形态多一个 `agg` 字段**：`{columnId, alias, agg}`。

关键分流（参见 model_query.md 的"度量作为维度"章节）：

- **明细取数（默认 / 推荐）**：用户想看每一行原始数据，不做聚合 → **把所有 measure 字段平移到 `#{dimensions}`**，并保持 `#{measures}` 为空数组 `[]`。原因：上游对 `measures[]` 中的元素强制要求 `agg` 聚合函数，若既不想聚合又填了 measures，会直接报错；把 measure 平移到 dimensions 相当于按明细列展开而不做聚合。
- **聚合取数**：仅当用户明确要"合计 / 平均 / 计数"等聚合时，才把度量放进 `#{measures}` 并**必填 `agg`**（可选 `SUM/AVG/COUNT/COUNT_DISTINCT/MAX/MIN/NONE`）。

-example（明细取数）:
User: "查看武汉新签单量的明细"，"新签单量"虽然在模型里是 measure，但用户想看明细 → 把它**平移进 dimensions**：

```
// 追加到 #{dimensions}
[
  {"columnId": 101, "alias": "业绩城市"},
  {"columnId": 202, "alias": "新签单量"}
]
// 保持 #{measures} 为空
[]
```

-example（聚合取数）:
User: "按城市汇总新签单量合计"，明确要求聚合：

```
// #{measures}
[
  {"columnId": 202, "alias": "新签单量合计", "agg": "SUM"}
]
```

示例输出记为 #{measures}（默认为 `[]`）。

### Step2.3: 筛选条件的确定

当用户明确筛选某些条件时（如"武汉的"、"品牌为 XX 的"），需匹配 dimension 字段的 `modelColumnId` 构造 filter。

**filter 是一棵嵌套节点树**（与 index 的 filter schema 完全不同，切勿混用）：

- **分组节点**：`{logic: "AND" | "OR", items: [子节点...]}`；根节点必须是分组节点；
- **条件节点（叶子）**：`{columnId: <modelColumnId>, op: <操作符>, values: [...]}`；
- 操作符可选：`EQ / NQ / GT / LT / GE / LE / BETWEEN / INCLUDE / EXCLUDE / LIKE`（多值枚举常用 `INCLUDE`）；
- 分组节点与条件节点字段**互斥**，不能混用（分组节点上不写 `columnId`，条件节点上不写 `items`）。

若用户提到的值（如"武汉" vs "武汉市" vs "wuhan"）无法直接匹配到字段取值格式，通过 AskUserQuestion 向用户确认，不要臆测。

示例输出（记为 #{filter}，假设"业绩城市"字段的 modelColumnId=101）：

```json
{
  "logic": "AND",
  "items": [
    {"columnId": 101, "op": "INCLUDE", "values": ["武汉"]}
  ]
}
```

多条件组合示例（AND + OR 嵌套）：

```json
{
  "logic": "AND",
  "items": [
    {"columnId": 101, "op": "INCLUDE", "values": ["武汉", "杭州"]},
    {
      "logic": "OR",
      "items": [
        {"columnId": 303, "op": "GE", "values": ["2025-01-01"]},
        {"columnId": 303, "op": "EQ", "values": ["2024-12-31"]}
      ]
    }
  ]
}
```

## Step3: 查询模型数据 & 整理返回数据

### Step3.1 构造 query 对象

将前述结果组装为 `query`（`#{dimensions}` / `#{measures}` / `#{filter}` 直接是**对象/数组**本身，非字符串）：

```json
{
  "dimensions": "#{dimensions}",
  "measures": "#{measures}",
  "filter": "#{filter}",
  "page": {"pageNo": 1, "pageSize": 1000}
}
```

注意：

- `dimensions` 元素形态 `{columnId, alias}`；`measures` 元素形态 `{columnId, alias, agg}`（`agg` 在 measures 非空时必填）；
- 明细取数场景下 `measures` 必须是空数组 `[]`（所有字段已平移到 `dimensions`）；
- `filter` 可省略（不带筛选时）；如带，必须是嵌套树 schema（Step2.3 定义），**不要**用 index 的 `{type:"and",fields:[...]}` 结构；
- `page.pageSize` 默认 1000，仅当用户明确要求更大分页时才调整。

### Step3.2 发起查询

使用 model_query 指令获取数据：must refer to reference/model/model_query.md

- 从资产命中进入时，`model_query` 和 `model_query_async` 都要带这个资产的 `asset_id`。
- 不是从资产来的查询不传 `asset_id`。
- modelId 传入 #{model_id}；
- query 传入 Step3.1 构造的对象；
- **odin_cluster 传入 #{odin_cluster}**（直接查模型时来自 Step1 list 返回的 odinCluster；从资产命中时由资产 `cluster_type` 按同样规则映射。**严禁猜测**）。

**同步 vs 异步下载**（默认同步；以下情况切异步）：

- 需要 `pageSize > 100` 或一次性拉完整数据集时，改走异步下载：refer to reference/model/model_query_async.md
- 同步接口返回的字段出现值 `null` 但预期非空（Odin 大 pageSize 已知 bug），也应改走异步；
- 异步行数上限按集群（`odin_cluster`）：`high_confidential`（高密）**5000 行**，其余（公共）**10W 行**；判断方式见 model_list 返回的 `odinCluster` 字段并透传；高密超限时需通过 filter/dimensions 提前缩小数据量；返回结构和同步接口不同（`data.list` 直接是行数组，值已按 `mapping.data_type` 强转过类型，见 model_query_async.md「返回数据说明」）。

### Step3.3 整理返回数据

1、⚠️ **`data` 常是"含单个元素的数组"**，需先归一化：`data` 是数组则取 `data[0]`、是对象则取 `data`，记为 payload；行数据在 `payload.queryResult.result.data.list`，`payload.errorDetail` 非空即上游报错。**别直接写 `data.queryResult...`（漏了取数组 [0]）**，详见 reference/model/model_query.md「返回数据说明」。提取该 list 为结果行集合，记为 #{model_data}；

2、**行内列名由请求中的 `alias` 决定**（推荐等于 `modelColumnName`），因此结果集列名默认就是中文；若查询时未传 `alias`，上游会回落到内部编码；

3、若 `data.errorDetail` 非空（或响应中带有 `errorDetail`），将该信息完整提示给用户，不要静默丢弃——常见原因是 SQL 权限、字段错拼、行级权限不足；若 errorDetail 提示"指标缺少聚合函数"，回查 `#{measures}` 中每个元素是否都带了 `agg`；

4、结果以表格或摘要形式呈现给用户；数值字段若为字符串型，计算前先做类型转换。

---

# odin_fetch api use core flow

基于奥丁看板 request_id 的取数流程。

⚠️ **进入本 flow 前必须满足以下条件之一，否则禁止进入：**
1. **Step 0 未命中任何资产**，且用户输入包含 request_id（UUID 格式）或明确提及"奥丁/odin"；
2. **已经过 `data asset core flow` → `supabase snapshot core flow` 检查，确认快照不可用**，从 `data asset core flow` 回落至此。

⚠️ **如果 Step 0 命中了资产（无论用户是否使用 @），必须先走 `data asset core flow`，禁止直接进入本 flow。**

## Step1: 收集必要信息

**request_id**：
- 若从 `data asset core flow` 回落至此，`request_id` 直接从资产 `detail[].request_id` 取得，无需询问用户；
- 若 Step 0 未命中资产，向用户确认奥丁看板的 Request ID，UUID 格式（如 `76e5e256-93e0-43a2-bd69-d4117286104a`），若用户已提供则跳过。

## Step2: 获取筛选项

must refer to reference/odin_fetch/odin_fetch_filter_params.md

调用接口获取该 request_id 支持的筛选字段，提取：
- `data.filterParams`，记为 #{filterParams}
- `data.specialDS`，记为 #{specialDS}（> 0 表示高密数据，可提示用户，流程不变）

### Step2.1: 处理日期类筛选项

对 `filterParams` 中 `dataType=date` 的字段：

**传参格式统一为 `yyyyMMddHHmmss`**，无论 filterParams 中 dateFormat 是什么值，一律使用此格式：
- 开始时间 HHmmss 固定为 `000000`
- 结束时间 HHmmss 固定为 `235959`

**根据 `dateArrayCnt` 决定向用户询问的方式和数组长度**：

| dateArrayCnt | 含义 | 传参格式 | 询问用户 |
|---|---|---|---|
| 1 | 单点时间 | `["20260713000000"]` | 询问具体某一天 |
| 2 | 时间范围 | `["20260701000000", "20260713235959"]` | 询问开始日期和结束日期 |

转换示例（dateArrayCnt=2）：
- 用户说「今天」→ `["20260713000000", "20260713235959"]`
- 用户说「上周」→ `["20260706000000", "20260712235959"]`
- 用户说「7月1日到7月10日」→ `["20260701000000", "20260710235959"]`

转换示例（dateArrayCnt=1）：
- 用户说「今天」→ `["20260713000000"]`
- 用户说「7月1日」→ `["20260701000000"]`

若用户未说明时间，必须通过 AskUserQuestion 询问，不要自行假设。

### Step2.2: 处理枚举类筛选项

对 `filterParams` 中 `dataType=string` 且有 `defaultValues` 的字段：
- 展示 defaultValues 列表让用户选择，避免用户自由输入导致匹配不上
- 若用户不需要按该字段筛选，则 dateParams 中省略该字段（不传空值）

### Step2.3: filterParams 为空

若 `filterParams` 为空数组，说明该 request_id 无筛选项，直接进入 Step3。

## Step3: 预览数据

must refer to reference/odin_fetch/odin_fetch_preview.md

根据 Step2 收集的筛选条件，组装 dateParams，调用预览接口（默认 pageSize=1000）。从资产命中进入时，body 必须带这个资产的 `asset_id`；不是从资产来的预览不传。

提取：
- `data.headers`：列名
- `data.data`：数据行
- `data.page.totalCount`：总行数

### Step3.1: 数据量判断

- **totalCount < 1000**：数据已全量返回，直接以表格展示，流程结束
- **totalCount = 1000**：实际数据量可能超过 1000，通过 AskUserQuestion 询问用户：「当前预览了 1000 条，实际数据可能更多，是否获取全量数据？」
  - 用户选择否：展示当前 1000 条，流程结束
  - 用户选择是：进入 Step4 全量下载

## Step4: 全量异步下载（按需）

仅当 Step3 判断需要全量数据时执行。

must refer to reference/odin_fetch/odin_fetch_async_download.md

调用 `/request/fetch` 接口（Skill 专用），该接口内部自动完成：提交异步任务 → 轮询 → 下载 CSV → 返回全量数据。从资产命中进入时，body 必须带和预览相同的 `asset_id`。

接口为同步等待，直到数据返回（通常需要数秒到数分钟）。返回结果格式：
```json
{"headers": [...], "list": [...], "total": N}
```

以表格或摘要形式展示全量数据，并告知用户总行数。


---

# personal supabase core flow

适用场景：用户要对**自己的个人 supabase 实例**（`user_supabase_workspace`）执行管理操作
（建表、改表、创建函数、migration、Storage 桶管理等），**与资产数据查询无关**。

**触发条件**：用户的操作意图是对个人 supabase 实例进行操作（建表、改表、创建函数、migration、Storage 桶管理、查询个人实例表结构等）

## Step 0：首次使用初始化（仅首次）

must refer to reference/personal_supabase/create_and_expose_schema.md

```bash
moma moma-data api POST_moma-data_personal_supabase_create-and-expose-schema --json
```

已初始化过则跳过本步。

## Step 1：按用户意图路由

| 用户意图 | 操作 | 参考文档 |
|---|---|---|
| 查看已有的表 | list-tables | reference/personal_supabase/list_tables.md |
| 查看 migration 历史 | list-migrations | reference/personal_supabase/list_migrations.md |
| 建表 / 改表 / 创建函数（推荐带版本记录） | apply-migration | reference/personal_supabase/apply_migration.md |
| 临时执行 SQL / 查数据 | execute-sql | reference/personal_supabase/execute_sql.md |
| 创建 Storage 桶 | create-storage-bucket | reference/personal_supabase/create_storage_bucket.md |
| 列出 Storage 桶 | list-storage-buckets | reference/personal_supabase/list_storage_buckets.md |
| 列出桶内文件 | list-storage-objects | reference/personal_supabase/list_storage_objects.md |

## 禁止操作

以下操作 moma-data 不提供接口，**不得尝试调用**：

- 删除 workspace（不可逆）
- 删除 Storage 桶（连带删除桶内所有对象）
- 获取数据库连接串（含密码，会泄漏进上下文）
- 枚举/创建 workspace（超出单用户边界）
- 分支管理（create/delete/restore_branch）
