---
tags: [source-summary, java, 面试]
type: source-summary
source: JAVA基础-上
date: 2025-06-23
---

# JAVA基础-上

## 核心要点

### Java概述
- Java是面向对象的编程语言，吸收了C++优点，摒弃了多继承、指针等概念
- **JVM是核心**：一次编译，到处运行
- JDK = JRE + 编译器(javac)等开发工具；JRE = JVM + Java类库

### 字节码与执行
- Java源文件(.java) → 编译器 → 字节码文件(.class) → JVM执行
- JVM类加载器加载字节码，解释器逐行解释执行
- **JIT编译器**：热点代码会触发JIT编译，保存机器码，下次直接使用
- Java = 编译 + 解释共存的语言

### 基本数据类型
- 8种：byte/short/int/long(整数)，float/double(浮点)，char(字符)，boolean(布尔)
- **基本类型 vs 包装类型**：
  - 基本类型栈中，包装类型堆中
  - 包装类型有缓存机制(Integer [-128,127])
  - 泛型只能用包装类型
  - == 比较：基本类型比值，包装类型比地址

### 面向对象三大特征
- **封装**：属性私有化，提供get/set
- **继承**：子类拥有父类所有属性方法（私有不可访问），可扩展
- **多态**：编译时多态(重载) + 运行时多态(重写)

### String
- **不可变性**：final修饰char数组，类也被final修饰
- JDK9后使用byte数组存储
- **StringBuffer vs StringBuilder**：前者线程安全，后者非线程安全
- 字符串拼接：JDK8用StringBuilder，JDK9用动态方法

### equals vs ==
- ==：基本类型比值，引用类型比地址
- equals()：未重写时等价==，String等重写后比较值

### hashCode
- 与equals配合用于HashMap/HashSet高效查找
- 重写equals必须重写hashCode

### 深拷贝 vs 浅拷贝
- 浅拷贝：复制引用地址
- 深拷贝：完全复制对象
- 实现：Cloneable接口、序列化、手动递归

### 语法糖
- 泛型、自动拆装箱、变长参数、枚举、内部类、增强for、try-with-resources、Lambda
- JVM不支持语法糖，编译阶段解糖

## 相关概念

- [[java-basic-2]] - JAVA基础下（异常、泛型、反射）
- [[java-io]] - JAVA IO
- [[java-new-features]] - Java新特性
- [[jvm-heap]] - JVM堆
- [[jvm-runtime-data-area]] - JVM运行时数据区
