# 资料摘要：原子操作类

## 基本类型原子类

- AtomicInteger
- AtomicLong
- AtomicBoolean

**常用API：**
- get() - 获取值
- getAndIncrement() - 先获取后自增
- compareAndSet(expect, update) - CAS操作
- lazySet() - 延迟设置（性能优化）

## 数组类型原子类

- AtomicIntegerArray
- AtomicLongArray
- AtomicReferenceArray

## 引用类型原子类

- AtomicReference - 普通引用
- AtomicStampedReference - 带版本号（解决ABA问题）
- AtomicMarkableReference - 带标记（一次性）

## 对象属性修改原子类

- AtomicIntegerFieldUpdater
- AtomicLongFieldUpdater
- AtomicReferenceFieldUpdater

**要求：字段必须public volatile修饰**

## 增强类

- LongAdder - 高并发下long累加（分散热点）
- LongAccumulator - 自定义运算
- DoubleAdder / DoubleAccumulator

## LongAdder vs AtomicLong

| 场景 | LongAdder | AtomicLong |
|------|-----------|------------|
| 低并发 | 差不多 | 差不多 |
| 高并发 | 快（分散热点） | 慢（自旋严重） |
| 精度 | 最终一致 | 强一致 |
| sum() | 可能有误差 | 精确 |

**LongAdder原理：**
- base变量：低并发时使用
- Cell数组：高并发时分散到不同槽位
- sum()累加所有Cell+base

---

**相关主题：** [[CAS]]
