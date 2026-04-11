# 资料摘要：java锁

## 锁的分类

### 1. 悲观锁 vs 乐观锁

**悲观锁**：操作前先加锁，认为数据会被其他线程修改。
- 代表：synchronized、ReentrantLock

**乐观锁**：操作时不加锁，更新时检查数据是否被修改。
- 代表：CAS、AtomicInteger

### 2. 公平锁 vs 非公平锁

**公平锁**：按请求顺序获取锁。
**非公平锁**：允许插队，可能饥饿。

```java
// 公平锁
ReentrantLock fairLock = new ReentrantLock(true);
// 非公平锁（默认）
ReentrantLock unfairLock = new ReentrantLock(false);
```

### 3. 可重入锁 vs 不可重入锁

**可重入锁**：同一线程可多次获取同一把锁。
- synchronized、ReentrantLock

**不可重入锁**：同一线程重复获取会死锁。

### 4. 独享锁 vs 共享锁

**独享锁**：一次只能被一个线程持有。
**共享锁**：可被多个线程同时持有。

## 常见锁实现

### synchronized

- JVM内置锁
- 自动获取/释放
- 不可中断
- 偏向锁→轻量级锁→重量级锁

### ReentrantLock

- java.util.concurrent包
- 可重入
- 可中断
- 可超时
- 可公平/非公平
- 支持多个条件变量

```java
ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    // 业务逻辑
} finally {
    lock.unlock();
}
```

### ReentrantReadWriteLock

- 读锁共享
- 写锁独享
- 适合读多写少场景

### StampedLock

- JDK8新增
- 支持乐观读
- 性能优于ReadWriteLock

## 死锁

四个必要条件：
1. 互斥条件
2. 请求与保持
3. 不剥夺条件
4. 循环等待

避免策略：按序加锁、银行家算法

## 锁优化

- 减小锁粒度
- 锁粗化
- 锁消除
- 读写分离

---

**相关主题：** [[并发编程]]、[[Synchronized与锁升级]]、[[CAS]]、[[AQS]]
