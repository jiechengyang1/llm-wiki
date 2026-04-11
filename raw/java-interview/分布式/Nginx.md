# Nginx

<font style="color:rgb(77, 77, 77);">正向代理是</font>**<font style="color:rgb(77, 77, 77);">代理服务器位于</font>****客户端****<font style="color:rgb(77, 77, 77);">和目标服务器之间</font>**<font style="color:rgb(77, 77, 77);">，客户端发送请求时需先将请求发送至代理服务器，代理服务器再将请求转发给目标服务器，并将响应返回给客户端。这种配置可以用于代理客户端访问受限制的内容或保护客户端的身份信息。（服务端不知道客户端的真实IP,都是通过代理服务器转发的请求和响应）</font>

![1726643722971-8bf16b25-22fd-4eb2-a70e-2b8ae3e453c5.png](./img/Uvewf-WBcufPcA_f/1726643722971-8bf16b25-22fd-4eb2-a70e-2b8ae3e453c5-910182.png)

<font style="color:rgb(36, 41, 47);">1、正向代理是为了代理客户端发送请求，而反向代理是为了代理服务器接收请求。</font>

<font style="color:rgb(36, 41, 47);">2、正向代理的主体是客户端，而反向代理的主体是服务器</font>

![1726643786295-9bf7746a-fe7f-46a0-841b-1f204db79af9.png](./img/Uvewf-WBcufPcA_f/1726643786295-9bf7746a-fe7f-46a0-841b-1f204db79af9-344138.png)

[Nginx的代理和负载均衡_nginx 代理 负载-CSDN博客](https://blog.csdn.net/pupcarrot/article/details/133855594)



> 更新: 2024-09-18 15:32:01  
> 原文: <https://www.yuque.com/nibiwanxiamei/yrd6t1/wmy99riniby8m1g8>