---
tags: [concept, java]
type: concept
---

# Java基础概念（上）

## 概述

Java是一门面向对象编程语言，具有功能强大和简单易用的特征。"一次编译，到处运行"。

## JDK/JRE/JVM关系

```
JDK = JRE + 开发工具(javac等)
JRE = JVM + Java类库
JVM = 字节码运行环境
```

## 字节码与执行流程

1. Java源文件(.java) → 编译器 → 字节码文件(.class)
2. JVM加载字节码，解释器逐行解释执行
3. **JIT编译器**：热点代码编译保存机器码，避免重复解释

## 基本数据类型

| 类型 | 字节 | 范围 |
|------|------|------|
| byte | 1 | -128~127 |
| short | 2 | -32768~32767 |
| int | 4 | -2^31~2^31-1 |
| long | 8 | -2^63~2^63-1 |
| float | 4 | IEEE754 |
| double | 8 | IEEE754 |
| char | 2 | Unicode |
| boolean | 1 | true/false |

## 面向对象三大特征

- **封装**：属性私有化，get/set访问
- **继承**：子类拥有父类属性方法（私有不可访问）
- **多态**：编译时多态(重载) + 运行时多态(重写)

## String

- final修饰，不可变
- JDK9后底层用byte[]
- StringBuilder非线程安全，StringBuffer线程安全

## equals vs hashCode

- equals判断对象内容相等
- hashCode确定哈希表索引位置
- 重写equals必须重写hashCode

## 深拷贝 vs 浅拷贝

- 浅拷贝：复制引用地址
- 深拷贝：完全复制对象

## 来源

- [[source-java-basics-1]]
