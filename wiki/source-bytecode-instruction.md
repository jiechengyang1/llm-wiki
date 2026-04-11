# 资料摘要：字节码指令集

## 指令分类（9类）

1. 加载与存储指令
2. 算术指令
3. 类型转换指令
4. 对象的创建与访问指令
5. 方法调用与返回指令
6. 操作数栈管理指令
7. 比较控制指令
8. 异常处理指令
9. 同步控制指令

## 加载与存储指令

**局部变量压栈：** iload, lload, fload, dload, aload
**常量入栈：** iconst, bipush, sipush, ldc
**出栈装入局部变量：** istore, lstore, fstore, dstore, astore

## 算术指令

**整数运算：** iadd, isub, imul, idiv, irem, ineg, iinc
**逻辑运算：** iand, ior, ixor
**移位操作：** ishl, ishr, iushr

## 类型转换指令

**宽化类型：** int→long→float→double（无精度损失）
**窄化类型：** 可能溢出或丢失精度

## 对象创建与访问

**创建：** new
**字段访问：** getfield, putfield, getstatic, putstatic
**数组：** newarray, anewarray, multianewarray
**类型检查：** instanceof, checkcast

## 方法调用指令

| 指令 | 用途 |
|------|------|
| invokevirtual | 调用实例方法（多态） |
| invokeinterface | 调用接口方法 |
| invokespecial | 调用私有/构造器/父类方法 |
| invokestatic | 调用静态方法 |
| invokedynamic | 动态方法调用 |

## 同步控制

**方法级同步：** ACC_SYNCHRONIZED标志
**代码块同步：** monitorenter / monitorexit

## 操作数栈指令

- pop / pop2：弹出废弃
- dup / dup2：复制栈顶
- swap：交换栈顶两项

## 异常处理

- athrow：抛出异常
- 异常表：try-catch-finally实现

---

**相关主题：** [[Class文件结构]]
