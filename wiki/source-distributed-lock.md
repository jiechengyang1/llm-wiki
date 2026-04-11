# 资料摘要：分布式锁

## 为什么需要分布式锁

在分布式系统中，多个进程可能同时访问共享资源，需要分布式锁来保证数据一致性。

## 分布式锁特性

- **互斥性**：同一时刻只能一个客户端持有锁
- **可重入**：同一客户端可多次获取同一把锁
- **死锁避免**：客户端崩溃后锁能自动释放
- **公平性**：按请求顺序获取锁
- **性能**：高并发下仍能高效

## 实现方案

### 1. 数据库实现

```sql
-- 乐观锁实现
UPDATE inventory SET stock = stock - 1 WHERE id = 1 AND stock > 0;

-- 唯一索引实现
INSERT INTO distributed_lock (lock_name, owner, expire_time)
VALUES ('order_lock', 'client_123', '2024-01-01 12:00:00');
```

缺点：性能低、无法处理死锁

### 2. Redis实现

**SETNX + EXPIRE**
```lua
-- 原子性
if redis.call('setnx', KEYS[1], ARGV[1], 'EX', ARGV[2]) == 1 then
    return 1
else
    return 0
end
```

**Redisson分布式锁**
```java
RLock lock = redisson.getLock("order_lock");
lock.lock();
try {
    // 业务逻辑
} finally {
    lock.unlock();
}
```

特点：高性能，支持自动续期

### 3. Zookeeper实现

临时有序节点 + Watch机制

```
/locks
  /lock-000000001  (最小序号获得锁)
  /lock-000000002
```

 Curator分布式锁：
```java
InterProcessMutex mutex = new InterProcessMutex(client, "/locks");
mutex.acquire();
try {
    // 业务逻辑
} finally {
    mutex.release();
}
```

特点：可靠性高，一致性强

## Redis vs Zookeeper分布式锁

| 特性 | Redis | Zookeeper |
|------|-------|-----------|
| 性能 | 高 | 中 |
| 可靠性 | 中（需要考虑主从切换） | 高 |
| 实现复杂度 | 中 | 低 |
| 公平支持 | 不支持（需额外实现） | 支持（临时有序节点） |
| 锁释放可靠性 | 中 | 高 |

## Redisson原理

- 看门狗机制：锁自动续期，避免业务未完成锁过期
- 可重入：使用hash存储重入次数
- 公平锁：使用有序队列保证公平

## 分布式锁常见问题

### 1. 锁过期，业务未完成
解决方案：看门狗自动续期

### 2. 主从切换导致锁丢失
解决方案：RedLock算法（多数派）

### 3. 误删他人锁
解决方案：value存唯一标识，删除前校验

```lua
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
```

## 使用建议

- 优先选择Redisson（成熟方案）
- 强一致性场景选Zookeeper
- 性能要求极高选Redis

---

**相关主题：** [[Redis]]
