# 资料摘要：CAS

## 基本概念

CAS（Compare-And-Swap）是一种乐观锁机制，通过硬件层面的原子指令实现无锁并发。

## 核心原理

三个操作数：
- 内存位置 V
- 预期原值 A
- 新值 B

当且仅当 V 的值等于 A 时，才将 V 更新为 B；否则不做任何操作。

## Java实现

- `sun.misc.Unsafe` - 直接操作内存
- `java.util.concurrent.atomic` - 原子类封装

常见原子类：`AtomicInteger`、`AtomicLong`、`AtomicReference`、`AtomicStampedReference`（解决ABA问题）

## ABA问题

问题：线程1读取V为A，线程2将V改为B再改回A，线程1仍认为V未被修改。

解决方案：
- 版本号机制：`AtomicStampedReference`
- 时间戳：`AtomicMarkableReference`

## 应用场景

- 计数器更新
- 乐观并发控制
- 无锁数据结构（如ConcurrentHashMap内部）

## 与synchronized对比

| 特性 | CAS | synchronized |
|------|-----|--------------|
| 类型 | 乐观锁 | 悲观锁 |
| 实现 | 硬件指令 | JVM内置锁 |
| 适用场景 | 冲突较少 | 冲突较多 |
| 线程阻塞 | 否 | 是 |
| 原子性保证 | 硬件级 | JVM级 |

## 注意事项

- CAS只保证单个变量的原子性
- 循环CAS长时间不成功会带来CPU开销
- 仍然无法解决ABA问题（需额外机制）

---

**相关主题：** [[并发编程]]、[[Synchronized与锁升级]]、[[AQS]]
