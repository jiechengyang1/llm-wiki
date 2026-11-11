---
tags: [source-summary, java, 面试, IO]
type: source-summary
source: JAVA-IO
date: 2024-10-08
---

# JAVA-IO

## 核心要点

### IO分类
- **输入流/输出流**：数据流入/流出内存
- **字节流/字符流**：字节流处理二进制，字符流处理字符
- 四基类：InputStream/OutputStream/Reader/Writer

### 字节流
- InputStream：read()返回0-255，-1表示结束
- OutputStream：write(int b)
- FileInputStream/FileOutputStream：文件操作
- BufferedInputStream/BufferedOutputStream：缓冲流，减少IO次数

### 字符流
- 解决字节流乱码问题
- Reader/Writer：读取字符
- InputStreamReader/OutputStreamWriter：字节流↔字符流桥梁

### BIO/NIO/AIO
- **BIO**：同步阻塞，线程等待
- **NIO**：同步非阻塞，Selector多路复用
- **AIO**：异步IO，基于事件回调

### NIO核心组件
- **Buffer**：缓冲区，flip()切换读写模式
- **Channel**：双向通道，FileChannel/SocketChannel
- **Selector**：多路复用器，监控多个Channel事件

### 装饰器模式
- FilterInputStream/FilterOutputStream增强功能
- BufferedInputStream增强FileInputStream
- 可多层嵌套

### 适配器模式
- InputStreamReader：字节流→字符流
- StreamDecoder/StreamEncoder编解码

### 零拷贝
- **mmap**：FileChannel.map()映射到内存
- **sendfile**：FileChannel.transferTo()
- 减少CPU拷贝和上下文切换

### Reactor线程模型
- 事件驱动分发
- 连接和业务线程分离
- 避免业务线程阻塞

## 相关概念

- [[JAVA基础-上]] - JAVA基础上
- [[JAVA基础-下]] - JAVA基础下
- [[JAVA新特性]] - Java新特性
