# 操作日志

## [2026-04-10] initialize | 初始化 Java 面试知识库

- 开始导入 java-interview 知识库
- 共 80+ 篇原始资料
- 分类：JAVA 基础/IO/新特性、JVM、并发编程、集合、分布式、常用框架、数据库、计算机基础、面经等

## [2026-06-09] ingest | 导入未消化资料

导入 raw/ 中尚未进入 wiki 的原始资料，新增 20+ 页面：

### JVM补充（4篇）
- source-jvm-architecture.md → [[JVM和Java体系]]
- source-jvm-execution-engine.md → [[执行引擎]]
- source-jvm-object-layout.md → [[对象的实例化与内存布局]]
- source-jvm-stringtable.md → [[StringTable字符串常量池]]

### 并发编程补充（3篇）
- source-completable-future.md → [[CompletableFuture]]
- source-threadpool.md → [[线程池源码解析]]
- source-java-object-header.md → [[Java对象内存布局与对象头]]

### 常用框架补充（3篇）
- source-springboot.md → [[SpringBoot]]
- source-spring-annotations.md → [[Spring&SpringBoot常用注解]]
- source-auth-authorization.md → [[认证授权]]

### 分布式与数据库补充（3篇）
- source-springcloud.md → [[SpringCloud]]
- source-idempotent.md → [[分布式幂等性]]
- source-database-basics.md → [[数据库基础知识]]

### 项目实战与算法（3篇）
- source-multithread-coding.md → [[多线程手撕常见代码]]
- source-project-onecoupon.md → [[oneCoupon优惠券系统]]
- source-project-mahjong-community.md → [[麻将社区（黑马头条改版）]]

### 面经补充（1篇）
- source-interview-collection.md → [[面经集合补充]]（中通/去哪儿/灵犀/科大讯飞/美团/百度/贝壳）

### AI（1篇）
- source-agent-skills.md → [[Agent Skills]]

### 索引更新
- 更新 wiki/index.md，新增所有页面链接和分类

## [2026-07-08] ingest | 新增 MySQL 死锁专题页

- source-mysql-deadlock.md → [[MySQL死锁专题]]
- 内容涵盖：死锁定义与四个必要条件、InnoDB锁体系回顾、死锁检测机制、6大经典死锁场景（交叉更新、Gap Lock互锁、唯一键冲突、UPDATE+INSERT、不同索引锁冲突、DELETE相邻记录）、排查方法、死锁日志阅读指南、避免死锁的17条最佳实践、面试速记
- 更新 wiki/index.md 数据库分类，新增 [[MySQL死锁专题]]
