# 资料摘要：Synchronized与锁升级

## 基本概念

synchronized是JVM内置的悲观锁，通过对象头的Mark Word实现锁机制。

## 锁升级过程（不可逆）

### 1. 无锁状态
- 对象头HashCode、GC年龄等状态
- 偏向锁禁用时直接Mark Word保存

### 2. 偏向锁
- 第一次被线程获取时使用
- Mark Word记录线程ID
- 该线程再次进入时无需任何同步开销
- 其他线程尝试竞争时撤销偏向锁

### 3. 轻量级锁
- 锁升级条件：多个线程交替获取锁，但有竞争
- 线程在栈帧建立Lock Record
- Mark Word复制到Lock Record
- CAS更新Mark Word指向Lock Record

### 4. 重量级锁
- 锁升级条件：多个线程同时竞争同一把锁
- 依赖操作系统Mutex实现
- 线程阻塞，不消耗CPU（自旋锁除外）
- Mark Word指向Monitor对象

## 锁膨胀触发条件

| 阶段 | 触发条件 |
|------|----------|
| 无锁→偏向锁 | GC后偏向锁延迟（-XX:+UseBiasedLocking） |
| 偏向锁→轻量级锁 | 偏向锁被其他线程访问 |
| 轻量级锁→重量级锁 | 自旋超过阈值（默认10次） |

## 锁消除

JIT编译器分析发现锁对象只被一个线程访问，消除锁。

## 锁粗化

JIT将多次加锁合并为一次，减少锁操作开销。

## 核心参数

- `-XX:BiasedLockingStartupDelay=0` - 启动时开启偏向锁
- `-XX:+UseBiasedLocking` - 启用偏向锁
- `-XX:PreBlockSpin=10` - 自旋次数

---

**相关主题：** [[并发编程]]、[[CAS]]、[[AQS]]
