# 看板组件资产查询（report_component）

组件资产是已发布 Odin 看板组件的版本化服务端查询引用，保留聚合口径、固定条件和筛选定义。录入人修改或刷新配置草稿不影响当前已发布定义；重新发布后版本改变，旧版本引用返回 409。
源模型可以已经同步到 Supabase，但组件没有独立数据副本；不得查询源表来模拟组件结果。
新版统一使用奥丁实时查询；旧版已发布快照仍按原版本兼容。请求身份由登录上下文自动注入，权限校验由服务端完成。Agent 仅按组件契约传入资产 ID、版本、筛选及分析条件，不传入或替换用户身份。两种模式都只能调用组件接口，不能由 Agent 自行切换或绕过。

## 1. 找到用户实际选择的组件

- 页面入口：数据资产或 @ 选择器中的「奥丁报告 → 报告名 → 组件名」，组件详情「概览」可查看图表和筛选。
- 用户在数据资产页点击「获取有权限的报告 / 刷新报告」后，服务端分批校验 Moma 中已录入且发布的报告，并保存个人目录。用户具备报告 view 权限时无需逐个分享组件；这不会授予底层模型或源表权限。
- API 从 accessible 的 by_tag/by_team/untagged 中读取已保存目录与已有分享，按整数 asset_id 去重。access_via_report=true 只是目录发现标记。不要假设有「奥丁报告」标签或 folder API，不自行扫描报告或触发目录刷新；列表无目标时引导用户点击页面按钮。
- 用户已 @ / 给出 ID 或 ref 时以该条为准；ref 按 accessible_resolve 反查，不手拆 ID。同名组件要核对报告；仍不明确时 Ask 一次。
- 上游只有组件 ref 时，可用 `GET_moma-data_cli_data-assets_accessible_resolve` 的 query.ref 反查；不得手拆 ref 猜目录 ID，found=false 即停止。
- lite 列表或 detail 缺失，先 `GET_moma-data_cli_data-assets_by-ids`，`query.ids` 为目录资产 ID 的逗号分隔字符串。返回 asset_id 是 data_asset 的目录 ID；不是 report_component 二级记录 ID。
- 本回合完整 detail 已有 version/query_body/columns/filters 时直接复用。不得从历史对话猜 ID、版本或筛选字段。

## 2. 读取契约

| detail 字段 | 用途 |
| --- | --- |
| query_api | 必须是 POST_moma-data_cli_report-components_query |
| query_body | 固定 asset_id、version，selections 的起点 |
| version | 当前组件资产版本；不自行加一或静默改用新版本 |
| query_mode | snapshot 为同步快照（默认），realtime 为奥丁实时；由服务端配置，调用参数不变 |
| columns | 结果 key（v0/v1…）、label 和 numeric，展示时使用标签及原单位 |
| filters | 允许的筛选器 id/title/date/options_supported；空数组表示无可传筛选器 |
| report_id / report_name / component_id | 在字段可用时辅助确认组件归属，不能代替目录 asset_id |
| source_asset_id / row_permission | 表示源资产及行级权限继承关系，不是允许绕过组件查询的授权 |
| source_sync | 仅供前端 @ 选择守卫使用；Agent 不基于该字段输出额外文字 |
| display | 图表展示建议；不改变字段、聚合和固定条件 |

## 3. 查询与筛选

唯一取数接口：`POST /moma-data/cli/report-components/query`，api_name 为 `POST_moma-data_cli_report-components_query`。
使用 `moma moma-data api ... --json`，登录、权限和敏感信息规则沿用根 Skill 引用的 moma-shared。只使用当前用户的正常 CLI 登录态，不伪造 test/创建人 UCID，不在命令里硬编码 Cookie 或密钥。

下面 CLI 命令仅演示格式。42、3、filter_city 必须替换为本回合真实契约中的目录 ID、版本及筛选器 ID。

默认查询（保留固定条件；新版实时组件未指定的可选筛选不限范围，旧版保留契约默认条件）：

```bash
moma moma-data api POST_moma-data_cli_report-components_query --json \
  -d '{"asset_id":42,"version":3,"selections":{}}'
```

用户选择已声明的城市筛选器后：

```bash
moma moma-data api POST_moma-data_cli_report-components_query --json \
  -d '{"asset_id":42,"version":3,"selections":{"filter_city":{"op":"in","values":["北京"]}}}'
```

- selections 最多200项；未选择且无默认值的筛选项省略，不要为每个控件发送空数组。旧版有默认值的筛选器，用户明确清空时保留空数组以覆盖默认条件。
- selections 的 key 只能取自 detail.filters[].id，不能传列名、报告 ID 或未知筛选器。
- 普通多选用 in；date=true 的范围筛选用 between 和两个端点，日期格式遵循组件约定。清除用户选择时移除该筛选 key，新版实时组件不限该筛选范围，旧版恢复契约默认条件；不能移除固定条件。
- filters=[] 时保持 selections={}，不能编造按天或按城市过滤。用户要求契约外字段/维度时说明当前能力，联系录入人调整并重新发布组件，不切换源模型。
- 只有 options_supported=true 且非日期筛选器才取枚举：同一 body 增加 option_filter=筛选器ID，同时携带其它当前 selections。
  成功选项在 data.rows[].value；服务端排除该筛选自身选中条件，保留其他筛选、固定条件和行级过滤。
- 改筛选后重新请求组件接口；不能在截断的首次结果中本地过滤或再聚合。除 asset_id/version/selections/option_filter 外不传模型、SQL、表名、身份、URL 或自定义请求头。

筛选候选项（仅 options_supported=true 的筛选器）：

```bash
moma moma-data api POST_moma-data_cli_report-components_query --json \
  -d '{"asset_id":42,"version":3,"selections":{},"option_filter":"filter_city"}'
```

## 4. 成功结果与失败边界

HTTP 成功且业务 errno=0 才处理 data；直接接口的行在 data.rows，列在 data.columns，不是 data.data.list。
非空结果按 columns[].label 展示；不要把百分比等字段再换一套单位或重新计算口径。
查询成功后按当前运行环境已有的展示方式呈现，只使用本次组件回包，不伪造数据或把失败结果生成成功报告。

| 响应 | 处理 |
| --- | --- |
| rows=[] | 当前条件无数据，不编造数字或排名 |
| restricted=true | 当前行级规则未授权可见行，不等同于接口故障 |
| truncated=true | 明示截断，不能视作完整报告或全量重算；提示收窄已支持的筛选范围 |
| data_source | snapshot / realtime 表示本次数据来源；实时结果没有快照更新时间，不编造同步时间 |
| 401 / login required / missing x-user-id | 按 moma-shared 的正常登录规则处理；此请求尚未成功，不伪造身份重试 |
| 403 | 按实际错误说明报告权限、绑定范围、撤回或封禁等原因；目录可见不代表实时授权，不能用旧目录承诺取数成功 |
| 409 | 定义/版本失效；录入人核对后重新发布，使用方确认新口径后再更新固定引用 |
| 503 / 502 / 网络超时 | 当前服务不可用；如实说明，禁止换接口、换 host 或换身份绕过 |
| HTTP 成功但业务错误 | 仍是失败，按实际 errmsg/detail/message 说明 |

权限、版本或服务失败时停止本次取数；登录问题按 moma-shared 处理。不生成成功展示，不把元信息可读/网关可达当作数据已验证。
只有实际当前用户在本次环境成功返回数据，才能声称该请求通过；浏览器预览登录仍需单独验证，不承诺部署后会自动恢复。

## 5. 应用、助手与 OB 复用

- @ 的是组件资产 ID，不是源资产或整个报告的隐式授权；使用平台提供的当前访问者认证方式。
- 应用优先读取框架生成的 src/data_assets/report_component_{asset_id}_v{version}.tsx，调用默认导出的 getDataBy_{asset_id}(selections) 和 getFilterOptions(filterId,selections)。
  生成工具使用 momaDataClient 请求专用接口；其包装结果为 success/data/columns，data 是行数组，与上面的原始 HTTP data.rows 区分。
- 助手/OB 仍使用同一 asset_id/version/selections 契约，按该运行环境已提供的真实认证能力调用；没有登录态时只说明未验证，不硬编码身份或 Cookie。
- 不修改生成目录文件、不复制源数据到应用表、不把返回数据写死在代码或共享缓存；版本更新不覆盖旧文件或静默替换已有 import。


## 新版实时组件：受控分析

报告导入的模型仅保存元数据，默认不启动同步；组件无需 Supabase 快照。
取数前仍先按资产 ID 读取本回合契约。`detail.analysis.enabled=true` 才能传 `analysis`。

- 不传 analysis：按发布的组件字段与原聚合查询。
- 传 analysis：dimensions 是 `detail.analysis.fields[].key`；metrics 为 `{field, agg}` 数组，至少一项。
- agg 只能选该字段的 aggregations；COUNT 是字段非空计数，COUNT_DISTINCT 是去重计数。
  不能自行把“商机数”等业务词解释成行数。优先用已发布 default_aggregation；口径不明确时询问用户。
- order 为 `{field:"v0",direction:"DESC"}` 数组；输出维度在前、指标在后，按顺序编号 v0/v1。
- limit 默认100，最多1000。analysis 与 option_filter 不可同时传。
- 可选筛选使用 selections：新版实时组件未指定的可选筛选不限制范围；固定条件、模型限制与权限不变。
- 只允许组件公开的字段，不允许 SQL、任意模型 ID、跨模型、源表或 snapshot 回退。
- 本次结果列以响应 data.columns 为准，不能套用原组件 columns，也不能把截断结果当全量再次统计。
- 应用构建使用组件客户端 `getAnalysisBy_<asset_id>(analysis, selections)`；
  普通展示继续 getDataBy，字段及权限逻辑都由组件接口处理。
