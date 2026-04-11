# TCP 三次握手与四次挥手

## 基础

TCP 是面向连接的可靠传输协议，三次握手建立连接，四次挥手断开连接。

## 核心

### TCP 报文

- **序列号**：解决网络包乱序问题
- **确认应答号**：期望收到的下一序列号，解决丢包问题
- **控制位**：ACK（确认应答）、RST（异常强制断开）、SYN（建立连接）、FIN（断开连接）

### TCP vs UDP

| 特性 | TCP | UDP |
| --- | --- | --- |
| 连接性 | 面向连接 | 无连接 |
| 可靠性 | 可靠交付 | 尽最大努力交付 |
| 拥塞控制 | 有 | 无 |
| 首部开销 | 20+ 字节 | 8 字节 |
| 传输方式 | 流式传输 | 数据报 |
| 分片 | 传输层分片 MSS | IP 层分片 MTU |

### 三次握手

1. **第一次握手（SYN）**：客户端发送 SYN，状态变为 SYN-SENT
2. **第二次握手（SYN+ACK）**：服务端发送 SYN+ACK，状态变为 SYN-REVD
3. **第三次握手（ACK）**：客户端发送 ACK，双方进入 ESTABLISHED

**为什么三次**：
- 防止历史连接初始化连接（主要原因）
- 同步双方初始序列号
- 减少双方不必要的资源开销

**序列号随机生成**：ISN = M + F，防止历史报文被接收和安全考虑。

### 四次挥手

1. **第一次挥手（FIN）**：主动关闭方发送 FIN
2. **第二次挥手（ACK）**：被动关闭方发送 ACK
3. **第三次挥手（FIN）**：被动关闭方完成数据发送后发送 FIN
4. **第四次挥手（ACK）**：主动关闭方发送 ACK

**为什么需要四次**：服务端需等待完成数据发送，ACK 和 FIN 分开发送。

### TIME_WAIT

等待 2MSL（Maximum Segment Lifetime）。

**原因**：
- 防止历史连接数据被新连接接收
- 保证被动关闭方被正确关闭

**大量 TIME_WAIT 原因**：HTTP 长连接频繁断开。

### TCP 连接队列

- **半连接队列（SYN 队列）**：SYN_RCVD 状态
- **全连接队列（Accept 队列）**：ESTABLISHED 状态

### 保活机制

TCP 保活：空闲后每间隔发送探测报文，连续无响应则认为连接死亡。

参数：tcp_keepalive_time（2小时）、tcp_keepalive_intvl（75秒）、tcp_keepalive_probes（9次）

### Socket 编程流程

服务端：socket → bind → listen → accept → read/write → close

客户端：socket → connect → write/read → close

### TLS 四次握手

1. Client Hello（TLS 版本、密码套件、Client Random）
2. Server Hello（确认 TLS 版本、Server Random）+ Server Certificate
3. Client Key Exchange（pre-master secret，用公钥加密）
4. Change Cipher Spec + Finished

## 关联

- [[操作系统]] - 操作系统基础知识

## 标签

#TCP #三次握手 #四次挥手 #TIME_WAIT #TLS #Socket
