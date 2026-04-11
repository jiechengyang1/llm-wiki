# 去哪儿面经

## 基础

去哪儿一面技术面试题，涵盖 Redis、并发编程、MySQL、Spring、设计模式等内容。

## 核心

### Redis

- 数据结构：String、Hash、List、Set、Zset
- Zset 实现原理：跳表 + 压缩列表
- 压缩列表被取代原因：连锁更新问题
- 持久化机制：RDB（默认）、AOF（appendonly yes 开启）
- volatile 为什么不保证原子性，原子类如何保证

### 并发编程

- synchronized vs Lock 区别
- 锁升级过程：无锁 → 偏向锁 → 轻量级锁 → 重量级锁
- JUC 常用组件
- 线程池复用机制
- 线程状态：新建、就绪、运行、阻塞、终止
- 阻塞线程唤醒：Object.wait / LockSupport.park
- notify vs notifyAll
- 线程池关闭：shutdown、shutdownNow、isTerminated、awaitTermination
- 关闭抛出的异常类型

### MySQL

- 最左匹配原则
- 主从复制原理
- 三大日志：redo log、binlog、undo log
- delete vs drop vs truncate
- SQL 执行顺序：from → join → on → where → group by → having → select → distinct → order by
- varchar(50) 含义及超长处理

### Spring

- 常用注解
- @Autowired vs @Resource 区别
- 注解可以加的位置：属性、方法、构造器
- Bean 生命周期
- AOP 动态代理原理

### 设计模式

- 单例模式：懒汉式 vs 饿汉式
- 线程安全保证

### 手撕算法

- 最小长度的连续子数组

## 标签

#面经 #去哪儿 #面试题
