# 计算机网络基础

***

# 计算机网络

# 计算机网络常见面试题总结(上)

## 计算机网络基础

### 网络分层模型

**OSI 七层模型** 是国际标准化组织提出一个网络分层模型

![1718420809890-0189ed32-5c1c-4d01-9796-17d82f989365.png](./img/Dz6jHQjVtUazqKJx/1718420809890-0189ed32-5c1c-4d01-9796-17d82f989365-665241.png)

**TCP/IP 四层模型** 是目前被广泛采用的一种模型,我们可以将 TCP / IP 模型看作是 OSI 七层模型的精简版本，由以下 4 层组成：

1. 应用层
2. 传输层
3. 网络层
4. 网络接口层

![1718420809968-d091fb64-8788-469c-b457-c1a4c55eb8ea.png](./img/Dz6jHQjVtUazqKJx/1718420809968-d091fb64-8788-469c-b457-c1a4c55eb8ea-398569.png)

每一层作用的详细介绍： [OSI 和 TCP/IP 网络分层模型详解（基础）](8e2b039fbdf9b2b35b4c69279026ed80)

### 常见网络协议

![1718420810034-f03a5405-07c2-4a1c-8eca-bb036e89b93a.png](./img/Dz6jHQjVtUazqKJx/1718420810034-f03a5405-07c2-4a1c-8eca-bb036e89b93a-290640.png)

* **HTTP（Hypertext Transfer Protocol，超文本传输协议）** ：基于 TCP 协议，是一种用于传输超文本和多媒体内容的协议，主要是为 Web 浏览器与 Web 服务器之间的通信而设计的。当我们使用浏览器浏览网页的时候，我们网页就是通过 HTTP 请求进行加载的。
* **SMTP（Simple Mail Transfer Protocol，简单邮件发送协议）** ：基于 TCP 协议，是一种用于发送电子邮件的协议。注意 ⚠️：SMTP 协议只负责邮件的发送，而不是接收。要从邮件服务器接收邮件，需要使用 POP3 或 IMAP 协议。
* **POP3/IMAP（邮件接收协议）** ：基于 TCP 协议，两者都是负责邮件接收的协议。IMAP 协议是比 POP3 更新的协议，它在功能和性能上都更加强大。IMAP 支持邮件搜索、标记、分类、归档等高级功能，而且可以在多个设备之间同步邮件状态。几乎所有现代电子邮件客户端和服务器都支持 IMAP。
* **FTP（File Transfer Protocol，文件传输协议）**  : 基于 TCP 协议，是一种用于在计算机之间传输文件的协议，可以屏蔽操作系统和文件存储方式。注意 ⚠️：**FTP 是一种不安全的协议，因为它在传输过程中不会对数据进行加密。建议在传输敏感数据时使用更安全的协议，如 SFTP。**
* **Telnet（远程登陆协议）** ：基于 TCP 协议，用于通过一个终端登陆到其他服务器。Telnet 协议的最大缺点之一是所有数据（包括用户名和密码）均以明文形式发送，这有潜在的安全风险。这就是为什么如今很少使用 Telnet，而是使用一种称为 SSH 的非常安全的网络传输协议的主要原因。
* **SSH（Secure Shell Protocol，安全的网络传输协议）** ：基于 TCP 协议，通过加密和认证机制实现安全的访问和文件传输等业务
* **RTP（Real-time Transport Protocol，实时传输协议）** ：通常基于 UDP 协议，但也支持 TCP 协议。它提供了端到端的实时传输数据的功能，但不包含资源预留存、不保证实时传输质量，这些功能由 WebRTC 实现。
* **DNS（Domain Name System，域名管理系统）** : 基于 UDP 协议，用于解决域名和 IP 地址的映射问题。

关于这些协议的详细介绍 [应用层常见协议总结（应用层）](dcba33666a3eaa385db2f6ba23c0db19)

## HTTP

### 从输入 URL 到页面展示到底发生了什么？（非常重要）

**打开一个网页，整个过程会使用哪些协议**

1. **在浏览器中输入指定网页的 URL。 - 解析URL**
2. **浏览器通过 DNS 协议，获取域名对应的 IP 地址。**
3. **浏览器根据 IP 地址和端口号，向目标服务器发起一个 TCP 连接请求。**
4. **浏览器在 TCP 连接上，向服务器发送一个 HTTP 请求报文，请求获取网页的内容。**
5. **服务器收到 HTTP 请求报文后，处理请求，并返回 HTTP 响应报文给浏览器。**
6. **浏览器收到 HTTP 响应报文后，解析响应体中的 HTML 代码，渲染网页的结构和样式，同时根据 HTML 中的其他资源的 URL（如图片、CSS、JS 等），再次发起 HTTP 请求，获取这些资源的内容，直到网页完全加载显示。**
7. **浏览器在不需要和服务器通信时，可以主动关闭 TCP 连接，或者等待服务器的关闭请求。**

[2.2 键入网址到网页显示，期间发生了什么？](https://xiaolincoding.com/network/1_base/what_happen_url.html)

### HTTP 状态码有哪些？

![1718420810091-3d244513-d3f7-4026-8b70-c1b4e875a6ec.png](./img/Dz6jHQjVtUazqKJx/1718420810091-3d244513-d3f7-4026-8b70-c1b4e875a6ec-964956.png)

[HTTP 常见状态码总结（应用层）](c40d300d327f8388555de4327f45e77c)

### HTTP Header 中常见的字段有哪些？

| 请求头字段名 | 说明 | 示例 |
| --- | --- | --- |
| Accept | 能够接受的回应内容类型（Content-Types）。 | Accept: text/plain |
| Accept-Charset | 能够接受的字符集 | Accept-Charset: utf-8 |
| Accept-Datetime | 能够接受的按照时间来表示的版本 | Accept-Datetime: Thu, 31 May 2007 20:35:00 GMT |
| Accept-Encoding | 能够接受的编码方式列表。参考 HTTP 压缩。 | Accept-Encoding: gzip, deflate |
| Accept-Language | 能够接受的回应内容的自然语言列表。 | Accept-Language: en-US |
| Authorization | 用于超文本传输协议的认证的认证信息 | Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ== |
| Cache-Control | 用来指定在这次的请求/响应链中的所有缓存机制 都必须 遵守的指令 | Cache-Control: no-cache |
| Connection | 该浏览器想要优先使用的连接类型 | Connection: keep-alive Connection: Upgrade |
| Content-Length | 以 八位字节数组 （8 位的字节）表示的请求体的长度 | Content-Length: 348 |
| Content-MD5 | 请求体的内容的二进制 MD5 散列值，以 Base64 编码的结果 | Content-MD5: Q2hlY2sgSW50ZWdyaXR5IQ== |
| Content-Type | 请求体的 多媒体类型 （用于 POST 和 PUT 请求中） | Content-Type: application/x-www-form-urlencoded |
| Cookie | 之前由服务器通过 Set- Cookie （下文详述）发送的一个 超文本传输协议 Cookie | Cookie: $Version=1; Skin=new; |
| Date | 发送该消息的日期和时间(按照 RFC 7231 中定义的"超文本传输协议日期"格式来发送) | Date: Tue, 15 Nov 1994 08:12:31 GMT |
| Expect | 表明客户端要求服务器做出特定的行为 | Expect: 100-continue |
| From | 发起此请求的用户的邮件地址 | From: <user@example.com> |
| Host | 服务器的域名(用于虚拟主机 )，以及服务器所监听的传输控制协议端口号。如果所请求的端口是对应的服务的标准端口，则端口号可被省略。 | Host: [en.wikipedia.org:80open in new window](http://en.wikipedia.org/) |
| If-Match | 仅当客户端提供的实体与服务器上对应的实体相匹配时，才进行对应的操作。主要作用时，用作像 PUT 这样的方法中，仅当从用户上次更新某个资源以来，该资源未被修改的情况下，才更新该资源。 | If-Match: “737060cd8c284d8af7ad3082f209582d” |
| If-Modified-Since | 允许在对应的内容未被修改的情况下返回 304 未修改（ 304 Not Modified ） | If-Modified-Since: Sat, 29 Oct 1994 19:43:31 GMT |
| If-None-Match | 允许在对应的内容未被修改的情况下返回 304 未修改（ 304 Not Modified ） | If-None-Match: “737060cd8c284d8af7ad3082f209582d” |
| If-Range | 如果该实体未被修改过，则向我发送我所缺少的那一个或多个部分；否则，发送整个新的实体 | If-Range: “737060cd8c284d8af7ad3082f209582d” |
| If-Unmodified-Since | 仅当该实体自某个特定时间已来未被修改的情况下，才发送回应。 | If-Unmodified-Since: Sat, 29 Oct 1994 19:43:31 GMT |
| Max-Forwards | 限制该消息可被代理及网关转发的次数。 | Max-Forwards: 10 |
| Origin | 发起一个针对 跨来源资源共享 的请求。 | Origin: [http://www.example-social-network.comopen in new window](http://www.example-social-network.com/) |
| Pragma | 与具体的实现相关，这些字段可能在请求/回应链中的任何时候产生多种效果。 | Pragma: no-cache |
| Proxy-Authorization | 用来向代理进行认证的认证信息。 | Proxy-Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ== |
| Range | 仅请求某个实体的一部分。字节偏移以 0 开始。参见字节服务。 | Range: bytes=500-999 |
| Referer | 表示浏览器所访问的前一个页面，正是那个页面上的某个链接将浏览器带到了当前所请求的这个页面。 | Referer: [http://en.wikipedia.org/wiki/Main\_Pageopen in new window](https://en.wikipedia.org/wiki/Main_Page) |
| TE | 浏览器预期接受的传输编码方式：可使用回应协议头 Transfer-Encoding 字段中的值； | TE: trailers, deflate |
| Upgrade | 要求服务器升级到另一个协议。 | Upgrade: HTTP/2.0, SHTTP/1.3, IRC/6.9, RTA/x11 |
| User-Agent | 浏览器的浏览器身份标识字符串 | User-Agent: Mozilla/5.0 (X11; Linux x86\_64; rv:12.0) Gecko/20100101 Firefox/21.0 |
| Via | 向服务器告知，这个请求是由哪些代理发出的。 | Via: 1.0 fred, 1.1 [example.comopen in new window](http://example.com/)<br/> (Apache/1.1) |
| Warning | 一个一般性的警告，告知，在实体内容体中可能存在错误。 | Warning: 199 Miscellaneous warning |

### HTTP 和 HTTPS 有什么区别？（重要）

![1718420810158-c5b43f90-d496-406b-9c9c-174312a91118.png](./img/Dz6jHQjVtUazqKJx/1718420810158-c5b43f90-d496-406b-9c9c-174312a91118-433932.png)

* **端口号**：HTTP 默认是 80，HTTPS 默认是 443。
* **URL 前缀**：HTTP 的 URL 前缀是 `http://`，HTTPS 的 URL 前缀是 `https://`。
* **安全性和资源消耗**：HTTP 协议运行在 TCP 之上，所有传输的内容都是明文，客户端和服务器端都无法验证对方的身份。HTTPS 是运行在 SSL/TLS 之上的 HTTP 协议，SSL/TLS 运行在 TCP 之上。所有传输的内容都经过加密，加密采用对称加密，但对称加密的密钥用服务器方的证书进行了非对称加密。所以说，HTTP 安全性没有 HTTPS 高，但是 HTTPS 比 HTTP 耗费更多服务器资源。
* **SEO（搜索引擎优化）** ：搜索引擎通常会更青睐使用 HTTPS 协议的网站，因为 HTTPS 能够提供更高的安全性和用户隐私保护。使用 HTTPS 协议的网站在搜索结果中可能会被优先显示，从而对 SEO 产生影响。
* [HTTP vs HTTPS（应用层）](1ca1095098e53c5f49217a00bc2b8651)

### HTTP/1.0 和 HTTP/1.1 有什么区别？

![1718420810220-4f59985b-3f6c-453f-9f5c-dfb3eac5cc90.png](./img/Dz6jHQjVtUazqKJx/1718420810220-4f59985b-3f6c-453f-9f5c-dfb3eac5cc90-103851.png)

* **连接方式** : HTTP/1.0 为短连接，HTTP/1.1 **支持长连接**。
* **状态响应码** : HTTP/1.1 中新加入了大量的状态码，光是错误响应状态码就新增了 24 种。比如说，`100 (Continue)`——在请求大资源前的预热请求，`206 (Partial Content)`——范围请求的标识码，`409 (Conflict)`——请求与当前资源的规定冲突，`410 (Gone)`——资源已被永久转移，而且没有任何已知的转发地址。
* **缓存机制** : 在 HTTP/1.0 中主要使用 Header 里的 If-Modified-Since,Expires 来做为缓存判断的标准，HTTP/1.1 则引入了更多的缓存控制策略例如 Entity tag，If-Unmodified-Since, If-Match, If-None-Match 等更多可供选择的缓存头来控制缓存策略。
* **带宽**：HTTP/1.0 中，存在一些浪费带宽的现象，例如客户端只是需要某个对象的一部分，而服务器却将整个对象送过来了，并且不支持断点续传功能，HTTP/1.1 则在请求头引入了 range 头域，它允许只请求资源的某个部分，即**返回码是 206（Partial Content）** ，这样就方便了开发者自由的选择以便于充分利用带宽和连接。
* **Host 头（Host Header）处理** :HTTP/1.1 引入了 Host 头字段，允许在同一 IP 地址上托管多个域名，从而支持虚拟主机的功能。而 HTTP/1.0 没有 Host 头字段，无法实现虚拟主机。

[HTTP/1.0 vs HTTP/1.1（应用层）](2743c3853ba0253d6aac11b53d0901b2)

### HTTP/1.1 和 HTTP/2.0 有什么区别？

![1718420810281-0c7337df-ee2a-422f-9fe2-b3dd453fdd8a.png](./img/Dz6jHQjVtUazqKJx/1718420810281-0c7337df-ee2a-422f-9fe2-b3dd453fdd8a-116917.png)

* **多路复用（Multiplexing）** ：HTTP/2.0 在同一连接上可以同时传输多个请求和响应（可以看作是 HTTP/1.1 中长链接的升级版本），互不干扰。HTTP/1.1 则使用串行方式，每个请求和响应都需要独立的连接，而浏览器为了控制资源会有 6-8 个 TCP 连接都限制。。这使得 HTTP/2.0 在处理多个请求时更加高效，减少了网络延迟和提高了性能。
* **二进制帧（Binary Frames）** ：HTTP/2.0 使用二进制帧进行数据传输，而 HTTP/1.1 则使用文本格式的报文。二进制帧更加紧凑和高效，减少了传输的数据量和带宽消耗。
* **头部压缩（Header Compression）** ：HTTP/1.1 支持`Body`压缩，`Header`不支持压缩。HTTP/2.0 支持对`Header`压缩，使用了专门为`Header`压缩而设计的 HPACK 算法，减少了网络开销。
* **服务器推送（Server Push）** ：HTTP/2.0 支持服务器推送，可以在客户端请求一个资源时，将其他相关资源一并推送给客户端，从而减少了客户端的请求次数和延迟。而 HTTP/1.1 需要客户端自己发送请求来获取相关资源。

![1718420810341-c3cddd05-2484-4e09-aa7f-7a960a9f1448.png](./img/Dz6jHQjVtUazqKJx/1718420810341-c3cddd05-2484-4e09-aa7f-7a960a9f1448-524834.png)

可以看到，HTTP/2.0 的多路复用使得不同的请求可以共用一个 TCP 连接，避免建立多个连接带来不必要的额外开销，而 HTTP/1.1 中的每个请求都会建立一个单独的连接

### HTTP/2.0 和 HTTP/3.0 有什么区别？

![1718420810403-720e2e6d-942e-4f27-8eeb-a85a0babf9c5.png](./img/Dz6jHQjVtUazqKJx/1718420810403-720e2e6d-942e-4f27-8eeb-a85a0babf9c5-192248.png)

* **传输协议**：HTTP/2.0 是基于 TCP 协议实现的，HTTP/3.0 新增了 **QUIC（Quick UDP Internet Connections） 协议**来实现可靠的传输，提供与 TLS/SSL 相当的安全性，具有较低的连接和传输延迟。你可以将 QUIC 看作是 UDP 的升级版本，在其基础上新增了很多功能比如加密、重传等等。HTTP/3.0 之前名为 **HTTP-over-QUIC**，HTTP/3 最大的改造就是使用了 QUIC。
* **连接建立**：HTTP/2.0 需要经过经典的 TCP 三次握手过程（由于安全的 HTTPS 连接建立还需要 TLS 握手，共需要大约 3 个 RTT）。由于 QUIC 协议的特性（TLS 1.3，TLS 1.3 除了支持 1 个 RTT 的握手，还支持 0 个 RTT 的握手）**连接建立仅需 0-RTT 或者 1-RTT**。这意味着 QUIC 在最佳情况下不需要任何的额外往返时间就可以建立新连接。
* **队头阻塞**：HTTP/2.0 多请求复用一个 TCP 连接，一旦发生丢包，就会阻塞住所有的 HTTP 请求。由于 QUIC 协议的特性，HTTP/3.0 在一定程度上解决了队头阻塞（Head-of-Line blocking, 简写：HOL blocking）问题，一个连接建立多个不同的数据流，这些数据流之间独立互不影响，某个数据流发生丢包了，其数据流不受影响（本质上是多路复用+轮询）。
* **错误恢复**：HTTP/3.0 具有更好的错误恢复机制，当出现丢包、延迟等网络问题时，可以更快地进行恢复和重传。而 HTTP/2.0 则需要依赖于 TCP 的错误恢复机制。
* **安全性**：HTTP/2.0 和 HTTP/3.0 在安全性上都有较高的要求，支持加密通信，但在实现上有所不同。HTTP/2.0 使用 TLS 协议进行加密，而 HTTP/3.0 基于 QUIC 协议，包含了内置的加密和身份验证机制，可以提供更强的安全性。

![1718420810471-e11eac08-d2c4-4eb0-8181-aded64fb00c3.png](./img/Dz6jHQjVtUazqKJx/1718420810471-e11eac08-d2c4-4eb0-8181-aded64fb00c3-488074.png)

### **HTTP 是不保存状态的协议, 如何保存用户状态?**

HTTP 是一种不保存状态，即无状态（stateless）协议。也就是说 HTTP 协议自身不对请求和响应之间的通信状态进行保存。**如何保存用户状态呢**？**Session 机制**的存在就是为了解决这个问题，**Session 的主要作用就是通过服务端记录用户的状态。**

添加商品到购物车的时候，系统不知道是哪个用户操作的，因为 HTTP 协议是无状态的。服务端给特定的用户创建特定的 Session 之后就可以标识这个用户并且跟踪这个用户了（**一般情况下，服务器会在一定时间内保存这个 Session，过了时间限制，就会销毁这个 Session**）。

> **Session是存放在服务器端的一个标识**

在服务端保存 Session 的方法很多，最常用的就是内存和数据库(比如是使用内存数据库 redis 保存)。Session 存放在服务器端，如何实现 Session 跟踪呢？**通过在 Cookie 中附加一个 Session ID 来方式来跟踪**。

> Cookie存放在客户端，客户端存放自己的Session ID，请求时带上Session ID

**Cookie 被禁用怎么办?**

最常用的就是利用 URL 重写把 Session ID 直接附加在 URL 路径的后面。

### URI 和 URL 的区别是什么?

* URI(Uniform Resource Identifier) 是**统一资源标志符**，可以唯一标识一个资源。
* URL(Uniform Resource Locator) 是**统一资源定位符**，**可以提供该资源的路径。它是一种具体的 URI，即 URL 可以用来标识一个资源，而且还指明了如何 locate 这个资源。**

URI 的作用像身份证号一样，URL 的作用更像家庭住址一样。URL 是一种具体的 URI，它不仅唯一标识资源，而且还提供了定位该资源的信息。

> URL = URI + 地址

### Cookie 和 Session 有什么区别？

<code>**Session**</code> **的主要作用就是通过服务端记录用户的状态。**

`Cookie` 数据保存在客户端(浏览器端)，`Session` 数据保存在服务器端。相对来说 `Session` 安全性更高。如果使用 `Cookie` 的一些敏感信息不要写入 `Cookie` 中，最好能将 `Cookie` 信息加密然后使用到的时候再去服务器端解密。

# 计算机网络常见面试题总结(下)

## TCP 与 UDP

### TCP 与 UDP 的区别（重要）

1. **是否面向连接**：UDP 在传送数据之前不需要先建立连接。而 TCP 提供面向连接的服务，在传送数据之前必须先建立连接，数据传送结束后要释放连接。
2. **是否是可靠传输**：远地主机在收到 UDP 报文后，不需要给出任何确认，并且不保证数据不丢失，不保证是否顺序到达。TCP 提供可靠的传输服务，TCP 在传递数据之前，会有三次握手来建立连接，而且在数据传递时，有确认、窗口、重传、拥塞控制机制。通过 TCP 连接传输的数据，无差错、不丢失、不重复、并且按序到达。
3. **是否有状态**：这个和上面的“是否可靠传输”相对应。TCP 传输是有状态的，这个有状态说的是 TCP 会去记录自己发送消息的状态比如消息是否发送了、是否被接收了等等。为此 ，TCP 需要维持复杂的连接状态表。而 UDP 是无状态服务，简单来说就是不管发出去之后的事情了（**这很渣男！** ）。
4. **传输效率**：由于使用 TCP 进行传输的时候多了连接、确认、重传等机制，所以 TCP 的传输效率要比 UDP 低很多。
5. **传输形式**：TCP 是面向字节流的，UDP 是面向报文的。
6. **首部开销**：TCP 首部开销（20 ～ 60 字节）比 UDP 首部开销（8 字节）要大。
7. **是否提供广播或多播服务**：TCP 只支持点对点通信，UDP 支持一对一、一对多、多对一、多对多；

### 什么时候选择 TCP，什么时候选 UDP?

* **UDP 一般用于即时通信**，比如：**语音、 视频、直播**等等。这些场景对传输数据的准确性要求不是特别高，比如你看视频即使少个一两帧，实际给人的感觉区别也不大。
* **TCP 用于对传输准确性要求特别高的场景**，比如文件传输、发送和接收邮件、远程登录等等。

### HTTP 基于 TCP 还是 UDP？

**<font style="color:#DF2A3F;">HTTP/3.0 之前是基于 TCP 协议的，而 HTTP/3.0 将弃用 TCP，改用 基于 UDP 的 QUIC 协议</font>**\*\* 。\*\*

**解决了 HTTP/2 中存在的队头阻塞问题**。队头阻塞是指在 HTTP/2.0 中，多个 HTTP 请求和响应共享一个 TCP 连接，如果其中一个请求或响应因为网络拥塞或丢包而被阻塞，那么后续的请求或响应也无法发送，导致整个连接的效率降低。这是由于 HTTP/2.0 在单个 TCP 连接上使用了多路复用，受到 TCP 拥塞控制的影响，少量的丢包就可能导致整个 TCP 连接上的所有流被阻塞。HTTP/3.0 在一定程度上解决了队头阻塞问题，一个连接建立多个不同的数据流，这些数据流之间独立互不影响，某个数据流发生丢包了，其数据流不受影响（本质上是多路复用+轮询）。

除了解决队头阻塞问题，**HTTP/3.0 还可以减少握手过程的延迟**。在 HTTP/2.0 中，如果要建立一个安全的 HTTPS 连接，需要经过 TCP 三次握手和 TLS 握手：

1. TCP 三次握手：客户端和服务器交换 SYN 和 ACK 包，建立一个 TCP 连接。这个过程需要 1.5 个 RTT（round-trip time），即一个数据包从发送到接收的时间。
2. TLS 握手：客户端和服务器交换密钥和证书，建立一个 TLS 加密层。这个过程需要至少 1 个 RTT（TLS 1.3）或者 2 个 RTT（TLS 1.2）。

所以，HTTP/2.0 的连接建立就至少需要 2.5 个 RTT（TLS 1.3）或者 3.5 个 RTT（TLS 1.2）。而在 HTTP/3.0 中，使用的 QUIC 协议（TLS 1.3，TLS 1.3 除了支持 1 个 RTT 的握手，还支持 0 个 RTT 的握手）连接建立仅需 0-RTT 或者 1-RTT。这意味着 QUIC 在最佳情况下不需要任何的额外往返时间就可以建立新连接。

### TCP 如何保证传输的可靠性？（重要）

[TCP 重传、滑动窗口、流量控制、拥塞控制](https://www.yuque.com/nibiwanxiamei/yrd6t1/130e68a6be1a77cc84134849cfd9eb50)

**序列号和确认号，重传机制，流量控制， 拥塞控制**

## TCP三次握手四次挥手

[三次握手和四次挥手](https://www.yuque.com/nibiwanxiamei/yrd6t1/d968348403feebd58e55f35d6a359929)

### 如何防范SYN攻击

<font style="color:rgb(44, 62, 80);">假设攻击者短时间伪造不同 IP 地址的 </font><code><font style="color:rgb(71, 101, 130);">SYN</font></code><font style="color:rgb(44, 62, 80);"> 报文，服务端每接收到一个 </font><code><font style="color:rgb(71, 101, 130);">SYN</font></code><font style="color:rgb(44, 62, 80);"> 报文，就进入</font><code><font style="color:rgb(71, 101, 130);">SYN_RCVD</font></code><font style="color:rgb(44, 62, 80);"> 状态，但服务端发送出去的 </font><code><font style="color:rgb(71, 101, 130);">ACK + SYN</font></code><font style="color:rgb(44, 62, 80);"> 报文，无法得到未知 IP 主机的 </font><code><font style="color:rgb(71, 101, 130);">ACK</font></code><font style="color:rgb(44, 62, 80);"> 应答，久而久之就会</font>**<font style="color:rgb(48, 79, 254);">占满服务端的半连接队列</font>**<font style="color:rgb(44, 62, 80);">，使得服务端不能为正常用户服务。</font>

![1725956719302-abc5c9e3-b12f-40f8-a7b6-8b4127629eca.png](./img/Dz6jHQjVtUazqKJx/1725956719302-abc5c9e3-b12f-40f8-a7b6-8b4127629eca-776598.png)

<font style="color:rgb(44, 62, 80);">在 TCP 三次握手的时候，Linux 内核会维护两个队列，分别是：</font>

* <font style="color:rgb(44, 62, 80);">半连接队列，也称 SYN 队列；</font>
* <font style="color:rgb(44, 62, 80);">全连接队列，也称 accept 队列；</font>

![1725956738848-7a74cb2d-2bac-4e49-9f18-ac0fc702c5a5.png](./img/Dz6jHQjVtUazqKJx/1725956738848-7a74cb2d-2bac-4e49-9f18-ac0fc702c5a5-771975.png)

**<font style="color:rgb(44, 62, 80);">避免 SYN 攻击方式，可以有以下四种方法：</font>**

* **<font style="color:rgb(44, 62, 80);">调大 netdev\_max\_backlog；</font>**
* **<font style="color:rgb(44, 62, 80);">增大 TCP 半连接队列；</font>**
* **<font style="color:rgb(44, 62, 80);">开启 tcp\_syncookies；</font>**
* **<font style="color:rgb(44, 62, 80);">减少 SYN+ACK 重传次数</font>**

## TCP基于字节流

<font style="color:rgb(44, 62, 80);">当用户消息通过 TCP 协议传输时，</font>**<font style="color:rgb(48, 79, 254);">消息可能会被操作系统分组成多个的 TCP 报文</font>**<font style="color:rgb(44, 62, 80);">，也就是一个完整的用户消息被拆分成多个 TCP 报文进行传输。</font>

<font style="color:rgb(44, 62, 80);">接收方的程序如果不知道发送方发送的消息的长度，是无法读出一个有效的用户消息的，因为用户消息被拆分成多个 TCP 报文后，并不能像 UDP 那样，一个 UDP 报文就能代表一个完整的用户消息，也就产生了粘包问题。</font>

<font style="color:rgb(44, 62, 80);">解决粘包问题的方案：</font>

* <font style="color:rgb(44, 62, 80);">固定长度的消息；</font>
* <font style="color:rgb(44, 62, 80);">特殊字符作为边界；</font>
* <font style="color:rgb(44, 62, 80);">自定义消息结构。</font>

<font style="color:rgb(44, 62, 80);"></font>

<font style="color:rgb(44, 62, 80);"></font>

<font style="color:rgb(44, 62, 80);"></font>

## <font style="color:rgb(44, 62, 80);">为什么 TCP 每次建立连接时，初始化序列号都要不一样呢？</font>

<font style="color:rgb(44, 62, 80);">为了防止历史报文被下一个相同四元组的连接接收。为了尽可能的随机出不一样的序列号，TCP采用如下算法。</font>

<font style="color:rgb(44, 62, 80);">初始化序列号 ISN 随机生成算法：</font>**<font style="color:#DF2A3F;">ISN = M + F</font>**<font style="color:rgb(44, 62, 80);">(localhost, localport, remotehost, remoteport)。</font>

* <font style="color:rgb(44, 62, 80);">M是一个计时器，这个计时器每隔 4 微秒加1。</font>
* <font style="color:rgb(44, 62, 80);">F 是一个 Hash 算法，根据源IP、目的IP、源端口、目的端口生成一个随机数值，要保证 hash 算法不能被外部轻易推算得出。</font>

**<font style="color:rgb(48, 79, 254);">序列号和初始化序列号并不是无限递增的，会发生回绕为初始值的情况，这意味着无法根据序列号来判断新老数据</font>**<font style="color:rgb(44, 62, 80);">。为了解决这个问题，就需要有 TCP 时间戳。tcp\_timestamps 参数是默认开启的，开启了 tcp\_timestamps 参数，TCP 头部就会使用时间戳选项，它有两个好处，</font>**<font style="color:rgb(48, 79, 254);">一个是便于精确计算 RTT ，另一个是能防止序列号回绕（PAWS）</font>**<font style="color:rgb(44, 62, 80);">。</font>**<font style="color:rgb(48, 79, 254);">如果发现收到的数据包中时间戳不是递增的，则表示该数据包是过期的，就会直接丢弃这个数据包</font>**<font style="color:rgb(44, 62, 80);">。</font>

## <font style="color:rgb(44, 62, 80);">SYN 报文什么时候情况下会被丢弃？</font>

* <font style="color:rgb(44, 62, 80);">开启 tcp\_tw\_recycle 参数，并且在 NAT 环境下，造成 SYN 报文被丢弃</font>
* **<font style="color:rgb(44, 62, 80);">TCP 两个队列满了（半连接队列和全连接队列），造成 SYN 报文被丢弃</font>**

## <font style="color:rgb(44, 62, 80);">已建立连接的TCP，收到历史SYN会发生什么？</font>

**<font style="color:rgb(48, 79, 254);">1. 客户端的 SYN 报文里的端口号与历史连接不相同</font>**

<font style="color:rgb(44, 62, 80);">如果客户端恢复后发送的 SYN 报文中的源端口号跟上一次连接的源端口号不一样，此时服务端会认为是新的连接要建立，于是就会通过三次握手来建立新的连接。</font>

<font style="color:rgb(44, 62, 80);">那旧连接里处于 Established 状态的服务端最后会怎么样呢？</font>

* <font style="color:rgb(44, 62, 80);">如果服务端发送了数据包给客户端，由于客户端的连接已经被关闭了，此时客户的内核就会回 RST 报文，服务端收到后就会释放连接。</font>
* <font style="color:rgb(44, 62, 80);">如果服务端一直没有发送数据包给客户端，在超过一段时间后，TCP 保活机制就会启动，检测到客户端没有存活后，接着服务端就会释放掉该连接。</font>

**<font style="color:rgb(48, 79, 254);">2. 客户端的 SYN 报文里的端口号与历史连接相同</font>**

<font style="color:rgb(44, 62, 80);">如果客户端恢复后，发送的 SYN 报文中的源端口号跟上一次连接的源端口号一样。</font>

**<font style="color:rgb(48, 79, 254);">处于 Established 状态的服务端，如果收到了客户端的 SYN 报文（注意此时的 SYN 报文其实是乱序的，因为 SYN 报文的初始化序列号其实是一个随机数），会回复一个携带了正确序列号和确认号的 ACK 报文，这个 ACK 被称之为 Challenge ACK。</font>**

**<font style="color:rgb(48, 79, 254);">接着，客户端收到这个 Challenge ACK，发现确认号（ack num）并不是自己期望收到的，于是就会回 RST 报文，服务端收到后，就会释放掉该连接。</font>**

## <font style="color:rgb(44, 62, 80);">在 TIME\_WAIT 状态的 TCP 连接，收到 SYN 后会发生什么？</font>

<font style="color:rgb(44, 62, 80);">如果处于 TIME\_WAIT 状态的连接收到「合法的 SYN 」后，</font>**<font style="color:rgb(48, 79, 254);">就会重用此四元组连接，跳过 2MSL 而转变为 SYN\_RECV 状态，接着就能进行建立连接过程</font>**<font style="color:rgb(44, 62, 80);">。</font>

![1718601944365-8b3746a3-59dc-4c22-bdac-72715fb6f75a.png](./img/Dz6jHQjVtUazqKJx/1718601944365-8b3746a3-59dc-4c22-bdac-72715fb6f75a-948899.png)

<font style="color:rgb(44, 62, 80);">如果处于 TIME\_WAIT 状态的连接收到「非法的 SYN 」后，就会</font>**<font style="color:rgb(48, 79, 254);">再回复一个第四次挥手的 ACK 报文，客户端收到后，发现并不是自己期望收到确认号（ack num），就回 RST 报文给服务端</font>**<font style="color:rgb(44, 62, 80);">。</font>

![1718601951912-44db3b82-a06e-437d-91f1-1e49db0a2933.png](./img/Dz6jHQjVtUazqKJx/1718601951912-44db3b82-a06e-437d-91f1-1e49db0a2933-480079.png)

## TCP连接后主机宕机和进程崩溃有什么区别

<font style="color:rgb(44, 62, 80);">如果「</font>**<font style="color:rgb(48, 79, 254);">客户端进程崩溃</font>**<font style="color:rgb(44, 62, 80);">」，客户端的进程在发生崩溃的时候，</font>**<font style="color:#DF2A3F;">操作系统内核会发送 FIN 报文，与服务端进行四次挥手</font>**<font style="color:rgb(44, 62, 80);">。</font>

<font style="color:rgb(44, 62, 80);">但是，「</font>**<font style="color:rgb(48, 79, 254);">客户端主机宕机</font>**<font style="color:rgb(44, 62, 80);">」，那么是不会发生四次挥手的，具体后续会发生什么？还要看服务端会不会发送数据？</font>

* <font style="color:rgb(44, 62, 80);">如果服务端会发送数据，由于客户端已经不存在，收不到数据报文的响应报文，服务端的数据报文会超时重传，当重传总间隔时长达到一定阈值（内核会根据 tcp\_retries2 设置的值计算出一个阈值）后，会断开 TCP 连接；</font>
* <font style="color:rgb(44, 62, 80);">如果服务端一直不会发送数据，再看服务端有没有开启 TCP keepalive 机制？</font>
  * <font style="color:rgb(44, 62, 80);">如果有开启，服务端在一段时间没有进行数据交互时，会触发 TCP keepalive 机制，探测对方是否存在，如果探测到对方已经消亡，则会断开自身的 TCP 连接；</font>
  * <font style="color:rgb(44, 62, 80);">如果没有开启，服务端的 TCP 连接会一直存在，并且一直保持在 ESTABLISHED 状态。</font>

## <font style="color:rgb(44, 62, 80);">拔掉网线后TCP连接还存在吗</font>

* <font style="color:rgb(44, 62, 80);">拔掉网线后，有数据传输；</font>
  * <font style="color:rgb(44, 62, 80);">在客户端拔掉网线后，服务端向客户端发送的数据报文会得不到任何的响应，在等待一定时长后，服务端就会触发</font>**<font style="color:rgb(48, 79, 254);">超时重传</font>**<font style="color:rgb(44, 62, 80);">机制，重传未得到响应的数据报文。</font>
  * **<font style="color:rgb(48, 79, 254);">如果在服务端重传报文的过程中，客户端刚好把网线插回去了</font>**<font style="color:rgb(44, 62, 80);">，由于拔掉网线并不会改变客户端的 TCP 连接状态，并且还是处于 ESTABLISHED 状态，所以这时客户端是可以正常接收服务端发来的数据报文的，然后客户端就会回 ACK 响应报文。</font>
  * **<font style="color:rgb(48, 79, 254);">如果如果在服务端重传报文的过程中，客户端一直没有将网线插回去</font>**<font style="color:rgb(44, 62, 80);">，服务端超时重传报文的次数达到一定阈值后，内核就会判定出该 TCP 有问题，然后通过 Socket 接口告诉应用程序该 TCP 连接出问题了，于是服务端的 TCP 连接就会断开。</font>
* <font style="color:rgb(44, 62, 80);">拔掉网线后，没有数据传输；</font>
  * <font style="color:rgb(44, 62, 80);">如果</font>**<font style="color:rgb(48, 79, 254);">没有开启</font>**<font style="color:rgb(44, 62, 80);"> TCP keepalive 机制，在客户端拔掉网线后，并且双方都没有进行数据传输，那么客户端和服务端的 TCP 连接将会一直保持存在。</font>
  * <font style="color:rgb(44, 62, 80);">而如果</font>**<font style="color:rgb(48, 79, 254);">开启</font>**<font style="color:rgb(44, 62, 80);">了 TCP keepalive 机制，在客户端拔掉网线后，即使双方都没有进行数据传输，在持续一段时间后，TCP 就会发送探测报文：</font>
    * <font style="color:rgb(44, 62, 80);">如果</font>**<font style="color:rgb(48, 79, 254);">对端是正常工作</font>**<font style="color:rgb(44, 62, 80);">的。当 TCP 保活的探测报文发送给对端, 对端会正常响应，这样 </font>**<font style="color:rgb(48, 79, 254);">TCP 保活时间会被重置</font>**<font style="color:rgb(44, 62, 80);">，等待下一个 TCP 保活时间的到来。</font>
    * <font style="color:rgb(44, 62, 80);">如果</font>**<font style="color:rgb(48, 79, 254);">对端主机宕机</font>**<font style="color:rgb(44, 62, 80);">（</font>*<font style="color:rgb(200, 73, 255);">注意不是进程崩溃，进程崩溃后操作系统在回收进程资源的时候，会发送 FIN 报文，而主机宕机则是无法感知的，所以需要 TCP 保活机制来探测对方是不是发生了主机宕机</font>*<font style="color:rgb(44, 62, 80);">），或对端由于其他原因导致报文不可达。当 TCP 保活的探测报文发送给对端后，没有响应达到保活探测次数后，</font>**<font style="color:rgb(48, 79, 254);">TCP 会报告该 TCP 连接已经死亡</font>**<font style="color:rgb(44, 62, 80);">。</font>

## <font style="color:rgb(44, 62, 80);">TCP连接过程</font>

![1718690097789-bdec4b6e-ea89-484c-a0a2-63469aefb18c.png](./img/Dz6jHQjVtUazqKJx/1718690097789-bdec4b6e-ea89-484c-a0a2-63469aefb18c-990494.png)

* 若没有listen()就不会建立半连接和全连接队列：此时TCP只能自连接或者客户端之间连接，客户端和服务器无法建立连接，发送数据会RST断开连接。
* 若没有accept()还可以建立连接，建立连接后才从accept()队列中取出连接。

<font style="color:#DF2A3F;">半连接队列是一个Map，全连接队列是一个链表。</font>


> 更新: 2024-09-10 16:27:38  
> 原文: <https://www.yuque.com/nibiwanxiamei/yrd6t1/8700c5656a6bf8550b6756d87ac74f3d>