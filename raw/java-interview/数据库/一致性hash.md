# 一致性hash

<font style="color:rgb(44, 62, 80);">原文：</font>

[9.4 什么是一致性哈希？](https://xiaolincoding.com/os/8_network_system/hash.html)

<font style="color:rgb(44, 62, 80);">一致性哈希算法就很好地解决了分布式系统在扩容或者缩容时，发生过多的数据迁移的问题。</font>

<font style="color:rgb(44, 62, 80);">一致哈希算法也用了取模运算，但与哈希算法不同的是，哈希算法是对节点的数量进行取模运算，而</font>**<font style="color:rgb(48, 79, 254);">一致哈希算法是对 2^32 进行取模运算，是一个固定的值</font>**<font style="color:rgb(44, 62, 80);">。可以把一致哈希算法是对 2^32 进行取模运算的结果值组织成一个圆环 - hash环。</font>

![1722955656897-fc79185c-f25f-4a7e-a911-3f98267dbf2c.png](./img/lC9zwu0QdGFXfNHy/1722955656897-fc79185c-f25f-4a7e-a911-3f98267dbf2c-368722.png)

**<font style="color:rgb(48, 79, 254);">一致性哈希是指将「存储节点」和「数据」都映射到一个首尾相连的哈希环上。顺时针的方向的找到第一个节点</font>**<font style="color:rgb(44, 62, 80);">，就是存储该数据的节点。</font>

![1722955698264-d917b582-39c4-4785-9fac-791ef1bf4254.png](./img/lC9zwu0QdGFXfNHy/1722955698264-d917b582-39c4-4785-9fac-791ef1bf4254-352365.png)

**<font style="color:rgb(48, 79, 254);">在一致哈希算法中，如果增加或者移除一个节点，仅影响该节点在哈希环上顺时针相邻的后继节点，其它数据也不会受到影响</font>**<font style="color:rgb(44, 62, 80);">。但是</font>**<font style="color:rgb(48, 79, 254);">一致性哈希算法并不保证节点能够在哈希环上分布均匀</font>**<font style="color:rgb(44, 62, 80);">，这样就会带来一个问题，会有大量的请求集中在一个节点上。</font>

![1722955750839-05939a2d-e15b-430c-b29d-d4bb1a8e8391.png](./img/lC9zwu0QdGFXfNHy/1722955750839-05939a2d-e15b-430c-b29d-d4bb1a8e8391-085685.png)

<font style="color:rgb(44, 62, 80);">要想解决节点能在哈希环上分配不均匀的问题，就要有大量的节点，节点数越多，哈希环上的节点分布的就越均匀。采用加入</font>**<font style="color:rgb(48, 79, 254);">虚拟节点</font>**<font style="color:rgb(44, 62, 80);">，也就是对一个真实节点做多个副本。引入虚拟节点后，原本哈希环上只有 3 个节点的情况，就会变成有 9 个虚拟节点映射到哈希环上，哈希环的节点数量多了 3 倍。</font>

![1722955811649-1bf5a2a1-6896-47e6-bbdd-dc9761ac33a4.png](./img/lC9zwu0QdGFXfNHy/1722955811649-1bf5a2a1-6896-47e6-bbdd-dc9761ac33a4-774600.png)



> 更新: 2024-08-07 09:40:59  
> 原文: <https://www.yuque.com/nibiwanxiamei/yrd6t1/cdwhd0syi4tzc2pm>