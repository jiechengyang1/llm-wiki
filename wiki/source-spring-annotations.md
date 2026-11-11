---
tags: [source-summary, java, spring, 面试]
type: source-summary
source: Spring&SpringBoot常用注解总结
date: 2026-06-09
---

# Spring&SpringBoot常用注解

## Spring Bean相关

### @Autowired
- 自动注入对象，默认**按类型匹配**，多个匹配时按名称匹配
- 由Spring提供

### 组件注解

| 注解 | 层级 | 用途 |
|------|------|------|
| @Component | 通用 | 任意Spring组件 |
| @Repository | Dao层 | 数据库操作 |
| @Service | Service层 | 业务逻辑 |
| @Controller | Controller层 | 接受请求返回视图 |
| @RestController | Controller层 | @Controller + @ResponseBody，返回JSON |

### @Scope — Bean作用域

| 作用域 | 说明 |
|--------|------|
| singleton | 唯一实例（默认） |
| prototype | 每次请求创建新实例 |
| request | 每次HTTP请求一个Bean |
| session | 每个HTTP Session一个Bean |

### @Configuration
声明配置类，比@Component更语义化，配合@Bean注册Bean

## HTTP请求注解

| 注解 | 等价 |
|------|------|
| @GetMapping | @RequestMapping(method=GET) |
| @PostMapping | @RequestMapping(method=POST) |
| @PutMapping | @RequestMapping(method=PUT) |
| @DeleteMapping | @RequestMapping(method=DELETE) |

## 前后端传值

| 注解 | 用途 |
|------|------|
| @PathVariable | 获取路径参数 |
| @RequestParam | 获取查询参数（?后面） |
| @RequestBody | 读取请求体JSON，自动绑定Java对象 |

> 一个方法只能有一个@RequestBody，可有多个@RequestParam和@PathVariable

## 读取配置信息

| 注解 | 用途 |
|------|------|
| @Value("${key}") | 读取单个配置 |
| @ConfigurationProperties(prefix="xxx") | 批量读取并绑定Bean |
| @PropertySource | 读取指定properties文件 |

## 参数校验注解

### JSR标准
- @Null / @NotNull / @NotEmpty / @NotBlank
- @Min / @Max / @Size / @Digits
- @Past / @Future / @Pattern / @Email

### 使用方式
- RequestBody校验：参数加 `@Valid`
- PathVariable/RequestParam校验：类上加 `@Validated`

## 全局异常处理

- `@ControllerAdvice`：定义全局异常处理类
- `@ExceptionHandler`：声明异常处理方法

## JPA相关注解

| 注解 | 用途 |
|------|------|
| @Entity + @Table | 声明数据库实体 |
| @Id + @GeneratedValue | 主键及生成策略 |
| @Column | 声明字段属性 |
| @Transient | 不持久化 |
| @Lob | 大字段 |
| @Enumerated | 枚举字段 |

### 主键生成策略
- IDENTITY：数据库自增（MySQL常用）
- SEQUENCE：序列（Oracle/PostgreSQL）
- TABLE：专用表格
- AUTO：由持久化引擎选择（默认）

## 相关链接

- [[Spring重要知识点]] — Spring核心知识
- [[SpringBoot]] — SpringBoot框架
- [[认证授权]] — 安全认证与授权
