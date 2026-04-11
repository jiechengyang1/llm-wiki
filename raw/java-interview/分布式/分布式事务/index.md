# 分布式事务

# <font style="color:rgb(38, 38, 38);">分布式事务概述</font>
<font style="color:rgb(38, 38, 38);">微服务架构下，一个系统被拆分为多个小的微服务。每个微服务都可能存在不同的机器上，并且每个微服务可能都有一个单独的数据库供自己使用。这种情况下，一组操作可能会涉及到多个微服务以及多个数据库。</font>**<font style="color:rgb(38, 38, 38);">分布式事务的终极目标就是保证系统中多个相关联的数据库中的数据的一致性！</font>**

**<font style="color:rgb(38, 38, 38);">分布式事务无法满足ACID特性，但是需要满足CAP理论和BASE理论。</font>**

[CAP & BASE理论详解](https://www.yuque.com/nibiwanxiamei/yrd6t1/d7043aa6299d453426967df23da14f0a)

# 分布式事务解决方案
**<font style="color:rgb(38, 38, 38);">2PC</font>**<font style="color:rgb(38, 38, 38);">、</font>**<font style="color:rgb(38, 38, 38);">3PC</font>**<font style="color:rgb(38, 38, 38);">、</font>**<font style="color:rgb(38, 38, 38);">TCC</font>**<font style="color:rgb(38, 38, 38);">、</font>**<font style="color:rgb(38, 38, 38);">本地消息表</font>**<font style="color:rgb(38, 38, 38);">、</font>**<font style="color:rgb(38, 38, 38);">MQ 事务</font>**<font style="color:rgb(38, 38, 38);">（Kafka 和 RocketMQ 都提供了事务相关功能） 、</font>**<font style="color:rgb(38, 38, 38);">Saga</font>**<font style="color:rgb(38, 38, 38);"> </font>

[Mq消息队列](https://www.yuque.com/nibiwanxiamei/yrd6t1/0762d3f7456a51dee928a917a485ae3a)

<font style="color:rgb(38, 38, 38);">2PC、3PC 属于业务代码无侵入方案，都是基于 XA 规范衍生出来的实现，XA 规范是 X/Open 组织定义的分布式事务处理（DTP，Distributed Transaction Processing）标准。TCC、Saga 属于业务侵入方案，MQ 事务依赖于使用消息队列的场景，本地消息表不支持回滚。</font>

## <font style="color:rgb(38, 38, 38);">2PC</font>
![images](./img/PUD1-jDpbc4YUKd5/1666839341975-f6e983c4-205e-47e2-9f68-aed83651b78c-936854.png)

+ **<font style="color:rgb(38, 38, 38);">AP（Application Program）</font>**<font style="color:rgb(38, 38, 38);">：应用程序本身。</font>
+ **<font style="color:rgb(38, 38, 38);">RM（Resource Manager）</font>**<font style="color:rgb(38, 38, 38);"> ：资源管理器，也就是事务的参与者，绝大部分情况下就是指数据库（后文会以关系型数据库为例），一个分布式事务往往涉及到多个 RM。</font>
+ **<font style="color:rgb(38, 38, 38);">TM（Transaction Manager）</font>**<font style="color:rgb(38, 38, 38);"> ：事务管理器，负责管理全局事务，分配事务唯一标识，监控事务的执行进度，并负责事务的提交、回滚、失败恢复等。</font>

![1666839398805-8d026011-316f-497a-9c11-e5a2e4a4b669.png](./img/PUD1-jDpbc4YUKd5/1666839398805-8d026011-316f-497a-9c11-e5a2e4a4b669-866156.webp)



+ **<font style="color:rgb(38, 38, 38);">2</font>**<font style="color:rgb(38, 38, 38);"> -> 指代事务提交的 2 个阶段</font>
+ **<font style="color:rgb(38, 38, 38);">P</font>**<font style="color:rgb(38, 38, 38);">-> Prepare (准备阶段)</font>
+ **<font style="color:rgb(38, 38, 38);">C</font>**<font style="color:rgb(38, 38, 38);"> ->Commit（提交阶段）</font>

### **<font style="color:rgb(38, 38, 38);">准备阶段(Prepare)</font>**
<font style="color:rgb(38, 38, 38);">准备阶段的核心是“询问”事务参与者执行本地数据库事务操作是否成功。  
</font><font style="color:rgb(38, 38, 38);">准备阶段的工作流程：</font>

1. **<font style="color:rgb(38, 38, 38);">事务协调者/管理者（后文简称 TM）</font>**<font style="color:rgb(38, 38, 38);"> 向所有涉及到的 </font>**<font style="color:rgb(38, 38, 38);">事务参与者（后文简称 RM）</font>**<font style="color:rgb(38, 38, 38);"> 发送消息询问：“你是否可以执行事务操作呢？”，并等待其答复。</font>
2. **<font style="color:rgb(38, 38, 38);">RM</font>**<font style="color:rgb(38, 38, 38);"> 接收到消息之后，开始执行本地数据库事务预操作比如写 redo log/undo log 日志，</font>**<font style="color:rgb(38, 38, 38);">此时并不会提交事务</font>**<font style="color:rgb(38, 38, 38);"> 。</font>
3. **<font style="color:rgb(38, 38, 38);">RM</font>**<font style="color:rgb(38, 38, 38);"> 如果执行本地数据库事务操作成功，那就回复“Yes”表示我已就绪，否则就回复“No”表示我未就绪。</font>

### <font style="color:rgb(38, 38, 38);">提交阶段(Commit)</font>
<font style="color:rgb(38, 38, 38);">提交阶段的核心是“询问”事务参与者提交本地事务是否成功。</font>

<font style="color:rgb(38, 38, 38);">当所有事务参与者都是“就绪”状态的话：</font>

1. **<font style="color:rgb(38, 38, 38);">TM</font>**<font style="color:rgb(38, 38, 38);"> 向所有参与者发送消息：“你们可以提交事务啦！”（</font>**<font style="color:rgb(38, 38, 38);">Commit 消息</font>**<font style="color:rgb(38, 38, 38);">）</font>
2. **<font style="color:rgb(38, 38, 38);">RM</font>**<font style="color:rgb(38, 38, 38);"> 接收到 </font>**<font style="color:rgb(38, 38, 38);">Commit 消息</font>**<font style="color:rgb(38, 38, 38);"> 后执行 </font>**<font style="color:rgb(38, 38, 38);">提交本地数据库事务</font>**<font style="color:rgb(38, 38, 38);"> 操作，执行完成之后 </font>**<font style="color:rgb(38, 38, 38);">释放整个事务期间所占用的资源</font>**<font style="color:rgb(38, 38, 38);">。</font>
3. **<font style="color:rgb(38, 38, 38);">RM</font>**<font style="color:rgb(38, 38, 38);"> 回复：“事务已经提交” （</font>**<font style="color:rgb(38, 38, 38);">ACK 消息</font>**<font style="color:rgb(38, 38, 38);">）。</font>
4. **<font style="color:rgb(38, 38, 38);">TM</font>**<font style="color:rgb(38, 38, 38);"> 收到所有 </font>**<font style="color:rgb(38, 38, 38);">事务参与者</font>**<font style="color:rgb(38, 38, 38);"> 的 </font>**<font style="color:rgb(38, 38, 38);">ACK 消息</font>**<font style="color:rgb(38, 38, 38);"> 之后，整个分布式事务过程正式结束。</font>

## <font style="color:rgb(38, 38, 38);">3PC</font>
![1666839392078-2129a477-9728-4d28-8b47-8aa4fd74570c.png](./img/PUD1-jDpbc4YUKd5/1666839392078-2129a477-9728-4d28-8b47-8aa4fd74570c-022869.webp)

<font style="color:rgb(38, 38, 38);">3PC 是人们在 2PC 的基础上做了一些优化得到的。3PC 把 2PC 中的 </font>**<font style="color:rgb(38, 38, 38);">准备阶段(Prepare)</font>**<font style="color:rgb(38, 38, 38);"> 做了进一步细化，分为 2 个阶段：</font>

+ <font style="color:rgb(38, 38, 38);">准备阶段(CanCommit)</font>
+ <font style="color:rgb(38, 38, 38);">预提交阶段(PreCommit)</font>

## <font style="color:rgb(38, 38, 38);">MQ事务</font>
<font style="color:rgb(38, 38, 38);">RocketMQ 、 Kafka、Pulsar 、QMQ 都提供了事务相关的功能。事务允许事件流应用将消费，处理，生产消息整个过程定义为一个原子操作。</font>

![images](./img/PUD1-jDpbc4YUKd5/1632403905120-c70b8cfa-52f6-4132-8f75-853421a64795-171541.png)

<font style="color:rgb(38, 38, 38);"></font>

+ <font style="color:rgb(38, 38, 38);">MQ 发送方（比如物流服务）在消息队列上开启一个事务，然后发送一个“半消息”给 MQ Server/Broker。事务提交之前，半消息对于 MQ 订阅方/消费者（比如第三方通知服务）不可见</font>
+ <font style="color:rgb(38, 38, 38);">半消息发送成功的话，MQ 发送方就开始执行本地事务。</font>
+ <font style="color:rgb(38, 38, 38);">MQ 发送方的本地事务执行成功的话，“半消息”变成正常消息，可以正常被消费。MQ 发送方的本地事务执行失败的话，会直接回滚。</font>

**<font style="color:#DF2A3F;">MQ 的事务消息使用的是两阶段提交（2PC），简单来说就是咱先发送半消息，等本地事务执行成功之后，半消息才变为正常消息。</font>**



> 更新: 2024-07-24 22:01:06  
> 原文: <https://www.yuque.com/nibiwanxiamei/yrd6t1/xc06wnmds4xpaknn>