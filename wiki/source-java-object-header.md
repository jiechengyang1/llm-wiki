---
tags: [source-summary, java, 并发编程, jvm, 面试]
type: source-summary
source: Java对象内存布局和对象头
date: 2026-06-09
---

# Java对象内存布局与对象头

## 对象在堆内存中的布局

`Object obj = new Object()` → JVM堆 → 新生区 → 伊甸园区

对象存储布局分为三部分：**对象头 + 实例数据 + 对齐填充**

## 对象头（Header）

64位系统中，对象头占16字节（Mark Word 8字节 + 类型指针 8字节）

### 1. 对象标记（Mark Word）

默认存储：**HashCode、分代年龄、锁标志位**等信息

- 非固定数据结构，根据对象状态复用存储空间
- 运行期间数据随锁标志位变化而变化

Mark Word结构（64位）：

| 锁状态 | 存储内容 |
|--------|---------|
| 无锁 | HashCode(31) + 分代年龄(4) + 偏向锁标志(1) + 锁标志位(2) |
| 偏向锁 | 线程ID(54) + Epoch(2) + 分代年龄(4) + 偏向锁标志(1) + 锁标志位(2) |
| 轻量级锁 | 指向栈中锁记录的指针 |
| 重量级锁 | 指向Monitor的指针 |
| GC标记 | 空 |

### 2. 类型指针（Class Pointer）

指向类元数据InstanceKlass，确定对象是哪个类的实例

- 默认开启**压缩指针**：4字节（`-XX:+UseCompressedClassPointers`）
- 关闭压缩指针：8字节（`-XX:-UseCompressedClassPointers`）

## 实例数据（Instance Data）

存放类的属性（Field）数据，包括父类的属性信息

## 对齐填充（Padding）

- 虚拟机要求对象起始地址必须是**8字节的整数倍**
- 非必须，仅为了字节对齐

## new Object()内存占用

- 开启压缩指针：Mark Word(8) + Class Pointer(4) + Padding(4) = **16字节**
- 关闭压缩指针：Mark Word(8) + Class Pointer(8) = **16字节**

## 相关链接

- [[Synchronized与锁升级]] — 对象头中锁标志位的变化
- [[对象实例化与内存布局]] — 对象创建过程与访问定位
- [[java锁]] — 锁分类与实现
- [[AQS]] — 抽象队列同步器
