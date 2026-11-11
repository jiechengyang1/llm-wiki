---
tags: [source-summary, java, jvm, 面试]
type: source-summary
source: JVM运行时数据区和PC
date: 2024-06-20
---

# JVM运行时数据区和程序计数器

## 运行时数据区

### 线程私有（随线程创建/销毁）
- **程序计数器(PC)**：存储下一条指令地址
- **虚拟机栈**：方法调用，栈帧结构
- **本地方法栈**：native方法

### 线程共享（随JVM启动/销毁）
- **堆**：对象实例
- **方法区**：类信息、运行时常量池

## 程序计数器

- 小的内存空间，速度最快
- 线程私有，生命周期与线程一致
- 存储当前执行的Java方法地址，或native方法undefined
- 唯一没有OutOfMemoryError的区域

## 虚拟机栈

- 线程执行方法创建栈帧
- 栈帧包含：局部变量表、操作数栈、动态链接、方法返回地址
- 两种异常：StackOverflowError(栈溢出)、OutOfMemoryError

## 本地方法栈

- 为native方法服务
- HotSpot将本地方法栈和虚拟机栈合一

## 相关概念

- [[JVM堆]] - JVM堆
- [[JAVA基础-上]] - JAVA基础上
