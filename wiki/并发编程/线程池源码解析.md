---
tags: [source-summary, java, 并发编程, 面试]
type: source-summary
source: 线程池源码解析
date: 2026-06-09
---

# 线程池源码解析

## 核心属性

### ctl — 状态与线程数的统一管理

`AtomicInteger ctl`：高3位=线程池状态，低29位=工作线程数量

```java
private static final int RUNNING    = -1 << 29; // 111 00000... 接受新任务+处理队列任务
private static final int SHUTDOWN   =  0 << 29; // 000 00000... 不接受新任务+处理队列任务
private static final int STOP       =  1 << 29; // 001 00000... 不接受+不处理+中断进行中
private static final int TIDYING    =  2 << 29; // 010 00000... 所有任务中止+线程数为0
private static final int TERMINATED =  3 << 29; // 011 00000... terminated()执行完毕
```

### 核心参数

| 参数 | 说明 |
|------|------|
| `corePoolSize` | 核心线程数 |
| `maximumPoolSize` | 最大线程数 |
| `keepAliveTime` | 非核心线程空闲存活时间 |
| `workQueue` | 任务阻塞队列 |
| `threadFactory` | 线程工厂 |
| `handler` | 拒绝策略 |
| `allowCoreThreadTimeOut` | 是否允许核心线程超时退出（默认false） |

> 创建线程池后**0个线程**，提交任务才创建

## 线程池生命周期

```
RUNNING → SHUTDOWN → STOP → TIDYING → TERMINATED
  ↓shutdown()    ↓shutdownNow()   ↓所有任务中止+线程数为0  ↓terminated()完成
```

## execute()执行流程

```
1. 线程数 < corePoolSize → 创建核心线程执行任务
2. 线程数 >= corePoolSize → 任务入队列
3. 队列满 → 创建非核心线程执行任务
4. 线程数 >= maximumPoolSize → 执行拒绝策略
```

## addWorker()创建工作线程

1. CAS循环将线程数+1
2. 创建Worker对象（封装firstTask + Thread）
3. 加锁 → 添加到workers集合 → 启动线程

## getTask()获取任务

- 核心线程：`workQueue.take()` — 阻塞等待
- 非核心线程：`workQueue.poll(keepAliveTime)` — 超时返回null
- 返回null → Worker退出 → `processWorkerExit()`

### keepAliveTime的含义

| allowCoreThreadTimeOut | 含义 |
|------------------------|------|
| false（默认） | 空闲**非核心线程**的存活周期 |
| true | 空闲**所有线程**（含核心）的存活周期 |

## processWorkerExit()线程退出处理

1. 线程数-1
2. 从workers集合移除
3. 尝试终止线程池 tryTerminate()
4. RUNNING/SHUTDOWN状态下：保证线程数不低于corePoolSize，不足则创建新线程

## 拒绝策略

| 策略 | 行为 |
|------|------|
| **AbortPolicy**（默认） | 抛出RejectedExecutionException |
| **DiscardPolicy** | 静默丢弃 |
| **DiscardOldestPolicy** | 丢弃队列最早任务，重试添加 |
| **CallerRunsPolicy** | 由调用线程自己执行 |
| 自定义 | 实现RejectedExecutionHandler |

## 相关链接

- [[并发编程]] — 并发编程基础
- [[AQS]] — 抽象队列同步器
- [[CompletableFuture]] — 异步编程利器
- [[CAS]] — CAS原理与应用
