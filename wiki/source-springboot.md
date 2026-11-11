---
tags: [source-summary, java, springboot, 面试]
type: source-summary
source: SpringBoot
date: 2026-06-09
---

# SpringBoot

## Spring Boot 核心优势

- 基于**自动配置**，减少开发和配置时间
- 不需要大量XML配置和样板代码
- **约定优于配置**，默认配置即可运行
- **内嵌Web容器**（Tomcat/Jetty/Undertow）
- 与Spring生态无缝集成

## @SpringBootApplication

是 `@Configuration + @EnableAutoConfiguration + @ComponentScan` 的集合

- **@EnableAutoConfiguration**：启用自动配置机制
- **@ComponentScan**：扫描@Component/@Repository/@Service/@Controller，默认扫描当前包及子包
- **@Configuration**：注册Bean到IOC容器

## 自动配置原理

1. `@EnableAutoConfiguration` 通过 `@Import` 导入 `AutoConfigurationImportSelector`
2. `getCandidateConfigurations()` 扫描 `META-INF/spring.factories`，获取自动配置类列表
3. 根据 `@Conditional` 注解判定哪些类需要加载
   - `@ConditionalOnClass`：指定类必须存在
   - `@ConditionalOnBean`：容器中有指定Bean
   - `@ConditionalOnMissingBean`：容器中没有指定Bean

## Spring Boot Starters

一系列依赖关系的集合，引入一个starter即可集成相关技术

| Starter | 用途 |
|---------|------|
| spring-boot-starter-web | Web开发 |
| spring-boot-starter-data-jpa | JPA数据库 |
| spring-boot-starter-security | 安全认证 |
| spring-boot-starter-test | 测试 |

`spring-boot-starter-parent`：官方Maven父工程，管理依赖版本号和插件配置

## 配置文件

### 核心配置文件
- **application.properties/yml**：应用程序配置
- **bootstrap.properties/yml**：Spring Cloud上下文配置（优先于application加载）

### 配置优先级（由低到高）
1. jar包内 application.properties/yml
2. jar包内 application-{profile}.properties/yml
3. jar包外 application.properties/yml
4. jar包外 application-{profile}.properties/yml

> .properties和.yml同时存在 → .properties优先

## 请求参数校验

### 常用校验注解
- `@NotNull` / `@NotEmpty` / `@NotBlank`
- `@Min` / `@Max` / `@Size`
- `@Email` / `@Pattern`
- `@Past` / `@Future`

### 使用方式
- RequestBody参数：加 `@Valid` 注解
- PathVariable/RequestParam参数：类上加 `@Validated`

## 全局异常处理

`@ControllerAdvice` + `@ExceptionHandler`

## 定时任务

- `@Scheduled` + `@EnableScheduling`
- 生产环境推荐使用 **Quartz / XXL-JOB**（支持集群、动态管理）

## 解决跨域

1. `@CrossOrigin` — 局部跨域
2. `WebMvcConfigurer.addCorsMappings()` — 全局跨域
3. `CorsFilter` — 过滤器级别
4. Spring Cloud Gateway — 网关层
5. Nginx反向代理

## SpringBoot启动流程

1. 加载 `@SpringBootApplication` 标识的启动类
2. 加载配置文件（application.properties/yml）
3. 初始化ApplicationContext（扫描Bean、注册到容器）
4. 启动内嵌Web服务器（Tomcat/Jetty）
5. 启动应用程序线程
6. 监听应用程序状态

## 相关链接

- [[Spring重要知识点]] — Spring核心知识
- [[MyBatis]] — ORM框架
- [[认证授权]] — 安全认证与授权
