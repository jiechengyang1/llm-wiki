# 中通面经

## 基础

中通快递技术面试题，主要涵盖 Java 队列、MQ、线程池、JVM 调优、并发编程、MySQL 索引等内容。

## 核心

### Java 队列

- 常见队列类型：ArrayList、LinkedList、PriorityQueue、DelayQueue、SynchronousQueue 等
- 阻塞队列实现：ReentrantLock + Condition
- Buffer 队列实现

### 消息队列

- 消费者顺序消费保证
- 队列与消费者关系：一对多/多对多
- 消息只被一个消费者消费：独占消费/手动 ACK
- 一个队列消息被多个消费者消费：广播模式/共享消费

### 线程池

- 延迟队列实现：DelayedWorkQueue
- 线程复用原理

### JVM 调优

- CPU 负载超 90% 排查：top → top -Hp → jstack
- jmap 导出堆转储后关注内容：对象数量、大小、GC Roots
- 导致 CPU 负载高的因素：频繁 GC、死循环、锁竞争、I/O 阻塞

### 并发编程

- 线程安全问题：共享资源 + 非原子操作
- 解决方案：synchronized、Lock、无锁 CAS

### MySQL

- 索引调优：覆盖索引、最左前缀、避免回表
- 联合索引顺序确定：区分度高的列、查询频率、Cardinality
- 三列索引构建示例：时间 + 性别 + 身份证（根据查询场景选择顺序）

## 标签

#面经 #中通 #面试题 #JVM调优
