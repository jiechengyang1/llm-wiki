---
tags: [source-summary, AI, LangChain]
type: source-summary
source: 尚硅谷-02-模型的创建与调用
date: 2026-11-17
---

# LangChain模型的创建与调用

## 核心要点

### 模型初始化的三个角度
- 历史脉络：GPT-3 时代以**补全模型**为主（"成语接龙"式、不稳定），GPT-3.5 起**对话模型**成为主流，指令跟随能力让工具调用/结构化输出成为原生功能 → 本章只讲对话模型
- **角度 1 用谁家 API**：模型提供商专用库 vs LangChain 统一方式（推荐）
- **角度 2 参数写在哪**：`.env` 配置文件（推荐，`load_dotenv(override=True)`，文件入 `.gitignore`）vs 硬编码（仅临时测试，密钥泄露风险）
- **角度 3 模型在哪**：在线 API 平台 vs 本地部署（Ollama、vLLM）
- LangChain 本身不提供任何 LLM，只依赖第三方集成；版本变动快，课程用 `requirements.txt` 锁定依赖版本

### 线上大模型服务平台（三要素：模型名 + api-key + base-url）
| 平台 | 特点 |
|------|------|
| **OpenRouter** | 全球主流聚合站，一个 Key 调几乎所有厂商（含国外），需 tizi；有专用 ChatOpenRouter |
| **CloseAI** | 亚洲最大中转，解决国内网络/支付；无专用集成，走 ChatOpenAI 兼容 |
| **阿里云百炼** | 企业端友好，新用户超 5000 万 Tokens 免费额度 |
| **硅基流动** | 性价比高，9B 以下模型永久免费，适合个人学习 |
| 百度千帆 / 火山引擎 | 主打百度生态 / 字节多模态生态 |


### 三种初始化方式
- **专用 Model Class**：`ChatOpenAI` / `ChatDeepSeek` / `ChatAnthropic` / `ChatOllama` / `ChatHunyuan` / `ChatTongyi` / `ChatZhipuAI` / `ChatOpenRouter`，导入即用；注意各家参数名不同（如 ChatDeepSeek 是 `api_base` 不是 `base_url`，默认 `https://api.deepseek.com/v1`）
- **init_chat_model()（推荐）**：LangChain 1.x 统一接口，`init_chat_model("provider:model_name")` 按模型名自动选驱动类；优势 = 统一接口、易切换（只改字符串）、少样板代码、自动适配
- **兼容用法（万能兜底）**：大多数平台支持 OpenAI API 规范 → `ChatOpenAI(api_key=..., base_url=..., model=...)` 可接 DeepSeek/智谱/千问/CloseAI 等几乎一切
- 细节：`model_provider` 支持 anthropic/deepseek/openai/ollama/openrouter 等；`qwen-plus` 这类名字**不能自动推断**厂商，须显式 `model_provider="openai"`（ChatTongyi 底层是 dashscope 专用 SDK，别设 compatible-mode 的 BASE_URL，会报错）

### 常用初始化参数
| 参数 | 说明 | 默认 |
|------|------|------|
| model / model_provider | 模型名（必需）/ 提供商 | 无 |
| api_key / base_url | 不传则读环境变量（如 `DEEPSEEK_API_KEY`） | None |
| **temperature** | 0.0-2.0，越高越随机 | 0.7 |
| max_tokens / timeout / max_retries | 输出上限 / 超时秒 / 失败重试 | None / None / 6 |

- temperature 选型：**0-0.3** 数学/数据提取/分类/代码（最稳定）；**0.5-0.7** 聊天问答；**0.8-1.5** 写作头脑风暴；**1.5-2.0** 诗歌故事
- Token：1 个中文 Token ≈ 1-1.8 汉字，1 个英文 Token ≈ 3-4 字符；按 Token 计费


### 本地模型（Ollama）
- 定位：本地下载/启动/运行大模型的集成框架，跨平台（Linux `curl -fsSL https://ollama.com/install.sh | sh`；Windows `OllamaSetup.exe /DIR=目录`）
- 常用命令：`ollama run/pull/list/rm/ps/stop/show` + `ollama serve`（起 API 服务）
- LangChain 接入：`ChatOllama(model="deepseek-r1:1.5b")`（默认 `http://localhost:11434`）或 `init_chat_model(model=..., model_provider="ollama")`

### 六种调用方式
| 方法 | 模式 | 适用 |
|------|------|------|
| **invoke()** | 阻塞，一次性返回 | 问答、批处理任务 |
| **stream()** | 流式逐 chunk 迭代器 | 聊天机器人、长文本（打字机效果） |
| **batch()** | 并行处理一批输入 | 高并发、批量问答 |
| ainvoke / astream / abatch | 上述的异步版 | 高并发 Web、IO 密集 |

- invoke 三种输入：**纯文本**（自动转 user message，无历史无 system）→ **字典列表**（推荐：`{"role": "system/user/assistant", "content": ...}`，可传历史、JSON 好序列化）→ **消息对象**（`SystemMessage/HumanMessage/AIMessage`，类型检查+IDE 补全，难序列化）
- **模型无状态**：不传历史就"失忆"——多轮对话须手动把 assistant 回复 append 回 messages
- `batch()` 按输入顺序返回全部结果；`batch_as_completed()` 完成即 yield `(index, AIMessage)` 可能乱序；实测 batch 比循环 invoke 快约 **50%**
- 异步写法：`asyncio.create_task(model.ainvoke(...))` 后继续本地逻辑，`await` 取结果；等待用 `asyncio.sleep` 而非 `time.sleep`
- 错误处理：try-except 捕获 `ValueError`（配置）/ `ConnectionError`（网络）/ `Exception`


### AIMessage 返回值解剖
- **content**：最终文本答案；`id`：Run ID；`additional_kwargs.refusal`：拒绝回答原因（None=正常）
- **usage_metadata**：`input_tokens / output_tokens / total_tokens`；`cached_tokens` 缓存命中省钱提速、`reasoning_tokens` 推理模型思考消耗
- **response_metadata**：`finish_reason`（`stop` 自然结束 / `length` 被截断）、`model_name`、`model_provider`、`latency_checkpoint`（`ttft` 首字时间、`tbt` 决定打字机丝滑度）
- **tool_calls / invalid_tool_calls**：模型发起的工具调用及失败的调用

### 拓展要点
- 美化输出：`response.pretty_print()`；终端调试用 **rich** 库 `rprint(response)`
- **model.profile 能力画像**（v1.1+）：`max_input_tokens / image_inputs / tool_calling / structured_output / reasoning_output` 等——是否可用取决于 LangChain 集成该厂商时是否声明（OpenRouter 已声明，DeepSeek 官方/CloseAI 为空）
- 完整参数列表用 `ChatDeepSeek.model_fields.keys()` 查看；参数构成 4 类：**网络连接**（api_key/api_base/request_timeout/max_retries/proxy）、**模型推理**（model_name/temperature/top_p/stop/n/presence_penalty/frequency_penalty/reasoning_effort）、**框架通用**（name/verbose/callbacks/tags/cache/rate_limiter）、**高级透传**（`model_kwargs` 传 LangChain 未定义字段如 tools；`extra_body` 传厂商扩展字段如 DeepSeek 的 `thinking` 开关）
- 调用时 **config 参数**（优先级高于初始化默认值）：`run_name`/`tags`/`callbacks`/`metadata`（LangSmith 追踪）、`max_concurrency`（限并发防限流）、`recursion_limit`（防 Agent 无限递归）、`configurable`（运行时换模型/温度——需初始化时声明 `configurable_fields`）


## 相关链接

- [[LangChain概述]] - LangChain整体认知
- [[LangChain Message与提示词模板]] - 消息体系详解
- [[LangSmith的使用]] - 调用链路追踪
- [[LangChain Tools]] - 工具调用
