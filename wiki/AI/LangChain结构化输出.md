---
tags: [source-summary, AI, LangChain]
type: source-summary
source: 尚硅谷-06-结构化输出
date: 2026-11-17
---

# LangChain 结构化输出

## 核心要点

### 概述
- **定义**：要求模型最终返回符合预定义结构的数据对象（固定字段的 JSON / Pydantic 模型 / TypedDict），而非无格式自然语言
- **核心目标**：把「自然语言回答」变成「程序可以稳定消费的数据」
- **三大价值**：
	1. 更容易被代码处理——下游系统直接读字段，不用再从自然语言里解析
	2. 结果更稳定——减少「说法变了但意思差不多」导致的解析失败
	3. 更适合工程化——表单抽取、分类、路由、工具参数生成、工作流状态传递
- **传统方式对比**：Prompt 里苦求「请返回 JSON」+ `json.loads()` + 手动 `isinstance` 校验 + 手动建对象 → 繁琐不推荐；`with_structured_output` 一步到位

### 基本用法
```python
class Person(BaseModel):
    """人物信息"""
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")

structured_llm = model.with_structured_output(Person)
result = structured_llm.invoke("张三是一名30岁的软件工程师")
result.name  # '张三' —— 直接点属性，无需解析
```
- 三要素：继承 `BaseModel` + 类型提示（str/int/List/Optional）+ `Field(description=...)`（没有描述 LLM 可能格式错误）
- 受欢迎的原因：**Prompt 变干净**（字段 description 直接充当提示词一部分）、**类型安全**（编辑器自动补全、运行前类型检查）、**极其稳定**（依托厂商底层 JSON 模式）
- 模型支持：OpenAI / Anthropic / Groq 等现代模型都支持（经函数调用）；不支持的旧模型 LangChain 会回退到提示词 + JSON 解析

### 四种 Schema 模式对比
| 模式 | 返回类型 | 类型校验 | 适用场景 |
|------|---------|---------|---------|
| **Pydantic** | Schema 类实例 | ✅ 不匹配抛异常 | 生产首选（字段校验/描述/嵌套，功能最丰富） |
| **TypedDict** | 字典 | ❌ | 轻量类型约束 |
| **JSON Schema** | 字典 | ❌ | 前后端跨语言接口最通用 |
| **@dataclass** | 字典 | ❌ | 简洁数据类定义 |

- 共同入口：模型对象调用 `with_structured_output(schema)` 绑定输出模式

### Pydantic 高级特性
- **可选字段**：`Optional[int]` → LLM 未提供时填 `None`（非 Optional 会拿到 0/1 之类的脏值）
- **默认值**：`Field(30, description=...)` → 未提供时用默认值；不同厂商对 default 字段支持不同
- **枚举限制**：`class Priority(str, Enum)` 或 `Literal["低","中","高"]` 限定字段可选值
- **列表提取**：字段用 `List[Person]` / `List[str]`——人物列表、评论优缺点、发票商品；适合批量评论分析、报告生成
- **嵌套结构**：模型套模型（`Movie` → `cast: List[Actor]`，`Company` → `address: Address`）；建议**嵌套 ≤ 3 层**，复杂嵌套易出错——用清晰 description，必要时拆成多次调用
- **限制条件**：`min_length` / `ge` / `gt` / `le` 等运行时校验（如 `price: float = Field(gt=0)`）；超范围抛 `ValidationError`

### 内部工作流程（四步）
1. **定义结构**：写 Pydantic 模型
2. **协议转换**：LangChain 调 `model_json_schema()` 把 Python 类转成标准 JSON Schema（字段、类型、描述的严格 JSON 文本）
3. **模型交互与强约束**：Schema 包装进 API 请求，作为 Tools 传入；OpenAI `strict=True` 启动**语法采样约束**——解码 token 时按 Schema 语法树选择，底层保证格式不走样
4. **自动解析与验证**：解析器接管——字符串解析为字典 → 喂给 Pydantic 验证（漏字段/类型错直接抛异常或触发重试）→ 返回可点属性的对象

### TypedDict 要点
- `TypedDict` 是 Python 3.8+ 的类型提示工具：声明字典有哪些字段、各字段什么类型；**只是类型声明，非运行时校验**（字段名不匹配仅 IDE 静态检查标记，运行照常输出）
- 字段描述用 `Annotated[str, "电影标题"]`（Annotated = 类型 + 附加元数据，类似 Pydantic 的 Field）
- `Annotated[str, ..., "说明"]`：`...` 即 Ellipsis 占位符，LangChain 约定该字段**必填**——缺失时输出中仍带该字段（值为空串），未标记的缺失字段被直接省略

### 类型校验实验（fake server）
- 构造虚拟 DeepSeek 服务端，人为返回字段不匹配的响应（`title1`/`year2`）观察四种模式行为
- 结论：**只有 Pydantic 抛 `ValidationError`**（字段缺失直接报错）；TypedDict / JSON Schema / @dataclass 都原样返回字典、不报错

### 获取结构化结果的两种方式
- **with_structured_output（推荐，v1.x 最新最简）**：模型「理解」数据结构并返回解析好的对象
- `with_structured_output(Movie, include_raw=True)` → 返回三字段字典：`raw`（原始 AIMessage，含 token 用量）、`parsed`（解析后对象）、`parsing_error`（解析错误；仅 Pydantic 校验失败会报）
- **输出解析器（传统，不推荐）**：`JsonOutputParser(pydantic_object=Movie)` + 提示词明确指示格式 → `prompt | model | parser` 链式转换，返回字典

## 相关链接

- [[LangChain Tools]] - 底层同为 tool calling / JSON Schema 机制
- [[LangChain概述]] - LangChain整体认知（v1.x 结构化输出是一等公民）
- [[LangChain Message与提示词模板]] - 消息体系
- [[Agent Skills]] - 智能体技能体系
