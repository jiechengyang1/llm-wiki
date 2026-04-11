# Spring 重要知识点

## 基础

Spring 是 Java EE 核心框架，提供 IoC 和 AOP 两大核心能力，简化企业级应用开发。

## 核心

### IOC 与 DI

**IOC（控制反转）**：将对象创建和管理权力交给外部环境（IoC 容器），用户丧失创建管理对象的权力，但得到不需要关注对象创建的好处。

**DI（依赖注入）**：IOC 的实现方式，容器实例化对象时将其依赖注入到对象中。

**IOC 解决**：
- 对象之间耦合度降低
- 资源容易管理（单例等）
- 用户专注业务开发

### AOP

**AOP（面向切面编程）**：将横切关注点（日志、事务、权限、限流等）从核心业务逻辑分离，通过动态代理或字节码操作实现代码复用和解耦。

**核心概念**：
- **Aspect（切面）**：横切关注点的封装类
- **JoinPoint（连接点）**：方法调用或执行的特定时刻
- **Advice（通知）**：切面在连接点执行的操作（Before/After/AfterReturning/AfterThrowing/Around）
- **Pointcut（切点）**：匹配连接点的表达式
- **Weaving（织入）**：将切面和目标对象连接

**Spring AOP vs AspectJ**：Spring AOP 运行时增强基于代理，AspectJ 编译时增强基于字节码操作。

**应用场景**：日志记录、性能统计、事务管理（@Transactional）、权限控制（@PreAuthorize）、接口限流、缓存管理。

### Spring 事务

**ACID 特性**：原子性、一致性、隔离性、持久性。AID 是手段，C 是目的。

**事务管理接口**：
- **PlatformTransactionManager**：事务管理器
- **TransactionDefinition**：事务定义（隔离级别、传播行为、超时、只读、回滚规则）
- **TransactionStatus**：事务状态

**传播行为**：
- REQUIRED：默认，存在事务则加入，否则创建新事务
- REQUIRES_NEW：创建新事务，挂起当前事务
- NESTED：嵌套事务，存在事务则在嵌套事务执行
- MANDATORY：必须存在事务，否则抛异常

**隔离级别**：DEFAULT、READ_UNCOMMITTED、READ_COMMITTED、REPEATABLE_READ、SERIALIZABLE

**回滚规则**：默认遇 RuntimeException 回滚，Error 也会回滚，检查型异常不回滚。

### 设计模式

- **工厂模式**：BeanFactory、ApplicationContext 创建 bean
- **单例模式**：Spring bean 默认单例，ConcurrentHashMap 实现
- **代理模式**：AOP 动态代理（JDK Proxy/Cglib）
- **模板方法**：JdbcTemplate、HibernateTemplate
- **观察者模式**：Spring 事件驱动模型（ApplicationEvent、ApplicationListener、ApplicationEventPublisher）
- **适配器模式**：Spring AOP Advice 适配器、Spring MVC HandlerAdapter
- **装饰者模式**：InputStream 系列类

### Spring Boot 自动装配

**核心机制**：
- @SpringBootApplication = @Configuration + @EnableAutoConfiguration + @ComponentScan
- @EnableAutoConfiguration 启用自动配置
- AutoConfigurationImportSelector 加载 META-INF/spring.factories 中的配置类
- @Conditional 按需加载

**实现 Starter**：创建工程引入依赖 → 创建 XXXAutoConfiguration → resources/META-INF/spring.factories 配置 → 引入 starter 使用

## 关联

- [[分布式事务]] - Seata 分布式事务
- [[Redis重要知识点]] - Redis 相关

## 标签

#Spring #IOC #AOP #事务 #自动装配 #设计模式
