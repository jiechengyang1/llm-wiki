# MySQL 重要知识点

## 基础

MySQL 是一款开源的关系型数据库，遵循 SQL 标准，支持 ACID 事务，采用插件式存储引擎架构。InnoDB 是默认存储引擎，支持事务、行级锁、外键。

## 核心

### 索引

索引是数据库加速查询的数据结构，常见类型包括：

**B+Tree 索引**：MySQL 默认索引结构，非叶子节点只存储键值，叶子节点包含所有数据且通过双向链表连接，适合范围查询。

**哈希索引**：基于哈希表实现，适用于等值查询，不支持排序和范围查询，Memory 存储引擎支持。

**全文索引**：用于文本搜索，MATCH AGAINST 语法，支持自然语言和布尔模式。

**索引设计原则**：针对区分度高的列创建索引，考虑查询条件，避免过多索引增加写入开销。

### 事务

事务是数据库操作的逻辑单元，具备 ACID 特性：原子性（Atomicity）、一致性（Consistency）、隔离性（Isolation）、持久性（Durability）。

**隔离级别**：读未提交（READ UNCOMMITTED）、读已提交（READ COMMITTED）、可重复读（REPEATABLE READ，MySQL 默认）、串行化（SERIALIZABLE）。低级别存在脏读、不可重复读、幻读问题。

### MVCC

多版本并发控制（MVCC）是 InnoDB 实现的读不加锁机制，通过 undo log 版本链和 ReadView 实现：

- 每行数据有两个隐藏列：DB_TRX_ID（最近修改的事务 ID）、DB_ROLL_PTR（指向 undo log 的指针）
- 更新时生成新版本，通过 undo log 链接形成版本链
- ReadView 包含 m_ids（活跃事务 ID 列表）、min_trx_id、max_trx_id、creator_trx_id
- READ COMMITTED 每次读取生成新 ReadView，REPEATABLE READ 首次读取生成固定 ReadView
- 根据版本链数据判断可见性：trx_id < min_trx_id 则可见，trx_id > max_trx_id 不可见，在 m_ids 中则根据 undo log 往上找

### 日志系统

**redo log（重做日志）**：物理日志，InnoDB 存储引擎层，记录页面修改，保证事务持久性。crash recovery 时重做已提交事务的修改。固定大小循环写入，配置 innodb_log_file_size 和 innodb_log_files_in_group。采用 WAL（Write-Ahead Logging）机制，事务提交前先写 redo log。

**binlog（归档日志）**：逻辑日志，MySQL Server 层，以 event 形式记录 DDL 和 DML，可用于数据恢复和主从复制。支持 STATEMENT、ROW、MIXED 三种格式，由 sync_binlog 参数控制刷盘策略。

**undo log（回滚日志）**：逻辑日志，记录数据行的旧版本，用于事务回滚和 MVCC。保存于系统表空间（MySQL 5.7 前）或独立 undo 表空间（MySQL 8.0）。当版本链被 GC 且无事务引用时清理。

### InnoDB 存储引擎

InnoDB 采用 B+Tree 聚簇索引，数据文件即索引文件，每个表必须有主键（建议自增整型），辅助索引叶子节点存储主键值。

**Buffer Pool**：缓存磁盘数据页，减少磁盘 IO。配置 innodb_buffer_pool_size，淘汰策略 LRU（分新生代和老年代，避免突发大表扫描污染）。刷脏策略由 innodb_max_dirty_pages_pct 和 page_cleaner 线程协调。

**锁机制**：行锁（Record Lock）、间隙锁（Gap Lock）、临键锁（Next-Key Lock）。查询包含间隙条件时升级为临键锁，防止幻读。意向锁协调表锁和行锁。MDL（Meta Data Lock）保护表结构变更。

### SQL 优化

**EXPLAIN 分析**：type（访问类型，从好到差：system > const > eq_ref > ref > range > index > ALL）、key（实际使用索引）、rows（扫描行数）、Extra（Using filesort、Using temporary、Using index 等）。

**优化方向**：避免 SELECT *、减少子查询改用 JOIN、合理使用覆盖索引、避免数据类型隐式转换、字符串 LIKE 模糊匹配左前缀导致全表扫描、OR 改用 UNION、避免 ORDER BY RAND()。

### 分库分表

垂直拆分按业务模块分库，水平拆分将数据按路由规则（如哈希、时间）分散到多表。ShardingSphere 是成熟中间件解决方案，支持分片、读写分离、分布式事务。

### 主从复制

主从复制基于 binlog 实现：master 将写记录到 binlog，slave 的 IO 线程拉取 binlog 写入 relay log，SQL 线程重放 relay log 实现数据同步。配置 relay_log_purge 清理 relay log。

**复制方式**：异步复制（性能高但可能数据不一致）、半同步复制（slave 接收并写入 relay log 后才确认）、全同步复制（所有 slave 同步后才提交）。

**GTID**：全局事务 ID，基于事务唯一标识简化复制位点管理，避免传统 binlog position 定位难题。

## 关联

- [[数据库基础知识总结]] - 数据库基础概念
- [[Redis重要知识点]] - Redis 相关知识
- [[SHARDINGSPHERE分库分表]] - 分库分表实战

## 标签

#MySQL #InnoDB #索引 #事务 #MVCC #redo log #binlog
