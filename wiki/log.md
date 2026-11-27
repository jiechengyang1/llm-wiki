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

## [2026-11-11] restructure | 知识库结构重组维护

- **目录重组**：wiki/ 下按分类建 12 个文件夹（Java基础、JVM、并发编程、Java集合、分布式、数据库、常用框架、计算机基础、项目实战、面经、AI、工具）
- **统一命名**：所有 source-*.md 重命名为中文正式名（与 index.md 链接一一对应），git mv 保留历史
- **删除冗余**：5 个 4 月旧版手写稿（被 source 版本取代）、3 个空文件（悬空链接误创建）、2 个已合并的面经源文件（qunar/zto）
- **新增索引**：[[系统设计]] 补入 index.md 项目实战分类
- **链接修复**：全库 18 处悬空 wikilink 修正为现行文件名
- **规范**：新增 .gitignore（排除 .DS_Store、未命名*.base、各工具目录）

> 此后新增知识流程：资料放入 raw/ → 生成 wiki/<分类>/<中文名>.md → 更新 index.md + log.md → git commit

## [2026-11-16] feature | 新增每日复习系统

- `wiki/每日复习/queue.md`：66 个知识点跨 12 大分类交叉轮转队列
- 每日笔记格式：今日新知（要点速览）+ 自测三题（折叠答案）+ 昨日回顾 + 明日预告
- 生成首篇 [[每日复习/2026-11-16|每日知识点 · 2026-11-16]]（JAVA基础-上，1/66）
- index.md 新增「每日学习」入口
- 设置每日 8:57 自动生成任务（对 Claude 说「今日知识点」可随时手动触发）

## [2026-11-17] daily | 每日知识点：JVM和Java体系（2/66）

## [2026-11-17] ingest | 导入尚硅谷 LangChain 课程（10 讲）

- **进料**：raw/01-课件/（10 份 PDF 讲义，共约 67MB，git 存档）
- **产出**：wiki/AI/ 新增 10 篇摘要页——[[LangChain概述]]、[[LangChain模型的创建与调用]]、[[LangSmith的使用]]、[[LangChain Message与提示词模板]]、[[LangChain Tools]]、[[LangChain结构化输出]]、[[LangChain智能体]]、[[LangChain中间件]]、[[LangChain上下文与记忆]]、[[LangChain RAG]]
- **登记**：index.md AI 分类新增 10 条；每日复习队列 66 → 76（AI 追加 10 讲，rows 67-76）

## [2026-11-18] daily | 每日知识点：并发编程（3/76）

- 生成 [[每日复习/2026-11-18|每日知识点 · 2026-11-18]]（今日新知：并发编程；昨日回顾：JVM和Java体系）
- queue.md 第 3 行填入完成日期，进度 3/76

## [2026-11-26] daily | 每日知识点：Java集合（4/76）

- 生成 [[每日复习/2026-11-26|每日知识点 · 2026-11-26]]（今日新知：Java集合；昨日回顾：并发编程）
- queue.md 第 4 行填入完成日期，进度 4/76

## [2026-11-27] daily | 每日知识点：分布式锁（5/76）

- 生成 [[每日复习/2026-11-27|每日知识点 · 2026-11-27]]（今日新知：分布式锁；昨日回顾：Java集合）
- queue.md 第 5 行填入完成日期，进度 5/76
