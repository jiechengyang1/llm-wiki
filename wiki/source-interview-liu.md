# 刘老板面经

## 基础

刘老板面经涵盖了多家公司的面试题目，包括经纬恒润、用友、美团、快手、陌陌、迅雷、58等公司的一二三面技术面试内容。

## 核心

### 高频技术问题

**Spring**：
- Spring Bean 生命周期
- 循环依赖如何解决？对象工厂原理？
- Spring 设计模式：单例、代理、适配器、模板方法、工厂、迭代器、责任链、原型、观察者
- Spring IOC 好处

**并发编程**：
- ThreadLocal 使用场景？内存泄漏问题？
- synchronized 底层原理？可重入？
- ReentrantLock 实现原理？Condition 与 Object.wait 区别？
- ReentrantReadWriteLock 读写锁
- 线程池执行流程
- wait 和 sleep 区别

**JVM**：
- 内存区域，哪些线程共享？线程安全问题？
- 什么情况下会有线程安全问题？

**Redis**：
- 数据结构？Zset 用途？底层跳表？压缩列表问题？
- 主从复制、Cluster、Sentinel 区别？
- 集群分片？一致性哈希？虚拟节点？
- Pipeline 用途？与原生批命令区别？
- 过期数据清理时机
- 分布式锁 set nx 命令？问题？

**MySQL**：
- 事务特性？隔离级别？InnoDB 默认？实现？
- 索引数据结构为什么是 B+ 树？
- 索引页分裂？回表？索引设计原则？

**分布式**：
- CAP 理论？Nacos 是 CP 还是 AP？
- 分布式锁实现
- Nacos 一致性协议（Distro/Raft）

**消息队列**：
- RocketMQ vs Kafka 区别？零拷贝？
- RocketMQ 事务消息实现
- 消费语义、投递语义

### 手撕代码

- 单例懒加载（双重检查 volatile）
- 堆排序
- LRU 算法
- 交替打印 100 个数字
- 寻找文件路径
- 数组中唯一出现奇数次的数
- 小于 n 的最大数

### 其他问题

- 限流算法？Sentinel？
- 布隆过滤器原理？bitmap 问题？
- 短链接生成方案
- MD5 加盐
- 优先级倒置、CPU 亲和性

## 关联

- [[Spring重要知识点]] - Spring 相关
- [[Redis重要知识点]] - Redis 相关
- [[并发编程]] - Java 并发

## 标签

#面经 #面试题 #春招 #秋招 #实习
