# MyBatis

## 基础

MyBatis 是半自动 ORM 框架，内部封装 JDBC，开发只需关注 SQL 语句，无需处理驱动加载、连接创建等繁杂过程。适合复杂动态 SQL 查询。

## 核心

### #{} vs ${}

- **${}**：变量占位符，直接字符串拼接，存在 SQL 注入风险。用于 SQL 命令或关键字。
- **#{}**：参数占位符，预处理方式执行，替换为 ? 号，参数通过 PreparedStatement 设置。安全，用于普通参数。

### 缓存

**一级缓存（SqlSession 级）**：基于 HashMap，默认开启，存储在 SqlSession 对象中。不同 SqlSession 缓存不共享。

**二级缓存（namespace 级）**：基于 mapper.xml，多个 SqlSession 共享。

### 分页

- **RowBounds**：内存分页，针对 ResultSet
- **物理分页**：SQL 写 Limit
- **分页插件**：拦截 sql 重写，添加分页语句

### 插件

MyBatis 仅可编写针对 ParameterHandler、ResultSetHandler、StatementHandler、Executor 四种接口的插件。JDK 动态代理实现，拦截指定方法。

### 动态 SQL

9 种标签：if、where、trim、set、foreach、choose、when、otherwise、bind。使用 OGNL 计算表达式值动态拼接 SQL。

### 执行器

- **SimpleExecutor**：每执行一次开一个 Statement，用完即关
- **ReuseExecutor**：复用 Statement 对象，缓存 Map
- **BatchExecutor**：批量执行 update，addBatch + executeBatch

### 关联查询

- **一对一**：association 标签
- **一对多**：collection 标签
- **延迟加载**：代理模式实现懒加载

### 映射

- **resultMap**：逐一定义列名和属性名映射
- **sql 别名**：AS 别名为属性名
- **驼峰命名**：开启后自动映射

## 关联

- [[Spring重要知识点]] - Spring 相关
- [[MySQL重要知识点]] - 数据库相关

## 标签

#MyBatis #ORM #缓存 #分页 #动态SQL
