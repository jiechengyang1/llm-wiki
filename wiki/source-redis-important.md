# Redis 重要知识点

## 基础

Redis 是一款基于内存的 Key-Value 存储系统，支持字符串、哈希、列表、集合、有序集合等数据结构，常用作缓存、消息队列、分布式锁、限流、计数器、Session 共享等场景。采用单线程模型（命令执行）和多路复用 IO（Nginx/Memcached 同样的高效 IO 模型），保证原子性，避免上下文切换和锁竞争。

## 核心

### 数据结构

**String（字符串）**：底层实现为 SDS（Simple Dynamic String），支持动态扩容、预分配空间、惰性释放内存，记录长度支持 O(1) 长度获取。与 C 字符串相比避免缓冲区溢出、减少修改重分配次数。

**Hash（哈希）**：底层实现包括ziplist（压缩列表，数据量小采用）和 hashtable，适合存储对象。

**List（列表）**：底层实现为 quicklist（双向链表+压缩列表），支持两端操作，适合消息队列、粉丝列表。

**Set（集合）**：底层实现包括 intset（整数集合，数据全为整数时使用）和 hashtable，支持交集、并集、差集运算。

**Zset（有序集合）**：底层实现包括 ziplist（数据量小）和 skiplist（跳表），按 score 排序，支持范围查询。

**Stream（流）**：Redis 5.0 引入的消息队列实现，支持消费者组、消息 ID、持久化。

### 持久化

**RDB（Redis Database）**：指定时间间隔生成数据集快照，fork 子进程遍历内存写入 RDB 文件，适合备份和灾难恢复。配置 save 规则（seconds changes），可配合 AOF 使用。缺点是可能丢失最近数据。

**AOF（Append Only File）**：记录所有写命令，文本协议格式，通过 fsync 策略控制刷盘（everysec、always、no）。重写机制压缩 AOF 文件（fork 子进程重写生成新文件，避免同步阻塞）。支持混合持久化（Redis 7.0）。

**选择建议**：内存数据量不大（<10GB）优先 AOF everysec，数据量大且能容忍分钟级丢失用 RDB，重要数据用混合持久化。

### 主从复制

主从复制配置 replicaof（旧版本 slaveof），master 可读可写，slave 默认只读。复制流程：slave 发送 psync，master 返回 full sync，master fork 子进程 dump RDB 发送给 slave，slave 加载后持续同步增量命令。

**全量复制**：master 生成 RDB 文件期间持续写入命令保存到 replication buffer，RDB 发送完后发送 buffer 给 slave。

**增量复制**：master 维护 replication stream buffer，每个命令记录 slave 偏移量，slave 断线重连后发送 psync {offset}，master 返回 backlog 范围内数据。

**replication buffer 和 backlog**：replication buffer 用于全量复制阶段主从交互，backlog 用于增量复制。配置 client-output-buffer-limit replica 256mb 64mb 60s 防止 slave 阻塞时 buffer 过大。

### Sentinel（哨兵）

Redis 高可用方案，负责监控 master/slave 健康状态、自动故障转移、通知客户端新的 master 地址。由多个哨兵实例组成集群，哨兵间通过 pub/sub 通信，配置 quorum 决定故障转移决策。

**故障转移流程**：主观下线（SDOWN）→ 客观下线（ODOWN）→ 哨兵投票（leader 选举，基于优先级的 Raft 类算法）→ 执行故障转移（选新 master、提升 slave、通知客户端）。

**常见问题**：异步复制导致的数据丢失（配置 min-slaves-to-write、min-slaves-max-lag）、脑裂问题（网络分区导致多个 master）、 Sentinel 吐血问题（配置down-after-milliseconds）。

### Cluster（集群）

Redis 3.0 引入的分布式方案，数据分片（16384 个 slot），多个 master 节点共同承担数据存储，每个 master 可配置多个 slave。

**数据分片**：基于哈希槽（hash slot），每个 key 计算 CRC16 后对 16384 取模。扩展时 resharding 将部分 slot 迁移到新节点，迁移期间数据存在于新旧两个节点（moved 和 asking 响应）。

**节点通信**：gossip 协议（PING/PONG 携带节点信息，meet 命令主动发现新节点），节点间通过总线端口（客户端端口+10000）通信。

**故障检测**：半数以上 master 认为某节点不可达则标记为 fail，slave 自动提升需等待 slave Promotion Timeout。

**客户端处理**：MOVED 重定向（集群模式下客户端缓存 slot-map 直接路由）、ASK 重定向（迁移中数据访问）、Smart 客户端（维护 slot-map）。

### 缓存问题

**缓存穿透**：查询不存在的数据绕过缓存直击数据库。解决方案：布隆过滤器（Redis 4.0 提供 module）、缓存空值（设短过期时间）、参数校验。

**缓存击穿**：热点 key 过期瞬间大量请求击穿到数据库。解决方案：互斥锁（SETNX）、逻辑过期（后台线程提前重建热点数据）。

**缓存雪崩**：大量 key 同时过期或 Redis 不可用。解决方案：过期时间加随机值、Redis 高可用（Cluster/Sentinel）、服务降级限流。

**缓存一致性**：Cache Aside（先删缓存再更新数据库，延迟双删保证最终一致）、Read Through（缓存自动加载）、Write Through（同步写缓存和数据库）、Write Behind（异步写缓存合并）。

### 分布式锁

基于 SET key value [EX seconds] [NX]（SETNX）实现，需设过期时间防止死锁。RedLock 算法：N 个独立 Redis 实例获取锁，超过半数实例成功则锁有效。Redisson 提供封装好的分布式锁实现（看门狗机制续期）。

### Redis 事务

MULTI/EXEC/WATCH 命令实现事务，批量执行命令，WATCH 实现乐观锁（事务执行前监控 key 变化则放弃执行）。不支持回滚（EXEC 前错误由客户端负责检查）。Lua 脚本保证原子性执行。

### 过期策略与内存淘汰

**过期策略**：惰性删除（访问时检查删除，CPU 友好但内存占用高）、定期删除（随机抽检部分 key，平衡方案）。Redis 采用惰性删除+定期删除组合。

**内存淘汰**：当 Redis 内存达到 maxmemory 时触发淘汰策略。volatile-lru/allkeys-lru（LRU 算法）、volatile-ttl（接近过期时间）、volatile-random/allkeys-random、volatile-lfu/allkeys-lfu（LFU 算法，Redis 4.0+）。建议开启惰性淘汰配合主动淘汰。

## 关联

- [[MySQL重要知识点]] - MySQL 相关知识
- [[一致性hash]] - 一致性哈希算法

## 标签

#Redis #缓存 #持久化 #主从复制 #Sentinel #Cluster
