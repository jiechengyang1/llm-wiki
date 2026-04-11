---
tags: [concept, jvm]
type: concept
---

# JVM堆

## 概述

- JVM进程唯一，线程共享
- 垃圾回收重点区域
- 空间可调节(-Xms/-Xmx)

## 内存结构演变

### Java 7

```
新生区(Eden+S0+S1) + 老年区 + 永久区
```

### Java 8+

```
新生区(Eden+S0+S1) + 老年区 + 元空间
```

**重要变化**：永久代→元空间，位置从堆内存移到本地内存

## 对象分配流程

1. Eden创建对象
2. Minor GC后存活→Survivor0
3. 再次Minor GC→Survivor1
4. 年龄达阈值(默认15)→老年代
5. 老年代满→Major GC/Full GC→OOM

## 垃圾回收类型

| 类型 | 区域 | 频率 |
|------|------|------|
| Minor GC | 新生代 | 高 |
| Major GC | 老年代 | 低 |
| Full GC | 整个堆 | 尽量避免 |

## 逃逸分析优化

- **栈上分配**：对象不逃逸可在栈上分配
- **同步省略**：单线程访问对象可取消同步
- **标量替换**：对象可拆解为标量在栈上分配

## TLAB

- Thread Local Allocation Buffer
- Eden中为每个线程分配私有缓存
- 避免并发分配冲突

## 来源

- [[source-jvm-heap]]
