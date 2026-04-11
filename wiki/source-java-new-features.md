---
tags: [source-summary, java, 面试, 新特性]
type: source-summary
source: JAVA新特性
date: 2024-07-19
---

# Java新特性

## Java 8 新特性

### 接口默认方法
- default修饰的方法有方法体
- static修饰的方法类似静态方法
- 解决接口修改与实现不兼容问题

### 函数式接口
- SAM接口：Single Abstract Method
- @FunctionalInterface注解
- java.util.function包提供常用函数式接口

### Lambda表达式
- 匿名函数，简化代码
- 替代匿名内部类
- 格式：(params) -> expression 或 (params) -> { statements; }
- 访问外部变量需final

### Stream
- java.util.stream包
- 串行流stream() / 并行流parallelStream()
- 延迟执行：调用非Stream方法才执行
- 常用方法：filter/map/sorted/collect

### Optional
- 防止NPE
- ofNullable/of创建
- map/flatMap转换
- isPresent/ifPresent判断

### Date-Time API
- LocalDateTime/LocalDate/LocalTime
- 线程安全
- 格式化：DateTimeFormatter

## Java 17 新特性

### 增强伪随机数生成器
- RandomGeneratorFactory
- 支持多种PRNG算法

### Switch类型匹配
- instanceof模式匹配
- switch支持类型自动转换

## 相关概念

- [[java-basic-1]] - JAVA基础上
- [[java-basic-2]] - JAVA基础下
- [[java-io]] - JAVA IO
