# 资料摘要：Java集合

## 集合框架体系

```
Collection
├── List（有序、可重复）
│   ├── ArrayList
│   ├── LinkedList
│   ├── Vector
│   └── Stack
├── Set（无序、不可重复）
│   ├── HashSet
│   ├── TreeSet
│   ├── LinkedHashSet
│   └── EnumSet
└── Queue（队列）
    ├── LinkedList
    ├── PriorityQueue
    ├── Deque
    └── BlockingQueue

Map（键值对）
├── HashMap
├── TreeMap
├── LinkedHashMap
├── Hashtable
├── ConcurrentHashMap
└── WeakHashMap
```

## List实现对比

| 实现 | 线程安全 | 底层结构 | 适用场景 |
|------|----------|----------|----------|
| ArrayList | 否 | 数组 | 随机访问、尾插 |
| LinkedList | 否 | 双向链表 | 频繁插入删除 |
| Vector | 是 | 数组 | 已废弃 |
| CopyOnWriteArrayList | 是 | 数组 | 读多写少 |

## Set实现对比

| 实现 | 线程安全 | 底层结构 | 排序 |
|------|----------|----------|------|
| HashSet | 否 | HashMap | 无序 |
| LinkedHashSet | 否 | LinkedHashMap | 插入顺序 |
| TreeSet | 否 | TreeMap | 自然顺序 |
| ConcurrentHashMap | 是 | 数组+链表/红黑树 | 无序 |

## Map实现对比

| 实现 | 线程安全 | 底层结构 | 特点 |
|------|----------|----------|------|
| HashMap | 否 | 数组+链表+红黑树 | 高性能 |
| LinkedHashMap | 否 | HashMap+双向链表 | 保持插入顺序 |
| TreeMap | 否 | 红黑树 | 自然排序 |
| Hashtable | 是 | 数组+链表 | 已废弃 |
| ConcurrentHashMap | 是 | 数组+链表+红黑树 | 高并发首选 |
| ConcurrentSkipListMap | 是 | 跳表 | 有序高并发 |

## 迭代器fail-fast机制

modCount记录修改次数，迭代时检查modCount是否改变，改变则抛出ConcurrentModificationException。

## 线程安全集合

- **synchronized开头**：synchronizedList、synchronizedMap等（全局锁）
- **concurrent包**：ConcurrentHashMap、CopyOnWriteArrayList等（分段锁/无锁）
- **queue包**：BlockingQueue实现生产消费者模式

## 常用集合选择

**单线程环境：**
- 随机访问：ArrayList
- 频繁插入删除：LinkedList
- 键值对：HashMap
- 需要排序：TreeMap
- 需要保持顺序：LinkedHashMap

**多线程环境：**
- 高并发Map：ConcurrentHashMap
- 高并发List：CopyOnWriteArrayList
- 高并发Set：CopyOnWriteArraySet或ConcurrentHashMap.newKeySet()
- 生产消费：BlockingQueue

---

**相关主题：** [[HashMap对比]]
