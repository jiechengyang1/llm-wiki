# 页面相关附件与图片

本文件中的已明确页面生命周期 API 直接调用；写操作首次调用即携带 `--yes`。

## 1. 节点附件

给节点上传附件：

```bash
moma moma-space api POST_api_v1_tools_storage_file_attachment-upload \
  --query 'nodeId=file_node_123' \
  --file 'file=<local-path>' \
  --yes \
  --json
```

获取附件下载地址：

```bash
moma moma-space api POST_api_v1_tools_storage_file_attachment-download \
  --data '{"attachment_id":"att_abc123"}' \
  --json
```

## 2. Agent 构建期图片

Agent 可通过 CLI 上传图片：

```bash
moma moma-space api POST_api_v1_tools_storage_file_upload-image \
  --file 'file=<local-path>' \
  --yes \
  --json
```

该操作返回图片 URL。页面展示资源按 [`resource-normalization.md`](resource-normalization.md) 把本地图片改写为该 URL。把 URL 写入 Database 图片字段是另一件事：必须先通过当前后端接口定义或实际可用 schema 合同验证记录写入结构，不能只根据 schema 的 `config.image` 推断 PropertyValue。

## 3. 页面运行期图片

参数结构见 [`database/database-sdk-schema.md`](database/database-sdk-schema.md) 的 `UploadImageParams`。页面直接把文件选择器产生的 `File` 传给 SDK：

```html
<input id="image-file" type="file" accept="image/*" />
<img id="preview" alt="上传结果" />
<p id="upload-status"></p>

<script>
  const db = window.__SPACE_PAGE__.database;
  const input = document.querySelector("#image-file");
  const preview = document.querySelector("#preview");
  const status = document.querySelector("#upload-status");

  input.addEventListener("change", async () => {
    const file = input.files && input.files[0];
    if (!file) return;

    status.textContent = "上传中...";

    try {
      const uploaded = await db.uploadImage({ file });
      preview.src = uploaded.url;
      status.textContent = "上传成功";
    } catch (error) {
      status.textContent = `上传失败：${error.message}`;
    }
  });
</script>
```

运行时约束：

- 参数必须是当前 iframe 的 `File` 实例；
- 最大 10 MiB；
- 返回 `{ url }`；
- 不需要 FileReader、base64、`contentType` 或 `fileName`；
- 图片上传不会触发 `db.onUpdated`；
- SDK 前端不校验图片扩展名或 MIME Type，不支持的格式由后端拒绝。

真实后端文档列出的格式包括：`png`、`jpg`、`jpeg`、`gif`、`webp`、`bmp`、`svg`、`heic`、`heif`、`tiff`。
