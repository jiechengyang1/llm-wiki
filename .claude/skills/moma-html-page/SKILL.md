---
name: moma-html-page
description: 在 Obsidian 中生成或修改独立 HTML 页面。用户要求制作 HTML、网页、数据页面、看板、仪表盘、大屏、清单、榜单、排行榜、交互页面，或通过 @ 引用现有 HTML 要求优化时使用；涉及 Moma Data、数据资产、指标或数据表时，按受控动态页面流程生成。仅当语义明确与 Moma Data 无关时生成普通 HTML。
---

# Moma HTML Page

根据用户语义生成自由 HTML。不要生成 PageSpec、组件 DSL 或主页配置。

## 视觉风格

用户指定了视觉风格时以用户为准。没有指定时默认使用 [Moma 暖橙色模板](assets/moma-warm-orange.html)：写任何页面 CSS 之前必须先 Read 该文件，并原样复制其设计变量与视觉节奏，不要凭记忆写默认样式；页面已经在用这套变量时不要重新配色。模板只提供样式，不是组件库，页面结构和交互仍按用户意图生成。

## 路由

按以下优先级选择分支：

1. 输入中携带数据资产的结构化 `@` 参数：必须生成 Moma Data 动态 HTML。
2. 未携带结构化参数，但语义明确涉及 Moma Data：生成 Moma Data 动态 HTML。
3. 语义明确无关：生成普通 HTML。
4. 数据来源无法判断：询问用户是否需要接入 Moma Data 实时数据，不要擅自按普通 HTML 处理。

## 开始生成

先由本 Skill 完成路由、目标文件名和视觉风格选择，再加载任何业务 Skill。第一次写入固定创建完整、可正常打开的静态准备页：用户指定了样式就按用户要求生成，否则以暖橙色模板为基础；页面显示“正在生成”，不调用任何接口，也不写入尚未完成的业务脚本。是否可以提供预览由这条固定规则决定，不要为此增加额外的 Read、试运行或模型判断。

第一次写入成功后立即用一句话给出可点击入口，例如：“已创建 [[城市榜单.html]]，可以先打开预览，后续内容会自动更新。”继续完成业务 Skill、CLI、校验和页面修改，不等待用户回复。正式页面完成前保留清晰的生成中状态，不自动发起业务请求；最后再启用数据加载和交互。除该入口、确实需要用户补充的信息和最终结果外，Skill 加载、临时工作流、CLI 命令、Schema、Manifest 和逐次编辑过程均静默执行，不向用户逐项讲解。

动态页面第一次启用正式业务脚本的写入顺序是硬性要求：HTML 保持静态生成中状态时，先创建目录并成功写入 Manifest，再更新 HTML 以启用完整的 `window.moma` 调用和数据加载。禁止先启用接口调用、后补写 Manifest；这两项本来就要执行，只调整顺序，不增加额外读取、校验或编辑。

## 运行环境约定

生成的 HTML、脚本和视觉资源必须自包含。禁止通过外链 `script`、`link`、`img`、`font`、`iframe` 等标签或动态注入方式加载 CDN、远程 JavaScript、CSS、字体、图片和媒体资源；沙箱 CSP 不允许这些资源，不能先引用外链再等待运行失败后返工，也不能要求放宽 CSP。图表优先使用页面内的原生 SVG、Canvas 或 DOM 实现，图标使用内联 SVG、`data:` URI 或纯 CSS。第三方 HTTPS API 是网络数据连接，不属于外部页面资源；确有业务需要时可以按“生成普通 HTML”的约定使用原生 `fetch`，并在 Manifest 的 `externalConnect` 中精确声明 Origin，但不得从该域名加载或执行代码与样式。

## 样式约定

以下约束与选用哪套视觉风格无关，用户自定义风格同样适用（正确写法见默认模板，此处只列禁止项）。

checkbox 和 radio 默认只调尺寸和 `accent-color`。一旦给它们设置 `border` 或 `background`，Chromium 会放弃原生绘制，勾选标记消失、选中态不可见；表单控件的通用样式也不要用裸 `input` 选择器，`min-height`、`min-width`、`padding` 会把它们撑成空方块。用户明确要求自定义外观时才用 `appearance:none` 自绘，且勾选图标只能用 `data:` URI 或纯 CSS 边框绘制。

所有使用原生 `hidden` 属性的元素都必须遵守 `[hidden] { display:none !important; }`，避免组件自己的 `display` 样式覆盖隐藏状态。

## 生成 Moma 动态 HTML

1. 阅读当前安装的 `moma-data` Skill，用它识别业务能力、候选 CLI 命令和 `apiName`。不要在本 Skill 中维护业务接口清单，也不要凭空编造 `apiName`。

   如果用户要求的某项功能不在业务 Skill/reference 声明的能力范围内，先判断它能否仅使用页面已经合法取得的完整数据在前端完成；能完成时按普通页面交互实现，不需要额外业务接口。确实需要新的业务数据或操作而没有可用的只读 API 时，不得编造接口、数据或假按钮，也不得自行改用用户未指定的第三方服务。缺失的是非核心功能时，省略该功能并继续完成其余部分，最终用一句话说明“当前业务能力暂不支持……；相关接口开放后可以再接入”；缺失的是用户核心目标时，停止生成正式页面，说明能力缺口并询问用户是移除该功能继续，还是等待相关接口开放。
2. 在内部确定当前任务的临时工作流，不向用户输出。一个业务命令可以包含多个 API，按数据依赖决定顺序；该工作流只是生成过程中的临时结论，不要持久化成 PageSpec 或另一套业务 DSL。
3. 先区分生成期的查询编译步骤和页面运行期 API。判断标准是某项信息在页面打开期间是否会随用户交互或业务数据变化，而不是它是否被后续 API 使用：
   - 对 `moma-data`，必须先按当前业务 Skill 完成数据源识别和查询参数求解。查找数据资产、匹配指标或模型、读取字段与维度、查询枚举值、确定分区、解析筛选语义和组装最终参数，默认都属于生成期查询编译，通过 CLI 执行，不写入 HTML，也不加入 Manifest。
   - `moma-data` 查询编译必须产出一个已验证的终点查询，包括精确的 `service`、`apiName`、固定参数和由页面状态控制的动态参数。默认只把最终返回页面主数据的只读接口保留为运行期 API。
   - 页面筛选、日期、排序或分页仅改变终点查询的动态参数时，直接用新参数重新调用同一个终点 API，不要重复执行资产、指标、维度或字段发现链路。
   - 只有页面本身允许切换数据资产、指标、模型或数据表，或者选项需要实时搜索、级联加载时，才把实际受这些交互影响的中间接口提升为运行期 API。生成期得到的稳定选项可以作为页面配置使用。
   - 生成期可以调用一次终点 API 校验查询参数和响应结构，但不得把当次结果作为死数据写入 HTML；页面运行时仍须请求最新数据。
4. 仅对每个确定的运行期 API 做契约查询和具体请求校验；生成期中间 API 按业务 Skill 通过 CLI 执行即可，不额外执行 `describe`。先根据生成期结果、页面初始状态和业务 Skill 构造完整候选请求，再执行：

   ```bash
   moma <service> describe <apiName> --request '<candidate-request-json>' --json
   ```

   `<candidate-request-json>` 只允许包含 `path`、`query`、`body`、`headers`，例如 `{"path":{},"query":{"limit":20},"body":null,"headers":{}}`。命令必须成功退出，且 JSON 中的 `service`、`apiName` 与目标完全一致并能确认接口为 `risk: "read"`。返回 `valid: true` 时，使用 `normalizedRequest` 作为 HTML 运行期调用的参数位置、结构和初始值依据。

   返回 `valid: false` 时，先按 `errors` 修复模型自身的漏参、位置或类型错误；如果失败原因是 `requestSchema` 与当前业务 Skill/reference 对同一参数的声明不一致，则允许使用业务 Skill 明确给出的候选请求，通过 CLI 实际试调同一个只读接口。试调成功且响应可用时继续生成，在内部记录并去重具体字段或参数位置的简短差异；生成过程中不要向用户输出这些差异，统一留到最终完成回复的一张表格中。不要记录或输出接口名、Manifest 路径及更多技术细节。

   实际试调失败、接口不存在、权限不足、风险不是只读或风险无法确认时停止受影响部分，不能用上述例外放行。修复和试调合计最多三次，不得猜测 API、伪造身份或直连网关。

   页面筛选、搜索、排序或分页会形成不同请求结构时，每种实际会发出的结构都要用有效的具体值执行 describe；属于上述契约差异时，每种结构都要实际试调成功。动态值可以替换已验证样例中的具体值，但参数位置和类型必须保持不变；无法从业务结果、Schema 的 enum/default/example 或用户输入得到合法值时，应向用户询问，不能编造。

   使用返回的 `service`、`apiName`、`risk`、`httpMethod` 和 `apiPath` 确认接口身份与调用方式，只允许 `risk: "read"`。结合 `requestSchema`、`responseSchema`、`responseExample` 和 `resultHint` 构造请求与页面；`requestSchema` 与业务 Skill/reference 不一致时按上述实际试调规则处理。
5. 根据用户要表达的内容选择页面结构和组件，不要假定每个页面都需要表格、卡片、图表、筛选或分页；结合响应 Schema、成功示例和结果提示生成当前页面专用的数据适配代码。不要编造响应字段，也不要建立全局业务响应转换器。
6. 直接生成自包含 `.html` 或 `.htm`。为动态页面只生成一次 UUID v4 `pageId`，在 HTML `<head>` 中写入并在后续修改、重命名时保持不变：

   ```html
   <meta name="moma-page-id" content="550e8400-e29b-41d4-a716-446655440000">
   ```

   将 Manifest 集中写入 `.moma/html-pages/<pageId>.json`，不要在 HTML 同目录创建 sidecar。`entry` 是 HTML 当前的 Vault 相对路径，Manifest 只声明页面实际在运行期使用的精确只读能力，每个运行期 API 只声明一次：

   ```json
   {
     "version": 2,
     "kind": "moma-html",
     "pageId": "550e8400-e29b-41d4-a716-446655440000",
     "entry": "报表/数据资产列表.html",
     "capabilities": [
       {
         "service": "moma-data",
         "apiName": "GET_exact_api_name",
         "risk": "read"
       }
     ],
     "externalConnect": []
   }
   ```

7. 页面通过插件注入的 SDK 调用运行期 API：

   ```js
   const result = await window.moma.request({
     service: 'moma-data',
     apiName: 'GET_exact_api_name',
     query: { page: state.page, keyword: state.keyword },
     signal: controller.signal,
     cache: { ttlMs: 60_000 }
   });
   ```

   `path`、`query`、`body` 和 `headers` 使用通过 describe 的 `normalizedRequest`；发生上述契约差异时，使用有业务 Skill/reference 依据且已实际试调成功的请求。必填参数必须提供，选填参数仅在页面确实需要且值有效时提供。HTML 表单控件的值默认是字符串；将页面状态写入请求前，必须按已确认的类型显式转换并校验：`integer` 和 `number` 转为有限数字（`integer` 还必须为整数），`boolean` 显式映射为布尔值，`array` 和 `object` 按声明结构构造。空的选填参数应从请求中省略，转换失败时在页面提示用户并停止请求，不能把 `NaN`、空字符串或类型错误的值传给 `window.moma.request`。不要添加既无 Schema 声明、也无业务 Skill/reference 依据或未实际试通的参数。不要写入 Token、插件鉴权头、Moma 网关地址、HTTP Method 或真实网关 Path，也不要用原生 `fetch` 调 Moma API。

   如果 `describe` 表明只读接口成功响应是附件或二进制文件，下载按钮使用独立下载方法，不要用 `window.moma.request` 读取文件内容：

   ```js
   const saved = await window.moma.download({
     service: 'moma-data',
     apiName: 'GET_exact_download_api',
     query: { taskId: state.taskId },
     fileName: '查询结果.xlsx',
     signal: controller.signal
   });
   ```

   下载使用同一个 Manifest 精确只读能力和同一份请求 Schema；文件由父插件保存到当前 HTML 同目录，同名时自动生成新名称。Promise 返回 `{ fileName, path, size, contentType? }`，页面只展示保存结果，不接收文件字节或鉴权信息。下载必须由用户点击等明确操作触发。

   页面需要把已经取得的数据在本地整理成 CSV、JSON 等文件时，不需要业务下载接口；由用户点击按钮后调用 `window.moma.saveFile`，让父插件保存到当前 HTML 同目录：

   ```js
   const saved = await window.moma.saveFile({
     fileName: '城市榜单.csv',
     content: csvText,
     contentType: 'text/csv;charset=utf-8'
   });
   ```

   `content` 可以是字符串、`ArrayBuffer` 或 TypedArray，Promise 同样返回 `{ fileName, path, size, contentType? }`。单文件最多 20 MB；一个页面运行实例最多保存 10 个文件、累计最多 50 MB。SDK 只允许在一次可信用户点击后保存一个文件，因此长耗时数据准备结束后若点击授权已失效，应在页面显示“数据已准备完成”和单独的“保存文件”按钮，不得自动落盘。不要使用 `Blob`、`URL.createObjectURL` 或 `<a download>`，它们只会进入系统默认下载目录且无法返回可靠路径。

   `window.moma.saveFile` 只负责保存页面已经持有的内容；业务接口直接返回附件或二进制文件时仍使用 `window.moma.download`。CSV 不能标注成 Excel，当前页或截断数据也不能称为“导出全部”；若用户要求的完整数据尚未被页面安全取得，必须继续使用业务方提供的全量查询或下载能力，不能用本地保存绕过业务限制。

   页面运行在不开放原生模态框的沙箱中。禁止使用 `alert()`、`confirm()` 或 `prompt()`；需要二次确认时，在 HTML 内渲染普通 DOM 卡片，明确展示操作说明，并提供“取消”和“确认”按钮。只有用户点击卡片中的确认按钮后才执行对应操作。不要通过要求 iframe 增加 `allow-modals` 绕过该限制。

   所有预计超过一秒或包含“提交任务 → 轮询 → 下载”等阶段的操作，都必须在 HTML 内提供持续可见的进度区域：立即进入 loading 状态并禁用重复提交，展示当前阶段和持续更新的耗时；轮询时展示服务端状态；支持 `AbortController` 时提供取消按钮；最后明确展示成功、失败或已取消。不要只依赖按钮的 disabled 样式，也不要让 SDK 猜测或绘制业务进度 UI；SDK 仅提供 Promise、下载结果和 `AbortSignal`，具体状态文案与 DOM 由页面负责。
8. 把首次打开和 Tab 重新激活接到同一个刷新函数：

   ```js
   window.moma.on('ready', () => refreshData({ force: false }));
   window.moma.on('activate', () => refreshData({ force: true }));
   ```

   筛选、搜索、分页等控件只更新页面状态，再调用刷新函数。适合缓存的只读请求可传 `cache: { ttlMs }`；重新激活和显式刷新传 `mode: 'reload'`。请求参数变化会自然产生不同缓存键。
9. 展示加载态、空态和错误态。上游错误文案原样展示，不要把失败响应当成数据。
10. 逐个核对每个运行期调用：已通过携带具体请求的 `describe` 校验，或属于上述契约差异并已实际试调成功；精确 `service/apiName`、只读风险、已确认参数、引用的响应字段和 Manifest 覆盖一致。没有业务依据或未试通的请求不能交付。

## 生成普通 HTML

普通 HTML 不调用 `describe`、不声明 Moma API 能力，也不使用 `window.moma.request`。它可以使用默认暖橙色样式。完全静态时不需要 Manifest 或 `pageId`；需要第三方 HTTPS 请求时使用页面原生 `fetch`，并按动态页面方式写入 `pageId` 和 `.moma/html-pages/<pageId>.json`，其中 `capabilities: []`，精确 Origin 写入 `externalConnect`。请求仍受对方 CORS 约束；不要把第三方密钥写入 HTML。

## 修改已有 HTML

保留用户未要求修改的结构、样式、交互、`pageId` 和能力。若新增或修改 Moma 请求，使用完整候选请求重新执行对应 `describe --request`，契约不一致时遵循上述实际试调规则；若删除请求，同步收紧 `.moma/html-pages/<pageId>.json`。不要扩大成 service 级授权。

## 面向用户的交付说明

用户通常不了解实现细节。正常进度说明和完成回复只说明页面的业务用途、可打开的 HTML 链接，以及必要的使用方式或尚未完成的事项；不要主动展示 Manifest 路径、pageId、内部配置目录、apiName、接口数量或“只授予了几个只读接口”等实现说明，也不要把这些内容写进页面的说明文案。仍须如实说明影响使用的错误或限制；用户主动询问实现或排查问题时，再提供相关技术细节，且不得泄露凭据。

完成回复示例：“已生成‘我的数据资产’页面，点击打开即可查看，也可以按类型筛选。”其中页面名称应链接到实际生成的 HTML。若本次记录了业务契约与 Skill 声明的差异，在完成回复末尾追加且只追加一次“业务契约与 Skill 声明存在差异”，并紧跟一张两列表格；每个去重后的差异占一行，没有差异时不要显示标题或表格。不要在生成过程中或完成回复的其他位置重复，也不要增加接口名、Manifest 路径或技术解释。

```markdown
业务契约与 Skill 声明存在差异：

| 位置 | 差异 |
| --- | --- |
| `query.select` | 业务契约未声明，Skill 允许使用 |
| `query.limit` | 业务契约未声明，Skill 允许使用 |
```

## 不做的事情

- 不修改 Obsidian Homepage 设置。
- 不开放 `write` 或 `high-risk-write`。
- 不把鉴权信息交给 iframe。
- 不代理任意第三方 URL。
- 不复制 `moma-data` 的接口清单或 Schema；业务 Skill 更新后应在生成时重新读取。
