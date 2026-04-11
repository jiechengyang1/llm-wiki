---
tags: [concept, jvm]
type: concept
---

# JVM运行时数据区

## 线程私有区域

随线程创建/销毁

### 程序计数器(PC)

- 存储下一条指令地址
- 线程私有，速度最快
- 唯一无OutOfMemoryError区域

### 虚拟机栈

- 方法调用创建栈帧
- 栈帧：局部变量表、操作数栈、动态链接、返回地址
- 异常：StackOverflowError、OutOfMemoryError

### 本地方法栈

- 为native方法服务
- HotSpot与虚拟机栈合一

## 线程共享区域

随JVM启动/销毁

### 堆

- 对象实例存储
- 垃圾回收重点

### 方法区

- 类信息、常量、静态变量
- JDK7：永久代（堆）
- JDK8+：元空间（本地内存）

## 来源

- [[source-jvm-runtime-data-area]]
