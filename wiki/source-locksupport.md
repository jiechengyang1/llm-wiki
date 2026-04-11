# 资料摘要：LockSupport与线程中断

## 线程中断机制

**三个方法：**
- `interrupt()` - 设置中断标志为true（协商机制，不立刻停止）
- `isInterrupted()` - 判断是否被中断（不清除标志）
- `interrupted()` - 静态方法，判断并清除中断标志

**中断只是协商机制，需要线程配合检测标志位才能真正停止。**

## 停止线程的方式

1. **volatile变量**：通过标志位协调
2. **AtomicBoolean**：原子性标志位
3. **interrupt() + isInterrupted()**：线程内检测

## 阻塞状态中断

线程处于sleep/wait/join时：
- 调用interrupt()会立即抛出InterruptedException
- 中断标志被清除

## LockSupport

**核心原语：park()和unpark()**

- `park()` - 阻塞当前线程
- `unpark(thread)` - 唤醒指定线程

**Permit机制：**
- 每个线程有一个permit（最多1个）
- unpark增加permit，park消耗permit
- 可以先unpark再park（突破wait/notify顺序限制）

## 三种等待唤醒对比

| 方式 | 阻塞位置 | 唤醒限制 |
|------|----------|----------|
| Object.wait/notify | 同步块内 | 先wait后notify |
| Condition.await/signal | 锁内 | 先await后signal |
| LockSupport.park/unpark | 任意位置 | 无顺序要求 |

---

**相关主题：** [[并发编程]] [[java锁]]
