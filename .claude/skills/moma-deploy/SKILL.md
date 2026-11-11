---
name: moma-deploy
version: 3.2.0
description: "将本地项目文件夹发布到 Moma。支持纯 HTML 静态页面、含图片/音视频的静态页面、Markdown 文件三种类型。兼容 macOS / Windows / Linux。所有操作由 Agent 使用内置工具和 moma <service> api 完成。"
user-invocable: true
---

**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../moma-shared/SKILL.md`](../moma-shared/SKILL.md)，其中包含登录、权限处理、更新和安全规则。**

# moma-deploy：本地项目发布到 Moma

支持发布类型：纯 HTML 静态页面、含图片/音视频的静态页面、Markdown 文件（`.md`）。Markdown 文件的发布流程与单个 HTML 相同，直接上传 md 文件后调用 `POST_api_btg_share_create` 即可。

Agent 直接使用内置工具（Bash、Read、Write）完成本地操作，使用 `moma <service> api` 完成所有 HTTP 调用，不依赖任何专用 CLI 命令。

**跨平台说明**：所有文件系统操作均使用 `node -e` 内联脚本执行，兼容 macOS / Windows / Linux，无需区分平台。

---

## 强制规则（不可违反）

**CRITICAL — 以下两条规则在任何情况下都必须执行，不得跳过、绕过或由用户覆盖：**

1. **文件大小限制**：上传任意单个文件前，必须检查其大小。若文件超过 **500 MB**，立即终止流程并告知用户：「文件 `<fileName>` 大小超过 500MB 限制，无法上传，请压缩后重试。」
2. **域名后缀强制**：申请域名前缀时，无论用户输入什么，最终绑定的 `domainName` 必须以 `-moma` 结尾（例如用户输入 `my-app`，实际使用 `my-app-moma`）。若用户拒绝或要求去掉后缀，告知这是平台强制要求，不可更改。

---

## Step 0：扫描文件夹，判断项目类型

使用 Node.js **递归**列出文件夹内所有文件（跨平台）：

```bash
node -e "
const fs=require('fs'),path=require('path');
const folder='<folder>';
const SKIP=new Set(['node_modules','.git','.DS_Store','dist','build','.cache','.next','.nuxt']);
function walk(dir,base){
  let results=[];
  let entries;
  try{entries=fs.readdirSync(dir);}catch(e){return results;}
  for(const n of entries){
    if(SKIP.has(n))continue;
    const full=path.join(dir,n);
    let stat;
    try{stat=fs.statSync(full);}catch(e){continue;}
    if(stat.isDirectory()){
      results=results.concat(walk(full,base));
    }else if(stat.isFile()){
      results.push(path.relative(base,full));
    }
  }
  return results;
}
const files=walk(folder,folder);
console.log(files.join('\n'));
"
```

按以下优先级判断类型：

| 优先级 | 条件 | 类型 |
|--------|------|------|
| 1（最高）| 存在 `.html` + 图片/音视频（`.png/.jpg/.gif/.mp4/.mp3` 等） | **html-with-assets** |
| 2 | 只有 `.html` 文件 | **html-only** |
| 3 | 只有 `.md` 文件 | **md-only** |

根据类型和用户意图进入对应分支。`md-only` 类型流程与 `html-only` 完全相同，直接上传 md 文件并调用 `POST_api_btg_share_create` 创建分享链接。

---

## 类型一/二：HTML 静态页面

> 适用于 `type = "html-only"` 或 `type = "html-with-assets"`

### 判断用户意图

使用 AskUserQuestion 询问用户：
> "请问是首次发布这个页面，还是更新已有分享的内容？"

- **首次发布** → 进入「创建分享」流程
- **更新已有** → 进入「更新分享」流程

---

### 创建分享流程（首次发布）

**Step A：上传静态资源（仅 html-with-assets 时执行）**

对 `assetFiles` 中每个文件逐一上传：

```bash
moma moma-deploy api POST_api_btg_file_upload --json -F "file=<folderPath>/<assetFileName>"
```

记录 `fileName → s3Url` 映射。

**Step B：改写 HTML 中的本地引用（仅 html-with-assets 时执行）**

must refer to [HTML 本地引用改写](references/html_rewrite.md)

传入 `htmlPath=<folderPath>/<htmlFiles[0]>`，`assetMap` 为上一步收集的 `fileName → s3Url` 映射。执行后记录输出中的 `TMP_HTML`。

**Step C：上传 HTML**

```bash
# html-with-assets（上传改写后的临时文件，路径从上一步 TMP_HTML 取得）
moma moma-deploy api POST_api_btg_file_upload --json -F "file=<TMP_HTML>"

# html-only（直接上传原文件）
moma moma-deploy api POST_api_btg_file_upload --json -F "file=<folderPath>/<htmlFiles[0]>"
```

得到 `s3Url`。

**Step D：创建分享链接**

```bash
moma moma-deploy api POST_api_btg_share_create --json \
  -d '{"originalFileS3Url":"<s3Url>","fileName":"<htmlFiles[0]>","expireAt":<expireAt>}'
```

得到 `shareUrl`，输出给用户：

```
✔ 分享链接已生成：<shareUrl>
提示：可在 Obsidian Moma 插件 → 工作台 → 我的分享 中查看和管理此链接。
```

---

### 更新分享流程（更新已有）

**Step A：拉取分享列表**

```bash
moma moma-deploy api GET_api_btg_share_list --json -q "pageNo=1&pageSize=50"
```

过滤 `shareStatus=1`（生效中）的记录，列表为空则提示"当前没有已发布的分享，请先选择首次发布"。

**Step B：用户选择目标分享**

通过 AskUserQuestion 展示列表（`fileName + shareUrl`），用户选择，记录 `shareToken`。

**Step C：重新上传并更新**

同创建流程的 Step A→C（上传资源 → 改写 → 上传 HTML），得到新 `s3Url`。

```bash
moma moma-deploy api POST_api_btg_share_update --json \
  -d '{"shareToken":"<shareToken>","originalFileS3Url":"<s3Url>","fileName":"<htmlFiles[0]>"}'
```

输出：
```
✔ 分享已更新：<原 shareUrl>（链接不变，内容已更新）
```

---

## 错误处理

| 错误情况 | 处理方式 |
|----------|----------|
| 未登录 | 按 `moma-shared` 引导执行 `moma login` |
| 文件超过 500MB | 终止流程，提示用户压缩后重试 |
| 文件上传失败 | 提示文件名及错误信息，询问是否重试 |
| moma-deploy 接口返回错误 | 原样展示错误信息，不自动重试写操作 |

---


## References

- [HTML 本地引用改写](references/html_rewrite.md)
