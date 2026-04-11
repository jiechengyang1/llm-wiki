---
tags: [concept, java]
type: concept
---

# Java基础概念（下）

## 异常处理

### Exception vs Error

- **Exception**：程序可处理
  - Checked Exception：编译时检查(IOException)
  - Unchecked Exception：运行时检查(RuntimeException)
- **Error**：系统错误，无法处理(JVM内存溢出等)

### try-catch-finally

- finally总会执行（除System.exit()）
- try-with-resources自动关闭资源

## 泛型

- 编译时类型检查，运行时类型擦除
- 泛型类/接口/方法
- 擦除后用最左边界类型替换

## 反射

- 运行时获取类内部信息
- Class对象一个类只有一个
- 场景：Spring DI、MyBatis、序列化

## 注解

- 元数据，修饰类/方法/字段
- 编译期扫描 or 运行期反射解析

## SPI

- Service Provider Interface
- 将接口与实现分离
- 场景：JDBC驱动、Spring框架、Dubbo扩展

## 序列化

- 对象→二进制字节流
- transient变量不序列化
- 常用协议：Hessian、Kryo、Protobuf

## Unsafe

- sun.misc包，底层操作
- 功能：内存操作、CAS、线程调度、Class操作
- JUC并发工具底层依赖

## 来源

- [[source-java-basics-2]]
