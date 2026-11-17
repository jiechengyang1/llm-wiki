---
tags: [source-summary, AI, LangChain]
type: source-summary
source: 尚硅谷-05-Tools
date: 2026-11-17
---

# LangChain Tools

## 核心要点

### 工具是什么
- **定义**：明确定义了输入和输出的可调用函数；工具调用（Tool Calling）也叫函数调用（Function Calling）
- **价值**：让 LLM 从「认识世界」走向「改变世界」——执行搜索、计算、数据库查询、邮件发送、调用第三方 API；是构建智能体的核心要素之一
- **两种调用方式**：直接 `.invoke()`（测试用，开发者手动传参）vs 绑定到模型 `bind_tools()`（主流，由 AI 根据上下文决定是否调用及传什么参数）

### 工具调用四步流程（Message 流转）
1. `model.bind_tools([...])` 绑定一个或多个工具
2. 用户提问 → 模型返回含 `tool_calls`（工具名+参数）的 **AIMessage**
3. 开发者手动执行工具：`get_weather.invoke(tool_call)`（@tool 修饰的工具直接返回 **ToolMessage**，无需手动拼接）
4. 工具结果回传模型，生成最终回复

```python
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气"""
    return "晴天，温度15°C"

model_with_tools = model.bind_tools([get_weather])
response = model_with_tools.invoke("北京天气如何？")
print(response.tool_calls)  # [{'name': 'get_weather', 'args': {'city': '北京'}, ...}]
```

- 消息序列：HumanMessage → AIMessage(tool_calls) → ToolMessage → AIMessage(最终回答)
- 注意：模型调用工具是**单次推理**，不会自己循环——多轮调用要开发者 `while True` 直到 `tool_calls` 为空

### 定义方式1：普通函数（不用 @tool）
- `bind_tools` 底层调用 **convert_to_openai_tool** 生成工具描述（JSON Schema：name / description / parameters）
- 普通（callable）函数走 `_convert_python_function_to_openai_function` 分支：基于函数定义 + docstring 生成 Pydantic 模式再转规范 schema
- **AI 依赖 docstring 理解工具**：描述必须遵循 **Google 风格**（Args: / Returns:），清晰准确是工具被正确调用的前提
- 参数类型来自**类型注解**；有默认值的参数不进 `required` 列表、描述中带 `default` 字段
- docstring 写了参数说明则对应参数**必须有类型注解**，否则报 `ValueError: Arg ... not found in function signature`

### 定义方式2：@tool 装饰器（推荐）
- `@tool` 自动把普通 Python 函数转为可调用工具，代码量最少；无 docstring 且无 description 时报错
- `@tool(description="...")`：覆盖工具描述，**优先级高于 docstring**
- `@tool(parse_docstring=True)`：解析 docstring 填充各参数 description；此时 docstring 不合法（非 Google 风格）会**抛异常**（不加 @tool 时只是当普通文本）
- `@tool("新名字")`（即 name_or_callable，参数名可省）：改工具名；开发习惯用函数名，**不推荐改名**
- 不要用 `config` / `runtime` 作参数名——LangChain 内部保留字

### args_schema：参数复杂时
- **方式1：Pydantic 模型**（首选）——继承 `BaseModel`，字段用 `Field(description=..., default=...)` 定制；`Literal["celsius", "fahrenheit"]` 限定枚举值；Pydantic 在调用前自动校验参数类型
- **方式2：JSON Schema 字典**——`@tool(args_schema=json_schema_dict)`，适合参数结构需要**运行时动态生成**的场景（基于数据库配置或用户输入）
- 注意：BaseModel 子类初始化**只接受关键字参数**（`__init__(self, /, **data)`），传位置参数报 TypeError

```python
class WeatherInput(BaseModel):
    city: str = Field(default="北京", description="城市名称")
    unit: Literal["celsius", "fahrenheit"] = Field(default="celsius", description="气温单位")

@tool(args_schema=WeatherInput)
def get_weather(city: str, unit: str = "celsius") -> str:
    """获取当日天气，可选未来五日天气预报"""
    ...
```

### 强制使用工具：tool_choice
- `bind_tools([...], tool_choice=X)` 控制是否强制调用（OpenAI / DeepSeek 规定一致）：
	- `none`：不调用任何工具
	- `auto`：默认值，模型自主决定调用与否
	- `required`（`any` 等价）：必须调用工具，数量不限——即使问「你好」也硬调
	- 直接传**工具名字符串**：强制调用指定工具（如 `tool_choice="get_weather2"`）

### 实践经验总结
1. **清晰描述**：docstring 即模型理解工具的说明书——「做一些事情」不行，「搜索航班信息，Args: origin: 出发城市…」才行
2. **功能单一**：一个工具只做一件事；不要写 `do_everything(action, data)` 什么都干
3. **失败三层防护**：工具内部 `try/except` 返回错误文案 → Agent 级 prompt 引导换方法 → 调用级 `@retry`（tenacity 的 `stop_after_attempt(3)`：失败拦截重试，连续 3 次才真正抛错）
4. **返回字符串**：LLM 本质只吃文本——返回 dict 会默认 Unicode 转义（中文「张三」会变成 `\u5f20\u4e09` 这样的转义序列），干扰模型稳定性；用 `json.dumps(user, ensure_ascii=False)` 输出纯中文 JSON
5. **同步 vs 异步**：CPU 密集用同步 `@tool`；IO 密集（API / 数据库 / 文件）用 `async def` + `await`

## 相关链接

- [[LangChain概述]] - LangChain整体认知
- [[LangChain Message与提示词模板]] - ToolMessage 在消息流中的位置
- [[LangChain结构化输出]] - args_schema 与结构化输出同源的 Pydantic 体系
- [[LangChain智能体]] - 工具是智能体的核心要素
- [[Agent Skills]] - 智能体技能体系
