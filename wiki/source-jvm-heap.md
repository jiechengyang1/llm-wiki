---
tags: [source-summary, java, jvm, 面试]
type: source-summary
source: JVM堆
date: 2024-09-19
---

# JVM堆

## 核心概述

- 堆针对一个JVM进程唯一，线程共享
- JVM启动时创建，空间可调节
- 物理上不连续，逻辑上连续
- GC重点区域

## 堆内存结构

### Java 7及之前
- 新生区(Eden + Survivor0/1) + 老年区 + 永久区

### Java 8及之后
- 新生区 + 老年区 + 元空间
- **元空间位于本地内存，非堆**

## 年轻代GC流程

1. 对象在Eden创建
2. Eden满触发Minor GC，存活对象→Survivor0
3. 再次Minor GC，Survivor0存活→Survivor1
4. 年龄达阈值(默认15)→老年代
5. 老年代满→Major GC/Full GC→OOM

## 垃圾回收类型

- **Minor GC**：新生代，频繁，快
- **Major GC**：老年代，慢，Full GC的一种
- **Full GC**：整个堆+方法区，尽量避免

## 内存分配策略

- 优先分配到Eden
- 大对象直接老年代
- 长期存活对象老年代
- 动态年龄判断

## TLAB

- Thread Local Allocation Buffer
- Eden空间中为每个线程分配私有缓存
- 避免并发分配内存冲突
- -XX:UseTLAB开启

## 堆外内存与逃逸分析

- **栈上分配**：逃逸分析发现对象不逃逸，可在栈上分配
- **同步省略**：只有一个线程访问的对象，同步可省略
- **标量替换**：对象不逃逸可拆解为标量分配

## 相关概念

- [[jvm-runtime-data-area]] - JVM运行时数据区
- [[java-basic-1]] - JAVA基础上
