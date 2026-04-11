# 资料摘要：Class文件结构

## 文件格式

```
Class文件 = 魔数(magic) + 版本号 + 常量池 + 访问标志 + 类索引 + 父类索引 + 接口集合 + 字段表 + 方法表 + 属性表
```

## 魔数

- 固定值：0xCAFEBABE
- 用于识别是否为有效的Class文件

## 版本号

| 主版本 | Java版本 |
|--------|----------|
| 50 | JDK1.8 |
| 52 | JDK1.8 |
| 54 | JDK10 |

高版本JVM可执行低版本编译器生成的Class文件，反之不行。

## 常量池

存放两大类常量：
- **字面量**：文本字符串、final常量值
- **符号引用**：类/接口名、字段名、方法名、描述符

常量类型（14种）：CONSTANT_Utf8、CONSTANT_Integer、CONSTANT_Class、CONSTANT_Fieldref等。

## 访问标志

| 标志 | 含义 |
|------|------|
| ACC_PUBLIC | public |
| ACC_FINAL | final |
| ACC_SUPER | invokespecial语义 |
| ACC_INTERFACE | 接口 |
| ACC_ABSTRACT | abstract |

## 类索引/父类索引

- this_class：指向常量池中的CONSTANT_Class_info
- super_class：父类索引（Object为0）

## 字段表结构

```
access_flags + name_index + descriptor_index + attributes
```

描述符规则：
- B=byte, C=char, D=double, F=float
- I=int, J=long, S=short, Z=boolean
- L+全限定名=对象类型
- [=数组类型

## 方法表结构

同字段表结构，包含继承自父类的方法（不包括private）。

## 属性表

Code属性：存储方法的字节码指令。

---

**相关主题：** [[字节码指令集]]
