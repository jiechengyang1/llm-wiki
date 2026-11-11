---
tags: [source-summary, MySQL, InnoDB, 死锁, 锁, 面试]
type: source-summary
source: MySQL死锁专题
date: 2026-07-08
---

# MySQL 死锁专题

## 基础概念

**死锁（Deadlock）**：两个或多个事务在执行过程中，因争夺锁资源而造成的一种互相等待的现象。若无外力作用，所有事务都将无法继续推进。

典型报错：`Deadlock found when trying to get lock; try restarting transaction`

**四个必要条件**（缺一不可）：

| 条件 | 含义 | MySQL中的体现 |
|------|------|--------------|
| 互斥 | 资源同时只能被一个事务持有 | 一行数据同一时刻只能被一个事务持有 X 锁 |
| 持有并等待 | 持有资源的同时请求其他资源 | 事务 A 持有行1的锁，等待行2的锁 |
| 不可抢占 | 已持有的资源不能被强制释放 | 锁只能被持有事务显式释放（COMMIT/ROLLBACK） |
| 循环等待 | 事务之间形成环形等待链 | A等B、B等A，形成有向环 |

> 破坏死锁只需打破四个条件中的任意一个。MySQL InnoDB 通过**死锁检测**主动打破循环等待。

## InnoDB 锁体系回顾

### 锁类型速查

| 锁类型 | 作用对象 | 说明 |
|--------|----------|------|
| 记录锁（Record Lock） | 索引记录 | 锁住单行，唯一索引等值匹配时 Next-Key Lock 退化为此锁 |
| 间隙锁（Gap Lock） | 索引间隙 | 锁住区间不含记录本身，**Gap Lock 之间互相兼容**，仅阻止 INSERT |
| 临键锁（Next-Key Lock） | 记录+前间隙 | 左开右闭区间 `(prev, current]`，RR 级别默认加锁单位 |
| 插入意向锁（Insert Intention Lock） | 插入位置的间隙 | INSERT 前申请，与 Gap Lock **互斥**，与其他插入意向锁**兼容** |
| 意向锁（IS/IX） | 表级 | 快速判断表内是否有行锁，意向锁之间互相兼容 |

### 锁兼容性矩阵

|  | IS | IX | S | X | Gap | 插入意向 |
|--|----|----|---|---|-----|---------|
| IS | ✅ | ✅ | ✅ | ❌ | - | - |
| IX | ✅ | ✅ | ❌ | ❌ | - | - |
| S | ✅ | ❌ | ✅ | ❌ | - | - |
| X | ❌ | ❌ | ❌ | ❌ | - | - |
| Gap | - | - | - | - | ✅(兼容) | ❌(互斥) |
| 插入意向 | - | - | - | - | ❌(互斥) | ✅(兼容) |

> **关键**：Gap Lock 之间互相兼容是死锁高发区——多个事务可以同时持有同一间隙的 Gap Lock，但当它们都想 INSERT 时，插入意向锁与对方 Gap Lock 互斥，形成循环等待。

### 加锁基本规则（RR 级别）

1. 加锁对象是**索引**，不是数据行
2. 加锁基本单位是 **Next-Key Lock**（左开右闭）
3. 唯一索引等值查询记录存在时，Next-Key Lock 退化为**记录锁**
4. 唯一索引等值查询记录不存在时，Next-Key Lock 退化为**间隙锁**
5. 非唯一索引等值查询会额外锁住下一个不满足条件的记录前面的间隙
6. 非唯一索引范围查询，Next-Key Lock **不会退化**

## 死锁检测机制

InnoDB 采用 **wait-for graph（等待图）** 算法主动检测死锁：

- 将每个事务视为节点，事务等待关系视为有向边
- 每次加锁请求无法满足进入等待时，触发检测
- 检测图中是否存在**环路**，有环路则存在死锁
- 检测到死锁后，回滚**代价最小**的事务（通常是持有行锁最少的事务）

**关键参数**：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `innodb_deadlock_detect` | ON | 死锁检测开关，生产环境建议开启 |
| `innodb_lock_wait_timeout` | 50s | 锁等待超时时间，作为死锁检测的兜底机制 |
| `innodb_print_all_deadlocks` | OFF | 是否将每次死锁信息输出到错误日志 |

> 生产环境建议：`innodb_print_all_deadlocks = ON`，便于事后分析死锁原因。

## 经典死锁场景

### 场景一：交叉更新（行锁互锁）

**最经典的死锁场景**：两个事务以不同顺序锁定不同行，形成循环等待。

```sql
-- 表：account(id PK, balance)
-- 数据：id=1 balance=100, id=2 balance=200

-- 事务A              -- 事务B
BEGIN;                BEGIN;
UPDATE account
  SET balance=1000
  WHERE id=1;  -- 锁住id=1
                      UPDATE account
                        SET balance=2000
                        WHERE id=2;  -- 锁住id=2
UPDATE account
  SET balance=1000
  WHERE id=2;  -- 等待id=2 ❌
                      UPDATE account
                        SET balance=2000
                        WHERE id=1;  -- 等待id=1 ❌ → 死锁！
```

**等待图**：A等B（id=2），B等A（id=1）→ 形成环路

**解法**：业务上约定按主键从小到大顺序更新，避免交叉加锁。

### 场景二：Gap Lock 互锁（间隙锁+插入意向锁）

**RR 级别下最高频的死锁场景**：两个事务都对同一间隙持有 Gap Lock，然后都想 INSERT。

```sql
-- 表：passjava_test_lock2(a PK, b INDEX, c)
-- 数据：(10,10,10), (15,15,15), (20,20,20)

-- 事务A                           -- 事务B
BEGIN;                             BEGIN;
UPDATE ... SET c=106
  WHERE b=10;
-- 加锁：idx_b Next-Key(-∞,10]
--       idx_b Gap(10,15)
--       PK Record(10)
                                   UPDATE ... SET c=206
                                     WHERE b=15;
                                   -- 加锁：idx_b Next-Key(10,15]
                                   --       idx_b Gap(15,20)
                                   --       PK Record(15)

INSERT INTO ... VALUES(12,12,12);
-- 申请插入意向锁 → 被事务B的Gap(10,15]阻塞 ❌
                                   INSERT INTO ... VALUES(14,14,14);
                                   -- 申请插入意向锁 → 被事务A的Gap(10,15)阻塞 ❌
                                   -- → 死锁！
```

**关键机制**：
1. Gap Lock 之间**互相兼容**，所以事务 A 和 B 都能成功加 Gap Lock
2. INSERT 需要申请**插入意向锁**，与 Gap Lock **互斥**
3. A 的插入意向锁等 B 的 Gap Lock，B 的插入意向锁等 A 的 Gap Lock → 循环等待

**解法**：
- 降低隔离级别为 RC（不加 Gap Lock）
- 改为先 SELECT 再按主键删除/更新（避免非唯一索引加 Gap Lock）
- INSERT 前避免在非唯一索引上做范围更新

### 场景三：唯一键冲突死锁

**并发 INSERT 同一唯一键值**：两个事务同时 INSERT 相同唯一键，发生冲突后各自加 S 锁，再尝试 ROLLBACK 后重新 INSERT 或 REPLACE INTO 导致死锁。

```sql
-- 表：test(id PK, ukvalue UNIQUE KEY)
-- 已有数据：ukvalue=5

-- 事务A                    -- 事务B
BEGIN;                      BEGIN;
INSERT INTO test
  VALUES(null,3,3,5);
-- ukvalue=5冲突 → 对唯一索引加S锁
                            INSERT INTO test
                              VALUES(null,3,3,5);
                            -- ukvalue=5冲突 → 对唯一索引加S锁
                            -- S锁之间兼容，不阻塞

ROLLBACK;  -- 释放S锁
                            -- 事务B等待获取X锁...
INSERT INTO test
  VALUES(null,3,3,5);
-- 尝试加X锁 → 被事务B的S锁阻塞 ❌
                            -- 尝试加X锁 → 被事务A的S锁阻塞 ❌
                            -- → 死锁！
```

**关键机制**：
- INSERT 唯一键冲突时，InnoDB 会对冲突的唯一索引加 **S Record Lock + Gap Lock**（即使 RC 级别也如此）
- S 锁之间兼容，所以两个事务的 INSERT 都会阻塞在 S 锁上
- 当任一事务 ROLLBACK 释放 S 锁后，另一事务获得 S 锁，但还需要升级为 X 锁才能完成 INSERT
- 两个事务互相等待对方释放 S 锁以升级 X 锁 → 死锁

**解法**：
- 使用 `INSERT ... ON DUPLICATE KEY UPDATE` 代替先 INSERT 再处理冲突
- 避免 `REPLACE INTO`（内部是 DELETE+INSERT，更容易死锁）
- 应用层保证唯一键值不冲突（如使用分布式 ID 生成器）

### 场景四：先UPDATE再INSERT的并发死锁

**线上高频死锁场景**：业务逻辑"先删除旧数据再插入新数据"，并发时触发 Gap Lock + 插入意向锁冲突。

```sql
-- 表：user_role(id PK, user_id, role_id)
-- 索引：idx_user_id_role_id(user_id, role_id)
-- 业务：编辑用户权限 → 先按user_id删除旧权限，再插入新权限

-- 事务A（编辑用户1权限）       -- 事务B（编辑用户2权限）
BEGIN;                          BEGIN;
UPDATE user_role
  SET is_deleted=1
  WHERE user_id=1
  AND role_id IN (50,60);
-- 加锁：idx Gap(50,+∞)
                                UPDATE user_role
                                  SET is_deleted=1
                                  WHERE user_id=2
                                  AND role_id IN (50,60);
                                -- 加锁：idx Gap(50,+∞)
                                -- Gap锁兼容，不阻塞 ✅

INSERT INTO user_role
  VALUES(50,50,0);
-- 申请插入意向锁 → 被事务B的Gap锁阻塞 ❌
                                INSERT INTO user_role
                                  VALUES(60,60,0);
                                -- 申请插入意向锁 → 被事务A的Gap锁阻塞 ❌
                                -- → 死锁！
```

**根因**：非唯一索引范围 UPDATE 加 Gap Lock，两个事务 Gap Lock 兼容共存，但 INSERT 时插入意向锁互相冲突。

**解法**：
- 改为先查询出主键，再按主键 DELETE（唯一索引等值查询不加 Gap Lock）
- 使用 `INSERT ... ON DUPLICATE KEY UPDATE` 替代 DELETE+INSERT
- 降低隔离级别为 RC

### 场景五：不同索引锁冲突

**不同索引路径加锁顺序不同**：事务 A 通过二级索引加锁（先二级索引再主键），事务 B 通过主键直接加锁，锁获取顺序不同导致循环等待。

```sql
-- 表：msg(id PK, token INDEX, message)
-- 数据：id=1 token='asd', id=2 token='cvs', id=4 token='qwe'

-- 事务A（通过二级索引）         -- 事务B（通过主键）
BEGIN;                          BEGIN;
DELETE FROM msg
  WHERE token='cvs';
-- 先锁二级索引token='cvs'
-- 再锁主键id=2
                                DELETE FROM msg
                                  WHERE id IN (1,2,4);
                                -- 按主键顺序锁id=1→2→4

-- 事务A持有二级索引锁，等待主键锁
-- 事务B持有部分主键锁，等待二级索引锁
-- → 循环等待，死锁！
```

**根因**：
- 通过二级索引操作时，InnoDB 先锁二级索引记录，再锁对应主键记录
- 不同事务走不同索引路径，加锁顺序不一致，容易形成环路

**解法**：
- 将相关单列索引改为联合索引，减少不同索引路径
- 统一通过主键操作数据
- 业务层面保证操作顺序一致

### 场景六：DELETE相邻记录导致死锁

**DELETE 不存在的记录**：DELETE 未命中记录时加 Gap Lock，两个事务同时 DELETE 同一不存在记录后 INSERT 导致死锁。

```sql
-- 表：t(id PK, c INDEX, d)
-- 数据：(0,0,0), (5,5,5), (10,10,10), (15,15,15)

-- 事务A                  -- 事务B
BEGIN;                    BEGIN;
DELETE FROM t
  WHERE id=4;
-- id=4不存在，加Gap Lock(0,5) ✅
                          DELETE FROM t
                            WHERE id=4;
                          -- id=4不存在，加Gap Lock(0,5) ✅
                          -- Gap锁兼容，不阻塞

INSERT INTO t
  VALUES(3,3,3);
-- 申请插入意向锁 → 被B的Gap Lock阻塞 ❌
                          INSERT INTO t
                            VALUES(3,3,3);
                          -- 申请插入意向锁 → 被A的Gap Lock阻塞 ❌
                          -- → 死锁！
```

**死锁日志关键信息**：
```
lock_mode X locks gap before rec insert intention waiting
```

**根因**：与场景二本质相同——Gap Lock 兼容共存，插入意向锁互相冲突。

**解法**：
- DELETE 前先 SELECT 确认记录存在
- 使用 `DELETE ... WHERE id = ? AND EXISTS (...)` 减少无效 DELETE
- 降低隔离级别为 RC

## 死锁排查方法

### 步骤一：开启死锁日志

```sql
-- 查看当前配置
SHOW VARIABLES LIKE 'innodb_print_all_deadlocks';

-- 开启所有死锁信息输出到错误日志（需SUPER权限）
SET GLOBAL innodb_print_all_deadlocks = ON;

-- my.cnf 永久配置
[mysqld]
innodb_print_all_deadlocks = ON
```

### 步骤二：查看最近一次死锁

```sql
SHOW ENGINE INNODB STATUS;
-- 查看 LATEST DETECTED DEADLOCK 部分
```

### 步骤三：查看当前锁等待（MySQL 8.0+）

```sql
-- 查看当前持有和等待的锁
SELECT * FROM performance_schema.data_locks;

-- 查看锁等待关系
SELECT * FROM performance_schema.data_lock_waits;

-- 查看正在运行的事务
SELECT * FROM information_schema.INNODB_TRX;
```

### 步骤四：定位阻塞线程

```sql
SHOW PROCESSLIST;
-- 重点关注 State 列为 "Waiting for row lock" 的线程

-- 杀死阻塞线程（紧急处理）
KILL <thread_id>;
```

### 步骤五：分析慢查询与长事务

```sql
-- 查看运行时间最长的事务
SELECT trx_id, trx_state, trx_started,
       TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS duration_sec,
       trx_query
FROM information_schema.INNODB_TRX
ORDER BY trx_started;
```

## 死锁日志阅读指南

死锁日志是 `SHOW ENGINE INNODB STATUS` 输出的 `LATEST DETECTED DEADLOCK` 部分，包含两个事务的锁信息：

```
------------------------
LATEST DETECTED DEADLOCK
------------------------
*** (1) TRANSACTION:              ← 事务1信息
TRANSACTION 2322, ACTIVE 6 sec    ← 事务ID，活跃时长
starting index read               ← 事务状态（常见：starting index read / inserting / updating）
2 lock struct(s)                  ← 持有的锁结构数量
MySQL thread id 37                ← 线程ID（对应 show processlist）

*** (1) WAITING FOR THIS LOCK:    ← 事务1正在等待的锁
RECORD LOCKS space id 11 page no 5 n bits 72
index idx_stuno of table student  ← 锁所在的索引
lock_mode X waiting               ← 锁模式
                                  ← X = Next-Key Lock
                                  ← X, REC_NOT_GAP = 记录锁
                                  ← X, GAP = 间隙锁
                                  ← X, GAP, insert intention = 插入意向锁

*** (2) TRANSACTION:              ← 事务2信息
TRANSACTION 2323, ACTIVE 4 sec inserting

*** (2) HOLDS THE LOCK(S):        ← 事务2已持有的锁
RECORD LOCKS ...
lock_mode X locks gap before rec  ← Gap Lock

*** (2) WAITING FOR THIS LOCK:    ← 事务2正在等待的锁
lock_mode X locks gap before rec
insert intention waiting           ← 插入意向锁等待
```

**快速判断锁类型**：

| LOCK_MODE 值 | 锁类型 |
|---------------|--------|
| `X` | Next-Key Lock（记录锁+前间隙锁） |
| `X, REC_NOT_GAP` | 记录锁（仅锁记录） |
| `X, GAP` | 间隙锁（仅锁间隙） |
| `X, GAP, insert intention` | 插入意向锁等待 |
| `S` | 共享 Next-Key Lock |
| `S, REC_NOT_GAP` | 共享记录锁 |

## 避免死锁的最佳实践

### 编码规范

1. **固定加锁顺序**：按主键从小到大更新，避免交叉加锁
2. **缩小事务范围**：减少持锁时间，避免长事务
3. **避免 DELETE + INSERT 模式**：改用 `INSERT ... ON DUPLICATE KEY UPDATE`
4. **避免 `REPLACE INTO`**：内部是 DELETE+INSERT，并发时易死锁
5. **按主键操作**：避免通过非唯一索引操作数据（减少 Gap Lock）
6. **DELETE 前先 SELECT**：避免对不存在的记录加 Gap Lock

### 索引优化

7. **确保索引生效**：索引失效会导致行锁升级为表锁
8. **合理设计联合索引**：减少多个单列索引导致的加锁路径不一致
9. **避免索引列计算**：`WHERE id+1=5` 等写法导致索引失效

### 隔离级别

10. **考虑 RC 级别**：READ COMMITTED 不加 Gap Lock，大幅减少死锁概率
    - 代价：无法通过锁机制防止幻读（仍可通过 MVCC 快照读避免）
    - 很多互联网公司选择 RC 作为生产隔离级别

### 参数配置

11. **开启死锁检测**：`innodb_deadlock_detect = ON`（默认开启）
12. **开启死锁日志**：`innodb_print_all_deadlocks = ON`
13. **合理设置超时**：`innodb_lock_wait_timeout` 根据业务调整（默认50s）
14. **双1配置**：`innodb_flush_log_at_trx_commit=1` + `sync_binlog=1` 保证数据安全

### 架构层面

15. **热点行打散**：秒杀场景将单行拆为多行（如库存分桶）
16. **乐观锁替代**：非强一致性场景用版本号乐观锁替代 `SELECT ... FOR UPDATE`
17. **MQ削峰**：高并发写请求通过消息队列串行化处理

## 面试速记

| 考点 | 关键词 |
|------|--------|
| 死锁定义 | 两个+事务互相等待、四个必要条件、循环等待 |
| 死锁检测 | wait-for graph、有向图环路检测、回滚代价最小的事务 |
| 行锁 vs 表锁死锁 | 行锁会死锁、表锁不会（锁整表无循环等待） |
| Gap Lock 核心 | Gap Lock 之间**兼容**、与插入意向锁**互斥**、这是死锁高发区 |
| 最常见死锁场景 | 先UPDATE加Gap Lock，再INSERT触发插入意向锁冲突 |
| 唯一键冲突死锁 | INSERT冲突加S锁 → 两事务S锁兼容 → 升级X锁互斥 → 死锁 |
| 锁升级为表锁 | 索引失效 → 行锁变表锁 → 冲突概率大增 |
| 如何排查 | `SHOW ENGINE INNODB STATUS` → LATEST DETECTED DEADLOCK |
| 如何避免 | 固定加锁顺序、缩小事务、按主键操作、考虑RC级别 |
| LOCK_MODE 含义 | X=Next-Key, X,REC_NOT_GAP=记录锁, X,GAP=间隙锁, insert intention=插入意向锁 |
| 生产配置 | `innodb_print_all_deadlocks=ON`、`innodb_deadlock_detect=ON` |
| RC vs RR | RC 不加 Gap Lock → 死锁概率低但无法锁防幻读；RR 加 Gap Lock → 死锁概率高但防幻读 |

## 关联

- [[MySQL重要知识点]] - MySQL核心知识总览（索引、事务、MVCC、锁）
- [[数据库基础知识]] - 数据库范式、ER图、NoSQL
- [[ShardingSphere分库分表]] - 分库分表实战
- [[Redis重要知识点]] - Redis核心知识
- [[java锁]] - Java层面的锁与死锁
- [[AQS]] - 抽象队列同步器
- [[分布式锁]] - 分布式场景下的锁实现
- [[面经集合补充]] - 科大讯飞面经问到了死锁问题
