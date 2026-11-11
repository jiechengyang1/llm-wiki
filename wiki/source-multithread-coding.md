---
tags: [source-summary, java, 并发编程, 算法, 面试]
type: source-summary
source: 多线程手撕常见代码
date: 2026-06-09
---

# 多线程手撕常见代码

## 两个线程交替打印1-100

核心思路：用 `(count + 1) % 2 == threadId` 判断轮到哪个线程

### 实现方式对比

| 方式 | 特点 |
|------|------|
| Semaphore | acquire/release，需双重校验 |
| ReentrantLock.tryLock() | 非阻塞，不需要双重校验 |
| ReentrantLock + Condition | await/signal精确唤醒，最优 |
| synchronized + wait/notifyAll | 经典方式，需while防虚假唤醒 |

### 推荐写法：synchronized + wait + notifyAll

```java
while (count <= MAX) {
    synchronized (lock) {
        while ((count - 1) % 2 != threadId) {
            lock.wait(); // 防虚假唤醒用while
        }
        if (count <= MAX) {
            System.out.println(count++);
            lock.notifyAll();
        }
    }
}
```

## 三个线程交替打印1-100

核心思路：将 `% 2` 改为 `% 3`，逻辑相同

### 推荐写法：ReentrantLock + Condition

```java
Condition[] conditions = {lock.newCondition(), lock.newCondition(), lock.newCondition()};
// 精确唤醒下一个线程
conditions[(threadId + 1) % 3].signal();
```

## 三个线程ABC交替打印123（10次）

```java
for (int i = 0; i < 10; i++) {
    synchronized (lock) {
        while (count != threadId) { lock.wait(); }
        System.out.println(threadId);
        count = count % 3 + 1; // 1→2→3→1
        lock.notifyAll();
    }
}
```

## 两个线程打印12A34B

核心：数字线程打2个，字母线程打1个，交替进行

```java
// 数字线程
System.out.println(count * 2 - 1);
System.out.println(count * 2);
// 字母线程
System.out.println((char)('A' + count - 1));
count++;
```

## 100个线程对变量加1操作100次

使用 `AtomicInteger` 保证原子性

```java
AtomicInteger count = new AtomicInteger(0);
count.incrementAndGet(); // 原子操作
```

## 手撕单例模式（双重检查锁）

```java
class Singleton {
    private Singleton() {}
    private static volatile Singleton instance;
    public static Singleton getInstance() {
        if (instance == null) {              // 第一次检查
            synchronized (Singleton.class) {
                if (instance == null) {      // 第二次检查
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

**为什么需要volatile？** 防止指令重排序：
- `instance = new Singleton()` 分三步：①分配内存 → ②初始化对象 → ③指向地址
- 重排序可能变为 ①→③→②，导致其他线程拿到未初始化的对象

## 生产者消费者模型

### 方式1：Semaphore

```java
Semaphore mutex = new Semaphore(1);  // 互斥
Semaphore empty = new Semaphore(10); // 空位
Semaphore full = new Semaphore(0);   // 产品
```

### 方式2：BlockingQueue（推荐）

```java
BlockingQueue<Integer> queue = new ArrayBlockingQueue<>(10);
queue.put(item);  // 队列满时阻塞
queue.take();     // 队列空时阻塞
```

## 手撕独占锁（基于AQS）

```java
class Sync extends AbstractQueuedSynchronizer {
    protected boolean tryAcquire(int arg) {
        if (compareAndSetState(0, 1)) {
            setExclusiveOwnerThread(Thread.currentThread());
            return true;
        }
        return false;
    }
    protected boolean tryRelease(int arg) {
        setExclusiveOwnerThread(null);
        setState(0);
        return true;
    }
    protected boolean isHeldExclusively() {
        return getState() == 1;
    }
}
```

## 相关链接

- [[并发编程]] — 并发编程基础
- [[AQS]] — 抽象队列同步器
- [[java锁]] — 锁分类与实现
- [[CAS]] — CAS原理与应用
- [[线程池源码解析]] — 线程池实现原理
