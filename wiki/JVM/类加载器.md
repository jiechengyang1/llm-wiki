# 资料摘要：再谈类的加载器

## 类加载器分类

**三层类加载器：**
- Bootstrap ClassLoader（C/C++，加载核心库）
- Extension ClassLoader（加载扩展类）
- AppClassLoader（加载应用类）

## ClassLoader核心方法

| 方法 | 作用 |
|------|------|
| loadClass() | 加载类，双亲委派实现 |
| findClass() | 自定义类加载逻辑 |
| defineClass() | 将字节数组转为Class对象 |

## 双亲委派模型

**加载顺序：**
1. 检查缓存
2. 委托父类加载器
3. 父类为null则用Bootstrap
4. 父类加载失败则调用findClass()

**优势：**
- 避免类重复加载
- 保证类全局唯一性
- 保护核心API安全

## 类的显式加载vs隐式加载

- **显式加载**：Class.forName()、loadClass()
- **隐式加载**：new、引用类时自动加载

## Class.forName() vs ClassLoader.loadClass()

| 方法 | 初始化 |
|------|--------|
| Class.forName() | 执行类初始化 |
| ClassLoader.loadClass() | 不执行初始化 |

## 线程上下文类加载器

解决父加载器需要访问子加载器加载类的场景（SPI机制）。

JNDI、JDBC、JCE等使用此机制。

## 破坏双亲委派

1. **JDK1.2之前**：自定义loadClass()
2. **SPI机制**：线程上下文类加载器
3. **OSGi**：网状结构类加载器

## 自定义类加载器

**场景：**
- 隔离加载类（容器、中间件）
- 修改类加载方式
- 扩展加载源（数据库、网络）
- 防止源码泄漏

**实现方式：**
- 重写loadClass()（不推荐）
- 重写findClass()（推荐）

---

**相关主题：** [[类的加载过程]]
