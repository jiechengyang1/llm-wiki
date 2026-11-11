# HTML 本地引用改写

改写 HTML 中的本地资源引用为 S3 URL，写入临时文件，输出临时文件路径。

## 脚本（跨平台）

```bash
node -e "
const fs=require('fs'),os=require('os'),path=require('path'),crypto=require('crypto');
const htmlPath='<folderPath>/<htmlFile>';
let html=fs.readFileSync(htmlPath,'utf-8');
const assetMap=<assetMapJSON>;
for(const [name,s3url] of Object.entries(assetMap)){
  const esc=name.replace(/[.*+?^\${}()|[\]\\\\]/g,'\\\\$&');
  html=html.replace(new RegExp('(src|href)=[\"\\'](\\.\\/)?('+esc+')[\"\\']','g'),'\$1=\"'+s3url+'\"');
}
const tmp=path.join(os.tmpdir(),'moma-html-'+crypto.randomBytes(6).toString('hex')+'.html');
fs.writeFileSync(tmp,html,'utf-8');
console.log('TMP_HTML='+tmp);
"
```

## 参数说明

| 占位符 | 说明 |
|--------|------|
| `<folderPath>/<htmlFile>` | HTML 文件绝对路径 |
| `<assetMapJSON>` | JS 对象字面量，键为文件名，值为 s3Url。例：`{'logo.png':'https://...','bg.mp4':'https://...'}` |

## 输出

`TMP_HTML=<临时文件绝对路径>`，后续上传时使用此路径。
