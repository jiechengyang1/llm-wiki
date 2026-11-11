# 资料摘要：HashMap对比

## HashMap vs Hashtable

| 特性 | HashMap | Hashtable |
|------|---------|-----------|
| 线程安全 | 否 | 是 |
| 性能 | 高 | 低（全局锁） |
| null支持 | key/value都可以 | 都不可以 |
| 迭代器 | fail-fast | fail-safe（枚举器） |
| 初始容量 | 16 | 11 |
| 继承关系 | AbstractMap | Dictionary |
| 扩容策略 | 2倍 | 2倍+1 |

## HashMap vs ConcurrentHashMap

| 特性 | HashMap | ConcurrentHashMap |
|------|---------|-------------------|
| 线程安全 | 否 | 是 |
| 锁机制 | 无 | 分段锁/JDK8红黑树+CAS |
| null支持 | key/value都可以 | 都不可以 |
| 性能（并发） | 低 | 高 |
| 迭代器 | fail-fast | 弱一致 |

## JDK7 vs JDK8 HashMap

**JDK7：数组+链表**
- 头插法（可能环形链表）
- 扩容时重新hash，效率较低

**JDK8：数组+链表+红黑树**
- 尾插法
- 链表长度>8转为红黑树
- 红黑树节点<6退化为链表
- 扩容时高位移动，效率更高

## HashMap数据结构

```
JDK8: 数组(Node[] table) + 链表(拉链法) + 红黑树(树化)
```

```java
// Node结构
static class Node<K,V> implements Map.Entry<K,V> {
    final int hash;
    final K key;
    V value;
    Node<K,V> next;
}
```

## 负载因子

- 默认负载因子：0.75
- 作用：平衡时间和空间
- 扩容阈值 = capacity * loadFactor

## HashMap扩容机制

1. 容量翻倍
2. JDK7：所有节点重新hash
3. JDK8：根据高位bit判断（原位置或原位置+旧容量）

## 为什么链表转红黑树阈值是8？

- 泊松分布计算，链表长度8概率<0.00000006
- 空间和时间的平衡

## ConcurrentHashMap JDK7 vs JDK8

**JDK7：Segment分段锁**
- 16个Segment，每个类似HashMap
- 并发度16

**JDK8：Node数组+CAS+Synchronized**
- 取消分段锁
- 并发度更高
- 锁住单个桶而不是整个map

---

**相关主题：** [[Java集合]]
