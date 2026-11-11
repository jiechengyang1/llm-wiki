---
tags: [source-summary, java, 并发编程, 面试]
type: source-summary
source: CompletableFuture
date: 2026-06-09
---

# CompletableFuture

## Future接口的局限性

Future定义了异步任务操作方法：获取结果、取消任务、判断状态等。

**优点**：Future+线程池显著提高运行效率

**缺点**：
- **get()阻塞** — 必须等到结果才能继续
- **isDone()轮询** — 浪费CPU资源，代码不优雅

> 真正的异步应通过**回调函数**，任务完成时自动通知

## CompletableFuture改进

JDK8设计，提供观察者模式机制：任务完成后自动通知监听方。

### 核心接口

- **CompletionStage**：代表异步计算的某个阶段，一个阶段完成后可触发另一个阶段
- **CompletableFuture**：实现Future + CompletionStage，支持回调、转换、组合

### 创建异步任务的4个静态方法

| 方法 | 有返回值 | 线程池 |
|------|---------|--------|
| `runAsync(Runnable)` | 无 | 默认ForkJoinPool |
| `runAsync(Runnable, Executor)` | 无 | 自定义线程池 |
| `supplyAsync(Supplier)` | 有 | 默认ForkJoinPool |
| `supplyAsync(Supplier, Executor)` | 有 | 自定义线程池 |

### 回调机制

```java
CompletableFuture.supplyAsync(() -> {
    return result;
}, executorService)
.whenComplete((v, e) -> {  // 完成时回调
    if (e == null) System.out.println(v);
})
.exceptionally(e -> {      // 异常时回调
    e.printStackTrace();
    return null;
});
```

> 优点：异步任务完成/出错时自动回调，主线程无需阻塞或轮询

## 常用方法

### 获得结果和触发计算

| 方法 | 说明 |
|------|------|
| `get()` | 阻塞等待结果 |
| `get(timeout, unit)` | 超时等待 |
| `join()` | 同get，不抛受检异常 |
| `getNow(valueIfAbsent)` | 立即获取，未完成返回备胎值 |
| `complete(value)` | 主动打断，立即返回指定值 |

### 对计算结果进行处理

| 方法 | 异常时 | 说明 |
|------|--------|------|
| `thenApply` | 停止，不执行下一步 | 串行化，有依赖 |
| `handle` | 继续执行 | 串行化，带异常处理 |

### 对计算结果进行消费

| 方法 | 需要A的结果 | B有返回值 |
|------|-----------|----------|
| `thenRun` | 不需要 | 无 |
| `thenAccept` | 需要 | 无 |
| `thenApply` | 需要 | 有 |

### 对计算速度选用

- `applyToEither` — 谁快用谁

### 对计算结果合并

- `thenCombine` — 两个任务都完成后合并结果，先完成的等另一个

### 线程池说明

- 未指定线程池 → 默认ForkJoinPool
- `thenRun/thenAccept/thenApply` → 复用上一个任务的线程池
- `thenRunAsync/thenAcceptAsync/thenApplyAsync` → 使用ForkJoinPool

## 电商比价案例

- 串行查价：~3000ms
- CompletableFuture并行查价：~1000ms（3倍提升）

```java
list.stream()
    .map(mall -> CompletableFuture.supplyAsync(
        () -> getPrice(mall), executor))
    .collect(Collectors.toList())
    .stream()
    .map(CompletableFuture::join)
    .collect(Collectors.toList());
```

## 相关链接

- [[并发编程]] — 并发编程基础
- [[AQS]] — 抽象队列同步器
- [[CAS]] — CAS原理
