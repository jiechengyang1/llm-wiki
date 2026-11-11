---
tags: [source-summary, java, 面试]
type: source-summary
source: JAVA基础-下
date: 2024-09-24
---

# JAVA基础-下

## 核心要点

### 异常
- **Exception vs Error**：Exception可处理，Error无法处理
- **Checked vs Unchecked**：Checked需编译时处理(IOException)，Unchecked运行时处理(RuntimeException)
- try-catch-finally：finally总会执行（除System.exit()）
- try-with-resources：自动关闭资源

### 泛型
- 编译时类型检查，运行时类型擦除
- 三种使用：泛型类、泛型接口、泛型方法
- `<T>`擦除后用最左边界类型替换

### 反射
- 运行时获取类的内部信息
- Class对象只由系统建立，一个类只有一个Class实例
- 获取方式：.class、forName()、getClass()

### 注解
- 元数据，供程序编译或运行时使用
- 本质：继承了Annotation的动态代理类
- 解析方式：编译期扫描、运行期反射

### SPI (Service Provider Interface)
- 服务提供者接口，将接口和实现分离
- JDK SPI：ServiceLoader.load()
- 典型应用：数据库驱动、Spring、Dubbo扩展

### 序列化
- 对象 → 二进制字节流
- transient修饰的变量不序列化
- 常用协议：Hessian、Kryo、Protobuf

### 语法糖（详见[[JAVA基础-上]]）
- switch支持String：基于hashCode和equals
- 泛型类型擦除
- 自动装箱/拆箱
- 枚举：编译后继承Enum
- Lambda：依赖底层API，编译后只有一个class文件

### Unsafe类
- 位于sun.misc包，提供底层操作
- 功能：内存操作、CAS、线程调度、Class操作
- 无法直接调用，通过反射获取theUnsafe实例
- 典型应用：JUC并发工具、DirectByteBuffer

## 相关概念

- [[JAVA基础-上]] - JAVA基础上
- [[JAVA-IO]] - JAVA IO
- [[JAVA新特性]] - Java新特性
