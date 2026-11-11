---
tags: [source-summary, java, security, 面试]
type: source-summary
source: 认证授权
date: 2026-06-09
---

# 认证授权

## 认证 vs 授权

- **认证（Authentication）**：校验用户身份（你是谁？）
- **授权（Authorization）**：校验用户权限（你能做什么？）

## RBAC模型

**基于角色的权限访问控制（Role-Based Access Control）**

用户 → 角色 → 权限，构成多对多关系

数据库设计（5张表）：
- 用户表、角色表、权限表
- 用户-角色关联表、角色-权限关联表

## Cookie

- 存放在**客户端**，保存用户信息
- 应用场景：保存登录信息、保存SessionId/Token、记录用户行为

### Cookie vs Session

| 对比 | Cookie | Session |
|------|--------|---------|
| 存储位置 | 客户端 | 服务端 |
| 安全性 | 较低 | 较高 |
| 生命周期 | 可设过期时间 | 随会话/可配置 |

## Session-Cookie方案

1. 用户发送用户名+密码登录
2. 服务器验证通过，创建Session并存储
3. 返回SessionID写入Cookie
4. 后续请求自动携带Cookie中的SessionID
5. 服务器通过SessionID验证身份

### 多服务器节点Session问题

| 方案 | 优缺点 |
|------|--------|
| 哈希策略分配同一服务器 | 简单但服务器宕机Session丢失 |
| Session同步 | 成本高，节点越多越差 |
| **共享存储（Redis）** | 推荐，高可用 |
| Spring Session | 与Redis/MongoDB集成 |

## Cookie无法防止CSRF，Token可以

**CSRF（跨站请求伪造）**：利用浏览器自动携带Cookie的特性发送恶意请求

| 对比 | Cookie+Session | Token |
|------|---------------|-------|
| 携带方式 | 浏览器自动携带 | 前端手动添加到Header |
| CSRF防护 | 无法防御 | 可以防御 |
| 存储位置 | Cookie | localStorage |

> Token存localStorage而非Cookie → CSRF攻击无法获取Token → 无法构造合法请求

## JWT（JSON Web Token）

- 基于Token的认证授权机制，目前最流行的跨域认证方案
- **自身包含身份验证所需所有信息**，服务端不需要存储Session
- 符合RESTful API无状态原则

### JWT组成
1. **Header**：令牌类型和签名算法
2. **Payload**：用户信息和声明
3. **Signature**：签名，防篡改

### JWT优点
- 无状态，服务端不存Session
- 防CSRF攻击
- 适合分布式系统

## OAuth2.0

行业的标准授权协议，为第三方应用颁发有时效性的令牌Token

**常见场景**：
- 第三方登录（微信/QQ登录）
- 支付场景（微信支付/支付宝）
- 开放平台

**流程**：用户选择第三方登录 → 应用请求OAuth2.0认证 → 显示二维码 → 用户扫码确认 → 第三方返回Token → 后续请求携带Token

## 相关链接

- [[Spring重要知识点]] — Spring核心知识
- [[SpringBoot]] — SpringBoot框架
