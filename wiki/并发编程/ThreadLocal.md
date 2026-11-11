# 资料摘要：ThreadLocal

## 概念

线程局部变量，每个线程拥有独立的变量副本，互不干扰。

## 数据结构

- ThreadLocalMap（类似HashMap但无链表）
- Entry弱引用ThreadLocal作为key
- 线性探测法解决冲突

## Hash算法

`threadLocalHashCode = 0x61c88647`（斐波那契数）

分布均匀，减少冲突。

## 线程隔离原理

每个Thread对象内部有threadLocals变量（ThreadLocalMap），以ThreadLocal弱引用为key存储值。

## 内存泄漏问题

**为什么用弱引用？**
- 强引用：ThreadLocal对象无法被回收
- 弱引用：GC时key=null，可回收

**但仍有风险：**
- key=null后，value无法被回收（除非手动remove）
- ThreadLocalMap在get/set时会清理过期Entry

**最佳实践：**
- 手动调用remove()
- 避免长期持有

## 扩容机制

- 阈值 = len * 2/3
- 扩容条件：size >= threshold * 3/4
- 扩容大小：oldLen * 2

## 三种ThreadLocal

| 类型 | 作用 |
|------|------|
| ThreadLocal | 线程隔离 |
| InheritableThreadLocal | 父子线程传递 |
| TransmittableThreadLocal | 线程池场景传递 |

## 使用场景

- 线程间数据隔离
- 避免参数传递
- 数据库连接、Session管理
- 链路追踪

---

**相关主题：** [[并发编程]]
