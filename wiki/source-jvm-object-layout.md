---
tags: [source-summary, java, jvm, 面试]
type: source-summary
source: 对象的实例化内存布局和访问定位
date: 2026-06-09
---

# 对象实例化与内存布局

## 创建对象的方式

1. **new**：最常见
2. **Class.newInstance()**：反射，只能调空参public构造器
3. **Constructor.newInstance()**：反射，可调任意构造器
4. **clone()**：不调用构造器，需实现Cloneable
5. **序列化**：从文件/网络获取二进制流
6. **Objenesis**：第三方库

## 创建对象的步骤

1. **判断类是否加载** → 检查Metaspace常量池中的符号引用
2. **为对象分配内存** → 计算大小，在堆中划分空间
3. **处理并发问题** → CAS失败重试 或 TLAB
4. **初始化默认值** → 零值初始化
5. **设置对象头** → 元数据、HashCode、GC信息、锁信息
6. **执行init方法** → 显式初始化 → 代码块初始化 → 构造器初始化

### 内存分配方式

| 堆内存状态 | 分配方式 | 对应GC |
|-----------|---------|--------|
| 规整 | **指针碰撞法**（Bump The Point） | Serial, ParNew（压缩算法） |
| 不规整 | **空闲列表**（Free List） | 无压缩的GC |

## 对象内存布局

### 1. 对象头

**运行时元数据（Mark Word）**：
- HashCode、GC分代年龄、锁状态标志、线程持有的锁、偏向线程ID、偏向时间戳

**类型指针**：指向类元数据InstanceKlass，确定对象所属类型

> 数组对象还需记录数组长度

### 2. 实例数据（Instance Data）

- 对象真正存储的有效信息（含父类继承字段）
- 相同宽度字段分配在一起
- 父类变量出现在子类之前
- CompactFields=true时，子类窄变量可插入父类变量空隙

### 3. 对齐填充（Padding）

- 非必须，仅起占位符作用

## 对象访问定位

### 句柄访问

- reference → 句柄池 →（实例数据指针 + 类型数据指针）
- **优点**：对象移动时只改句柄池指针，reference不变
- **缺点**：两次指针访问

### 直接指针（HotSpot采用）

- reference → 堆中对象实例 → 类型指针 → 方法区类型数据
- **优点**：一次堆访问，速度快
- **缺点**：对象移动时reference需修改

## 直接内存（Direct Memory）

- 非JVM规范定义的内存区域，堆外直接向系统申请
- 来源于NIO，通过DirectByteBuffer操作Native内存
- 读写性能优于Java堆
- 大小通过 `MaxDirectMemorySize` 设置，默认与-Xmx一致
- **可能导致OutOfMemoryError: Direct buffer memory**

## 相关链接

- [[JVM堆]] — 堆内存结构
- [[JVM运行时数据区]] — 内存区域划分
- [[Synchronized与锁升级]] — 对象头中的锁信息
- [[java锁]] — 锁分类与实现
