---
tags: [concept, java, io]
type: concept
---

# Java IO

## IO分类

```
输入流/输出流：数据流入/流出内存
字节流/字符流：处理二进制/字符数据
```

四基类：InputStream、OutputStream、Reader、Writer

## BIO/NIO/AIO

| 模型 | 特点 | 线程 |
|------|------|------|
| BIO | 同步阻塞 | 等待 |
| NIO | 同步非阻塞，Selector多路复用 | 单线程处理多连接 |
| AIO | 异步IO，基于事件回调 | 不等待 |

## NIO三大组件

### Buffer

- flip()切换读写模式
- clear()清空缓冲区
- 常用：ByteBuffer、CharBuffer

### Channel

- 双向通道
- FileChannel、SocketChannel、DatagramChannel

### Selector

- 多路复用器
- 监控OP_ACCEPT/OP_CONNECT/OP_READ/OP_WRITE事件

## 设计模式

### 装饰器模式

- FilterInputStream增强InputStream
- BufferedInputStream/DataInputStream

### 适配器模式

- InputStreamReader：字节→字符
- StreamDecoder/StreamEncoder

## 零拷贝

- mmap：FileChannel.map()
- sendfile：FileChannel.transferTo()
- 减少CPU拷贝和上下文切换

## Reactor模型

- 事件驱动分发
- 连接和业务分离
- 单线程处理多连接

## 来源

- [[source-java-io]]
