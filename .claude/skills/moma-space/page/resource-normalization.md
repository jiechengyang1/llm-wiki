# 页面资源归一化合同

用于生成、导入、编辑、克隆和素材转换。目标是让最终 HTML 在 MSpace 独立页面 iframe 中可重复加载，同时控制 2 MiB 上限。

## 1. 建立资源清单

解析入口 HTML 和关联样式/脚本，收集：

- `img/src`、`source/src/srcset`；
- `link[href]`、`script[src]`；
- CSS `url(...)` 和 `@import`；
- JavaScript 静态 `import ... from` 与 `import("...")`；
- 图片、字体、stylesheet、script 和其他下载资源。

ZIP 先安全解压到临时目录；所有解析后的路径必须位于该目录内，忽略 `../` 越界项和绝对路径项。

## 2. 归一化策略

按顺序处理：

1. 小型、自有 CSS/JS 内联进单 HTML；
2. 本地图片使用 `POST_api_v1_tools_storage_file_upload-image` 上传，取得可访问 URL 后改写引用；
3. 大型本地脚本、字体或其他不能内联/上传的依赖必须换成已验证可访问的固定版本 URL，不能静默丢失；
4. 保留可靠远程资源时使用 HTTPS 和固定版本，不依赖浮动 `latest`；
5. 重写 `srcset`、CSS URL、import 和嵌套 stylesheet 中的相对路径；
6. 删除来源 `<base>`；容器会在 `<head>` 起始处注入完整预览 URL 的 `<base>`，最终页面不依赖来源目录语义。

不要为了单 HTML 把大型图片转成 base64。base64 会增加体积，且页面 HTML 最大 2 MiB。

## 3. 最终允许状态

每项资源必须属于以下之一：

- `inline`：已经进入 HTML；
- `uploaded`：通过当前 moma-space API 上传并改写为可访问 URL；
- `remote`：HTTPS、可访问且版本固定；
- `unresolved`：只允许存在于分析报告，最终 HTML 禁止。

最终 HTML 禁止：

- `file://`；
- 开发机绝对路径；
- 未实际上传的相对本地文件；
- ZIP 外路径；
- 裸 `localhost`；
- 漂移版本 CDN；
- 依赖来源 `<base>` 才能解析的 URL。

## 4. 检查

```bash
python3 page/lint_page_resources.py '<temporary-workdir>/final.html'
```

检查器覆盖 HTML、CSS、module import、相对文件存在性和 2 MiB 上限。资源存在并不代表发布环境能访问；远程 URL 的实际可用性仍需在最终预览中验证。

## 5. 与生命周期衔接

```text
分析来源
→ 建立资源 inventory
→ 内联/上传/重写
→ 资源 lint + SDK lint
→ upload-node / write_file
→ publish-page
→ 取得 publish URL
→ 清理下载、解压、分析和转换产物
```
