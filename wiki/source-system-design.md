# 系统设计

## 基础

系统设计涵盖高并发场景、分布式架构设计、性能优化等核心问题。

## 核心

### 秒杀系统

**热点数据处理**：静态热点数据提前预热，动态热点数据实时检测。

**高可用**：集群化（Redis 主从-哨兵-集群）、限流（Sentinel/Lua）、流量削峰（MQ）。

**一致性**：下单减库存，Lua 脚本原子操作，异步同步 MySQL。

### 延迟任务

**单机方案**：Timer、ScheduledExecutorService、DelayQueue、Spring Task、时间轮。

**分布式方案**：Redis（过期监听、Redisson DelayedQueue）、RocketMQ（定时消息、时间轮算法）。

### 高并发抢券

- 定时预热活动数据到 Redis
- Lua 脚本扣减库存保证原子性
- 异步同步 MySQL 最终一致

### 大文件上传

分片上传：SHA-256 标识 → 分片 → 并行/串行上传 → 哈希校验 → 分片合并 → 整体校验。

**好处**：断点续传、多线程加速。

### 限速方案

**应用层**：分块传输+sleep、限制缓冲区大小、动态限速（会员）、多线程控制。

**Web 层**：Nginx limit_rate / limit_rate_after。

### 扫码登录

轮询 → 长连接 → WebSocket（双向通信）。

### 数据迁移

双写方案（不停机扩容）：全量迁移 + binlog 增量同步。

### 实时推送

- **短轮询**：定时请求，浪费资源
- **长轮询**：服务端 hold 请求，减少请求次数
- **SSE**：服务端推送，单向，基于 HTTP
- **MQTT**：物联网轻量级协议，发布/订阅
- **WebSocket**：全双工通信，双向

### 排查工具

**Jstack**：生成线程快照，分析 Deadlock、Waiting on condition、Blocked 状态。

**CPU 飙升**：top → top -Hp → printf '%x\n' tid → jstack grep

**内存泄漏**：jstat -gc、jmap dump:format=b,file=xxx、MAT/JProfile 分析

**死锁**：jstack -l 或 JConsole 检测死锁按钮

**OOM**：Dump 堆快照分析，区分内存泄漏和内存溢出

### Redis 宕机处理

1. 诊断：检查进程、日志、redis-cli
2. 恢复：重启、从备份/持久化文件恢复
3. 优化：内存配置、持久化策略、高可用架构
4. 预防：定期备份、Sentinel/Cluster 高可用、监控报警

## 关联

- [[Redis重要知识点]] - Redis 相关
- [[分布式事务]] - 分布式一致性

## 标签

#系统设计 #高并发 #秒杀 #延迟队列 #分布式
