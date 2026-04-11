# 梦阳GG

为什么选择这个项目，用的技术架构，Spring Boot和Cloud的区别，怎么用Cloud实现的

:::success
+ **<font style="color:rgb(36, 41, 47);background-color:rgb(244, 246, 248);">Spring Boot</font>**<font style="color:rgb(36, 41, 47);background-color:rgb(244, 246, 248);"> </font><font style="color:rgb(36, 41, 47);background-color:rgb(244, 246, 248);">是一个用于简化 Spring 应用程序开发和部署的工具，它关注于单体应用的开发和基础设施。</font>
+ **<font style="color:rgb(36, 41, 47);background-color:rgb(244, 246, 248);">Spring Cloud</font>**<font style="color:rgb(36, 41, 47);background-color:rgb(244, 246, 248);"> 是一个用于构建和管理微服务架构的工具集，它关注于微服务间的通信、配置管理和分布式系统的其他方面。</font>

:::

用的Feign远程调用框架，你了解吗，除了了解这个你还了解那些类以的框架

:::success
<font style="color:rgb(77, 77, 77);">使用Feign的步骤：</font>

<font style="color:rgb(85, 86, 102);background-color:rgb(238, 240, 244);">① 引入依赖  
</font><font style="color:rgb(85, 86, 102);background-color:rgb(238, 240, 244);">② 添加@EnableFeignClient注解  
</font><font style="color:rgb(85, 86, 102);background-color:rgb(238, 240, 244);">③ 编写FeignClient接口  
</font><font style="color:rgb(85, 86, 102);background-color:rgb(238, 240, 244);">④ 使用FeignClient中定义的方法代替RestTemplate</font>

<font style="color:rgb(85, 86, 102);background-color:rgb(238, 240, 244);">Feign基于HTTP，Dubbo基于RPC</font>

<font style="color:rgb(85, 86, 102);background-color:rgb(238, 240, 244);">基本流程</font>

**<font style="color:rgb(25, 27, 31);">a. 主程序入口添加了@EnableFeignClients注解开启对FeignClient扫描加载处理。根据Feign Client的开发规范，定义接口并加@FeignClientd注解。</font>**

**<font style="color:rgb(25, 27, 31);">b. 当程序启动时，会进行包扫描，扫描所有@FeignClients的注解的类，并且将这些信息注入Spring IOC容器中，</font>****<font style="color:#DF2A3F;">当定义的的Feign接口中的方法被调用时，通过JDK</font>**[**<font style="color:#DF2A3F;">动态代理方式</font>**](https://www.zhihu.com/search?q=%E5%8A%A8%E6%80%81%E4%BB%A3%E7%90%86%E6%96%B9%E5%BC%8F&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra=%7B%22sourceType%22%3A%22article%22%2C%22sourceId%22%3A608548106%7D)**<font style="color:#DF2A3F;">，来生成具体的RequestTemplate</font>****<font style="color:rgb(25, 27, 31);">。当生成代理时，Feign会为每个接口方法创建一个RequestTemplate对象，该对象封装可HTTP请求需要的全部信息，如请求</font>**[**<font style="color:rgb(25, 27, 31);">参数名</font>**](https://www.zhihu.com/search?q=%E5%8F%82%E6%95%B0%E5%90%8D&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra=%7B%22sourceType%22%3A%22article%22%2C%22sourceId%22%3A608548106%7D)**<font style="color:rgb(25, 27, 31);">，请求方法等信息都是在这个过程中确定的。</font>**

**<font style="color:rgb(25, 27, 31);">c. 然后RequestTemplate生成Request，然后把Request交给Client去处理，这里指的Client可以是JDK原生的URLConnection、Apache的HttpClient、也可以是OKhttp，最后Client被封装到LoadBalanceClient类，这个类结合Ribbon</font>**[**<font style="color:rgb(25, 27, 31);">负载均衡</font>**](https://www.zhihu.com/search?q=%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra=%7B%22sourceType%22%3A%22article%22%2C%22sourceId%22%3A608548106%7D)**<font style="color:rgb(25, 27, 31);">发起服务之间的调用。</font>**

:::

你项目中有没有限流，怎么实现的，你知道那些限流算法，

:::success
sentinel限流，redis + lua脚本限流

四大限流算法：计数器，滑动窗口，漏桶，令牌桶

:::

降级又是怎么实现的，它和限流的关系你在项目中是如何体现的？？？

使用令牌限流，你觉得必要性大吗？令牌不多以至于好多人抢不到票？（会不会影响到用户体验，你又该如何设计呢）

:::success
令牌就是为了防范突发流量，如果人数过多只能放一部分用户来抢票。

:::

**八股异常-你项目中又是如何定义异常的？三层之间是如何处理的？**

:::success
java异常处理，自定义异常处理controllerAdvice + ExeceptionHandler - 全局异常捕获，针对不同业务设置不同的错误情况，或者抛出不同异常

:::

你除了上面的令牌用到了缓存还有哪里，又是如何保证和数据库一致性的

:::success
缓存使用场景

数据库一致性：先写mysql，在删除redis | 延迟双删 | canel监听binlog

:::

缓存的数据类型

:::success
八大数据类型

:::

java中final的作用（你在做项目中使用它做什么）

:::success
修饰类，修饰方法，修饰变量。。。项目使用，，，**修饰线程本地变量防止被修改**

:::

mysql的引擎，他怎么存储数据的

:::success
B +树，叶子节点存放页面，页面存放了页目录 + 分组 页目录是分组的最大记录，二分查找槽位，在遍历分组找到对应的数据。。一个页面16KB，存放在磁盘块上。。。。。。。。

:::

mysql执行的过程

:::success
连接，查缓存，分析器，优化器，执行器，存储引擎

:::

联合索引？问了一个具体的题那些情况下联合索引会失效

:::success
多个列组成的索引，比如（a，b，c）三个索引，查找不带a，直接b，c或者c导致索引失效

:::

先讲一下hashmap,自己实现一个简单的hashmap

:::success
ACM常见算法有

:::



> 更新: 2024-08-21 22:05:50  
> 原文: <https://www.yuque.com/nibiwanxiamei/yrd6t1/zuam4qe8v05cdicv>