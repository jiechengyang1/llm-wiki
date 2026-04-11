# 科大讯飞

偏向开发还是算法？

项目是哪里做的，学校还是实习期间？

项目中有挑战的地方在哪里？

说说对分布式架构的理解？

:::color4
**单体服务中，系统的所有模块都是编写在一个机器上，这样做的话部署会简单，但是单体服务不适合我们进行扩展，各个模块之间的耦合度也比较高，需要更新模块时，需要停止整个系统才能更新。同时单体服务对技术栈的选择也不够灵活。**

**业务量很大的情况下，单体服务无法承载大量的需求。微服务架构是将应用程序拆分成多个服务，同时可以更方便的扩展分布式系统。针对不同的服务也可以选择适合的技术栈，选择上会更加灵活。针对不同服务的需求，可以合理动态分配资源，甚至可以采用不同的开发语言开发对应模块。当然微服务也会带来服务复杂性增加，运维压力增大等问题。**

:::

threadLocal保存上下文，也用了redis，为什么还要用ThreadLocal

1. **<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">数据隔离与共享</font>**<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">：</font><code><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">ThreadLocal</font></code><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);"> </font><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">提供线程间的数据隔离，确保每个线程都有自己独立的数据副本；而 Redis 提供跨多个线程、进程或机器的数据共享。两者结合使用，可以在需要时既保证数据的隔离性，又实现数据的共享。</font>
2. **<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">性能与可扩展性</font>**<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">：对于需要频繁访问但不经常变更的共享数据，可以使用 Redis 存储；而对于每个线程特有的上下文信息或临时数据，使用</font><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);"> </font><code><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">ThreadLocal</font></code><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);"> </font><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">存储更为高效。这样，既利用了 Redis 的高性能和可扩展性，又利用了</font><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);"> </font><code><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">ThreadLocal</font></code><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);"> </font><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">的线程隔离和性能优势。</font>
3. **<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">简化代码和逻辑</font>**<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">：在某些情况下，使用 </font><code><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">ThreadLocal</font></code><font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);"> 可以简化代码逻辑，避免将上下文信息作为参数显式传递。同时，Redis 的使用可以提供更灵活的数据存储和访问方式。</font>

<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">redis访问那些方面有性能瓶颈？</font>

**<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">性能瓶颈主要在网络IO 和 内存硬件速度</font>**

<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">TCP的抓包有抓包过吗？分析过吗？</font>

<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">抓过，没有实战用过</font>

<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">TCP报文的组成说说看</font>

<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">TCP头（源端口，目的端口，序列号，确认号，标志位（ack，fin，syn，rst），窗口大小，校验和） +  数据</font>

<font style="color:rgb(5, 7, 59);background-color:rgb(253, 253, 254);">什么时候会出现拒绝连接RST</font>

* 1.网络波动历史连接发送过来
* 2.连接队列满了

ThreadLocal内存泄漏

[9.聊聊ThreadLocal](https://www.yuque.com/nibiwanxiamei/yrd6t1/83fb6387326387e72a6f0920e8813217)

每次使用结束后remove掉。

Redis数据结构有那些

String和Hash的区别

Redis的Zset底层实现是什么

**RedisHash扩容方式**

[Redis](https://www.yuque.com/nibiwanxiamei/yrd6t1/76ffb5da40f53854f93631d9e57dc765)

Java内的Set结构是怎么实现的，JavaSet是如何实现的

[Java集合](https://www.yuque.com/nibiwanxiamei/yrd6t1/4e4c87fd7480bbcafd4ef7dc4f757637)

javaset和treeset基于hashmap和treemap，hashmap = 数组+链表+红黑树，treemap=红黑树

Redis内存快满了会怎么样

面试官想问内存回收的算法机制，我先说的过期key回收策略

LRU和LFU有什么区别

让你自己实现LRU应该怎么实现：HashMap + 链表

并发相关使用了什么？乐观锁vs悲观锁

死锁的必要条件

java乐观锁的实现

从10w数据选取前10个，怎么处理？ 用堆就好了

常见限流算法？

* **计数器，令牌桶，滑动窗口，漏桶**

**源码有阅读吗？HashMap的扩容原理。**

**TCP的序列号有什么用：同步序列好，有序传达**

\*\*粘包问题：放长度，规定数据的长度 \*\*

[聊聊TCP协议的粘包、拆包以及http是如何解决的？\_tcp拆包粘包-CSDN博客](https://blog.csdn.net/cj_eryue/article/details/131046881)

**如何查看TCP状态（Linux）**

**如果说处于timewait是什么原因呢？**

**四次回收timewait有什么作用**

**TCP调优有过吗？**

[计算机网络基础](https://www.yuque.com/nibiwanxiamei/yrd6t1/8700c5656a6bf8550b6756d87ac74f3d)

**JVM理解的垃圾回收算法**

***

***


> 更新: 2024-09-05 14:37:21  
> 原文: <https://www.yuque.com/nibiwanxiamei/yrd6t1/puv4ksnli5q7ic9r>