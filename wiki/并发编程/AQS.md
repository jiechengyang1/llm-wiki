# 资料摘要：AbstractQueuedSynchronizer之AQS

## 基本概念

AQS是JDK并发包的核心抽象类，定义了锁的底层实现机制，是实现ReentrantLock、CountDownLatch、Semaphore、CyclicBarrier等同步器的基础。

## 核心思想

- 状态管理：通过`state`变量表示资源状态
- 队列管理：FIFO双向队列管理等待线程
- 模板方法：子类实现`tryAcquire`、`tryRelease`等方法

## 两种模式

### 独占模式（Exclusive）
- 同一时刻只有一个线程获取锁
- 实现：`tryAcquire`、`tryRelease`
- 代表：ReentrantLock

### 共享模式（Shared）
- 多个线程可同时获取锁
- 实现：`tryAcquireShared`、`tryReleaseShared`
- 代表：CountDownLatch、Semaphore

## 队列结构

```
Node {
    prev / next      // 双向链表
    thread           // 等待线程
    waitStatus       // 等待状态
    SHARED / EXCLUSIVE  // 模式标记
}
```

等待状态（waitStatus）：
- 0：初始状态
- CANCELLED(1)：已取消
- SIGNAL(-1)：后继节点需要唤醒
- CONDITION(-2)：等待条件
- PROPAGATE(-3)：传播（共享模式）

##  acquire流程

1. 调用`tryAcquire`尝试获取锁
2. 失败则创建Node加入队列
3. `acquireQueued`使线程阻塞
4. 被唤醒后检查是否需要前驱节点出队

##  release流程

1. 调用`tryRelease`释放锁
2. 唤醒后继节点
3. 后继节点尝试获取锁

##  Condition实现

- `await()`：当前线程进入等待队列
- `signal()`：唤醒一个等待线程
- `signalAll()`：唤醒所有等待线程

每个Condition对应一个单向等待队列。

##  公平锁 vs 非公平锁

**公平锁**：获取锁前检查是否有前驱节点
**非公平锁**：直接尝试获取，可能插队

```java
// 非公平锁tryAcquire
if (compareAndSetState(0, 1)) {
    setExclusiveOwnerThread(Thread.currentThread());
    return true;
}

// 公平锁tryAcquire
if (compareAndSetState(0, 1)) {
    setExclusiveOwnerThread(Thread.currentThread());
    return true;
}
// 多一个hasQueuedPredecessors检查
```

##  子类可重写的方法

- `tryAcquire(arg)` - 独占模式获取
- `tryRelease(arg)` - 独占模式释放
- `tryAcquireShared(arg)` - 共享模式获取
- `tryReleaseShared(arg)` - 共享模式释放
- `isHeldExclusively()` - 是否独占模式

##  资源获取工具

| 工具 | 作用 | 模式 |
|------|------|------|
| CountDownLatch | 倒计时 | 共享 |
| Semaphore | 信号量 | 共享 |
| CyclicBarrier | 循环栅栏 | 共享 |
| ReentrantLock | 可重入锁 | 独占 |

---

**相关主题：** [[并发编程]]、[[java锁]]、[[Synchronized与锁升级]]
