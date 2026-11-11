# 资料摘要：类的加载过程（类的生命周期）

## 类的生命周期阶段

```
加载(Loading) → 链接(Linking) → 初始化(Initialization) → 使用(Using) → 卸载(Unloading)
```

链接分为三个环节：验证(Verification) → 准备(Preparation) → 解析(Resolution)

## 加载阶段（Loading）

完成三件事：
1. 通过类的全限定名获取类的二进制数据流
2. 解析为方法区内的数据结构
3. 创建java.lang.Class实例作为访问入口

## 链接阶段

### 验证（Verification）
- 文件格式验证
- 语义检查
- 字节码验证
- 符号引用验证

### 准备（Preparation）
- 为静态变量分配内存
- 设置默认初始值（0、false、null等）

### 解析（Resolution）
- 符号引用转为直接引用
- 类、接口、字段、方法的引用解析

## 初始化阶段

**static final基本类型/String字面量**：在准备阶段显式赋值
**普通static变量**：在初始化阶段(<clinit>)赋值

**主动使用会触发初始化：**
- new创建实例
- 调用静态方法
- 访问静态字段
- 反射Class.forName()
- 初始化子类时先初始化父类
- main方法所在类

**被动使用不触发初始化：**
- 子类访问父类静态字段
- 数组定义
- 引用常量（final）
- ClassLoader.loadClass()

## 类加载器分类

| 加载器 | 作用 | 特点 |
|--------|------|------|
| Bootstrap ClassLoader | 加载核心库 | C/C++实现 |
| Extension ClassLoader | 加载扩展类 | sun.misc.Launcher$ExtClassLoader |
| AppClassLoader | 加载应用类 | sun.misc.Launcher$AppClassLoader |

## 双亲委派模型

加载请求向上委托父类处理，只有父类无法完成时才由子类处理。

**优势：**
- 避免类重复加载
- 保护核心API不被篡改

**三次破坏：**
1. JDK1.2之前用户自定义loadClass
2. 线程上下文类加载器（JNDI、JDBC等SPI）
3. OSGi模块化热部署

## 类的卸载

满足三个条件才能卸载：
1. 所有实例已回收
2. 类加载器已被回收
3. Class对象无引用

启动类加载器加载的类不会被卸载。

---

**相关主题：** [[类加载器]]、[[Class文件结构]]、[[字节码指令集]]
