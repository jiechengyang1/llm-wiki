# Elasticsearch

## 基础

Elasticsearch 是一个开源的分布式 RESTful 搜索和分析引擎，基于 Lucene 构建，解决数据库模糊搜索时的性能问题。适用于所有类型数据，包括文本、数字、地理空间、结构化和非结构化数据。早期版本需要 JDK，7.X 后已集成 JDK 无需第三方依赖。

## 核心

### ES vs MySQL

| MySQL | Elasticsearch |
| --- | --- |
| Table | Index |
| Row | Document |
| Column | Field |
| Schema | Mapping |
| SQL | DSL |

**为什么不用 MySQL**：模糊匹配可能全表扫描，全文索引只支持特定字段类型且不支持分词器。

**ES 优势**：支持多种数据类型、RESTful API、多语言兼容、丰富分词器、近实时查询、相关性打分、天然分布式分片。

### 倒排索引

倒排索引首先将文档分词得到词语，然后建立词语与文档 ID 的关联，从而提高检索效率。

**正排索引**：以 DocID 为索引，查询时需扫描所有词语逐个比较，查询效率低但新增数据简单。

**倒排索引**：建立分词和 DocID 关系，查询效率高但建立成本高，维护麻烦。

**倒排索引组成**：
- 单词字典：用 B+Tree 或 Hash 拉链法存储
- 倒排列表：记录 DocID、TF（词频）、Position（位置）、Offset（偏移量）

### Mapping

Mapping 定义字段名称、数据类型、优化信息、分词器，类似数据库表结构定义。

**动态 Mapping**：根据数据自动建立索引和映射类型。

**显示 Mapping**：手动控制字段存储和索引方式。

**dynamic 属性**：
- true：新字段自动添加到映射
- runtime：新字段作为运行时字段，不编入索引
- false：新字段被忽略，不可搜索
- strict：检测到新字段则抛出异常

**映射爆炸**：动态映射可能导致字段无限增加，消耗内存。可通过映射限制设置防止。

### 查询

**请求体查询（Query DSL）**：
- 叶子查询：term（精确匹配）、match（全文检索）
- 复合查询：bool（组合条件）、dis_max

**Term vs 全文检索**：
- Term 查询不做分词处理，用于非文本字段精确匹配
- 全文检索使用分词器，分词后逐词查询汇总得分

**Match vs Match_phrase**：
- Match 多个词默认 OR 关系
- Match_phrase 多个词必须相邻且默认 AND 关系

**Bool 查询子句**：
- must：必须匹配，贡献算分
- should：应该匹配，贡献算分
- must_not：必须不匹配
- filter：必须匹配但不计算得分，提高效率

**Range 查询**：gt、gte、lt、lte，用于范围查找。

### 数据同步

**全量同步**：一次性导入所有数据，常用工具 go-mysql-elasticsearch、Datax。

**增量同步**：
- 同步双写：性能差、有丢数据风险
- 异步双写：使用 MQ 异步写入，引入新组件
- 定时器：时效性差
- Canal：解析 MySQL binlog，业务代码零侵入准实时同步（推荐）

### 集群

Elasticsearch 集群是多节点集合，解决单台服务器负载和存储能力有限的问题，支持横向扩展和高可用。

**分片**：ES 在集群内分发数据的单位，分为主分片和副本分片。索引创建时确定主分片数量，不允许改变。

**副本**：提高可用性，占用资源，不建议过多副本。

**路由公式**：shard = hash(routing) % number_of_primary_shards，默认 routing 为文档 id。

**写入流程**：写主分片，再同步副本分片。

**故障转移**：主分片故障时从副本中选举新主分片。

## 关联

- [[MySQL重要知识点]] - MySQL 基础知识
- [[ShardingSphere分库分表]] - 数据分片方案

## 标签

#Elasticsearch #倒排索引 #Mapping #全文检索 #分布式 #集群
