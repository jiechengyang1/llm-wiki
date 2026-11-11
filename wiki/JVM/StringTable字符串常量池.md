---
tags: [source-summary, java, jvm, 面试]
type: source-summary
source: StringTable字符串常量池
date: 2026-06-09
---

# StringTable字符串常量池

## String基本特性

- **final类**，不可继承；内部`byte[] value`（JDK9+）也用final修饰
- 实现Serializable、Comparable接口
- **JDK9存储变更**：`char[]` → `byte[] + 编码标记`，节约空间
  - Latin-1字符：1字节/字符
  - UTF-16字符：2字节/字符

### 不可变性

1. 重新赋值 → 重写指定内存区域
2. 字符串连接 → 重新指定内存区域
3. replace() → 重新指定内存区域

> 字面量方式赋值的字符串声明在**字符串常量池**中，常量池不存相同内容

## StringTable（字符串常量池）

- 固定大小Hashtable，默认长度：
  - JDK6: 1009
  - JDK7: 60013
  - JDK8+: 最小1009
- `-XX:StringTableSize` 设置长度
- Hash冲突严重 → 链表长 → intern性能下降

### 常量池位置变迁

| JDK版本 | 字符串常量池位置 |
|---------|----------------|
| JDK6及以前 | 永久代 |
| JDK7 | **Java堆** |
| JDK8+ | 堆（元空间为方法区，串池仍在堆） |

> 调整原因：永久代空间有限，大量使用intern()容易OOM

## 字符串拼接操作

| 拼接方式 | 结果位置 | 原理 |
|---------|---------|------|
| 常量+常量 | 常量池 | 编译期优化 |
| 含变量 | **堆** | 底层new StringBuilder |
| final修饰的变量 | 常量池 | 编译期可确定 |
| 拼接后调intern() | 常量池 | 主动入池 |

> 变量拼接底层：`new StringBuilder().append().append().toString()`

### 性能对比（5万次循环）

| 方式 | 耗时 |
|------|------|
| String + | 7963ms |
| StringBuilder.append | 1ms |
| StringBuffer.append | 4ms |

> 实际开发中优先使用StringBuilder，预估容量指定capacity减少扩容

## intern()方法 ⭐⭐⭐⭐

- native方法，将字符串尝试放入常量池
- 池中已有 → 返回池中对象
- 池中没有 → 入池并返回

### JDK6 vs JDK7/8 区别

| 版本 | 池中不存在时的行为 |
|------|-------------------|
| JDK6 | **复制对象**入池，返回池中对象地址 |
| JDK7/8 | **复制引用地址**入池，返回池中引用地址 |

### 经典面试题

```java
String s = new String("1");
s.intern();
String s2 = "1";
s == s2  // JDK6: false  JDK7/8: false

String s3 = new String("1") + new String("1");
s3.intern();
String s4 = "11";
s3 == s4  // JDK6: false  JDK7/8: true ← 引用入池
```

### intern效率

- 大量重复字符串时使用intern()可显著**节省内存**
- 测试：千万级字符串，使用intern耗时1395ms vs 不使用7256ms

## StringTable的垃圾回收

- StringTable也会被GC回收
- 常量池中的字符串无引用时可被回收

## G1中的String去重

- 堆存活数据中String占25%，其中重复的占13.5%
- G1实现自动String去重（非常量池中的重复）

```bash
-XX:+UseStringDeduplication        # 开启String去重
-XX:+PrintStringDeduplicationStatistics  # 打印去重统计
-XX:StringDeduplicationAgeThreshold=nnn  # 去重候选年龄
```

去重流程：GC访问对象 → 检查是否候选String → 入队列 → 后台线程查hashtable去重

## 相关链接

- [[JVM堆]] — 字符串常量池在堆中
- [[JVM运行时数据区]] — 内存区域划分
- [[方法区]] — 运行时常量池
- [[垃圾回收概述]] — GC与StringTable回收
