# 资料摘要：volatile与JMM

## 两大特性

### 可见性
- 写操作：立即刷新到主内存
- 读操作：从主内存读取最新值

### 有序性（禁重排）
- 通过内存屏障实现
- 防止指令重排序

## 内存屏障

**四种屏障：**
- LoadLoad - 读之后禁止重排
- StoreStore - 写之后禁止重排
- LoadStore - 读后写禁止重排
- StoreLoad - 写后读禁止重排（最重量级）

## Happens-Before volatile规则

- volatile写happens-before volatile读
- 写前操作不能重排到写后
- 读后操作不能重排到读前

## 三大特性对比

| 特性 | volatile | synchronized |
|------|----------|--------------|
| 可见性 | 保证 | 保证 |
| 有序性 | 保证 | 保证 |
| 原子性 | 不保证 | 保证 |

## 不保证原子性

`i++`这类复合操作不保证原子性：
1. 读取i值
2. +1计算
3. 写回i

多线程下会有线程安全问题了。

**适用场景：**
- 单一赋值可以（flag = true）
- 状态标志
- DCL单例

## 内存屏障实现原理

JVM在字节码中插入内存屏障指令：
- 写前插入StoreStore屏障
- 写后插入StoreLoad屏障
- 读后插入LoadLoad+LoadStore屏障

---

**相关主题：** [[Java内存模型之JMM]] [[CAS]]
