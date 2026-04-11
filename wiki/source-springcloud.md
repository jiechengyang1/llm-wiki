# Spring Cloud 微服务架构

## 概述

Spring Cloud 是微服务架构的综合解决方案，整合了分布式系统中的各种组件和服务治理能力。

## 核心组件

### Nacos 服务发现与配置管理

**服务发现**：客户端向Nacos注册中心注册服务，服务提供者和消费者通过Nacos获取服务实例列表，支持临时实例（心跳检测）和永久实例（手动注册）。

**配置管理**：配置文件的拉取和热更新机制，支持命名空间隔离（dev/test/prod）和配置分组管理。

**健康检查**：支持心跳检测、TCP、HTTP等方式检测服务健康状态，不健康的实例会被从服务列表中剔除。

### Gateway 网关

**路由功能**：匹配用户请求的Path、Host、Header等条件，将请求转发到对应的后端服务实例，支持路径重写。

**负载均衡**：内置负载均衡器，根据RoundRobin、Random、WeightedResponseTime等策略分配请求到不同实例。

**过滤器链**：Pre过滤器（鉴权、限流、路径重写）→ 后端服务 → Post过滤器（响应头处理、链路追踪）。

### Sentinel 流量控制

**流控规则**：QPS阈值、并发线程数限流，支持直接拒绝、冷启动、匀速排队等流控效果。

**降级熔断**：RT响应时间、异常比例、异常数降级规则，自动熔断不健康实例，恢复后逐步放行请求。

**热点规则**：对携带参数的方法进行流控，参数索引和参数值维度限流。

**授权规则**：黑白名单过滤请求来源。

### Feign 远程服务调用

**声明式HTTP客户端**：通过@FeignClient定义接口，自动完成HTTP请求的构造和响应解析。

**负载均衡**：集成Ribbon，提供轮询、随机、重试、加权等负载均衡策略。

**降级机制**：通过fallback类在服务不可用时返回降级数据，支持和Hystrix或Sentinel集成。

**日志配置**：debug日志级别下可看到完整的请求响应信息。

### 负载均衡策略

**Ribbon策略**：RoundRobinRule（轮询）、RandomRule（随机）、WeightedResponseTimeRule（响应时间加权）、BestAvailableRule（最小并发）、ZoneAvoidanceRule（区域可用性）。

**SpringCloud LoadBalancer**：Netflix Ribbon已停止维护，官方推荐使用Spring Cloud LoadBalancer替代。

### 链路追踪

**Sleuth + Zipkin**：在请求中注入TraceId和SpanId，记录整个调用链路的耗时和调用关系，支持可视化查看。

**请求流程**：外部请求 → 网关（添加TraceId）→ 业务服务（创建Span）→ 数据库/缓存 → 响应返回 → Zipkin收集展示。

## 相关技术

- 服务治理：Nacos、Zookeeper、Eureka
- 网关：Gateway、Zuul
- 流量控制：Sentinel、Hystrix
- 远程调用：Feign、OpenFeign、Dubbo
- 链路追踪：Sleuth、Zipkin、Jaeger

## 相关文件

- 源文件：raw/java-interview/分布式/SpringCloud/index.md