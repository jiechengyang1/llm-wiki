# 页面运行期 Database SDK 合同

本合同以真实实现文档 `mspace-page-database-sdk.md` 为准，供 Agent 生成可在 MSpace 独立页面中运行的 HTML。

## 1. 运行环境和入口

SDK 只注入到 `/mspace/page/:id` 独立预览页的 iframe HTML 中。推荐入口：

```javascript
const db = window.__SPACE_PAGE__.database;
const DATABASE_ID = "<real-database-id>";
```

SDK 没有 `ready()`。异步方法会等待 MessageChannel 建立；如果通道始终未建立，Promise 可能保持 pending。SDK 没有内置超时、取消或 `AbortSignal`。

## 2. 真实 API

完整类型定义见 [`database-sdk-schema.md`](database-sdk-schema.md)。

| 方法 | 入参 | 返回 |
|---|---|---|
| `db.query` | `{ database_id, filter?, sorts?, cursor?, page_size? }` | `Promise<{ results, next_cursor, has_more }>` |
| `db.addRecord` | `{ database_id, record }` | `Promise<BatchRecordResult>` |
| `db.getRecord` | `{ database_id, record_id }` | `Promise<{ record_id, fields }>` |
| `db.updateRecord` | `{ database_id, record_id, properties }` | `Promise<BatchRecordResult>` |
| `db.deleteRecord` | `{ database_id, record_id }` | `Promise<BatchRecordResult>` |
| `db.getSchema` | `{ database_id }` | `Promise<{ id, title, properties }>` |
| `db.uploadImage` | `{ file }` | `Promise<{ url }>` |
| `db.onUpdated` | `handler(event)` | `() => boolean` 取消订阅函数 |

运行期 SDK 入参和返回字段都使用 snake_case。不要改成 camelCase。

`database_id` 必须是 trim 后非空且最长 64 字符的 string；`record_id` 必须是非空 string。

## 3. Schema

```javascript
const schema = await db.getSchema({
  database_id: DATABASE_ID,
});
```

返回：

```javascript
{
  id: "db_001",
  title: "项目任务",
  properties: [
    {
      id: "field_001",
      name: "任务名称",
      config: { text: "" },
    },
  ],
}
```

可靠的 property 结构是 `{ id?, name, config }`。不要假设存在通用 `type` 字段；字段类型从 `config` 的唯一类型键判断。筛选、排序、读取和表单字段名使用真实 `property.name`。

## 4. 查询、过滤和分页

SDK 每次只查询一页，不会自动翻页：

```javascript
const page = await db.query({
  database_id: DATABASE_ID,
  filter: {
    and: [
      {
        property: {
          property: "完成状态",
          checkbox: { equals: false },
        },
      },
    ],
  },
  sorts: [{ property: "截止日期", direction: "ascending" }],
  page_size: 100,
});
```

参数：

- `cursor`：下一页使用上一页的 `next_cursor`；
- `page_size`：1–1000 的整数，默认由后端决定；页面通常使用 100；
- `sorts`：对象数组，direction 为 `ascending` 或 `descending`；
- `filter`：使用实际 schema 字段名。

返回：

```javascript
{
  results: [
    {
      record_id: "100000001",
      fields: {
        "任务名称": "编写文档",
        "完成状态": false,
      },
    },
  ],
  next_cursor: "next-page-token",
  has_more: true,
}
```

读取记录必须使用 `record.record_id` 和 `record.fields`，不能把记录当作扁平对象，也没有 `_id` 合同。

完整分页：

```javascript
async function queryAllRecords(database_id) {
  const all = [];
  let cursor;

  do {
    const page = await db.query({
      database_id,
      cursor,
      page_size: 100,
    });

    all.push(...(page.results || []));
    const next = page.has_more ? page.next_cursor : undefined;
    cursor = next && next !== cursor ? next : undefined;
  } while (cursor);

  return all;
}
```

支持的常用过滤操作符：

- text：`equals`、`contains`；
- number：`equals`、`greater_than`、`less_than`、`greater_than_or_equal`、`less_than_or_equal`、`is_empty`；
- select：`equals`、`does_not_equal`；
- date：`equals`、`before`、`after`；
- checkbox：`equals`、`does_not_equal`；
- person：`equals`、`does_not_equal`、`contains`、`does_not_contain`、`is_empty`。

每个 filter 节点只放 `property`、`and`、`or` 中的一种。

## 5. 读取值与写入值

查询和 `getRecord` 返回展示值：

```javascript
const record = await db.getRecord({
  database_id: DATABASE_ID,
  record_id: "100000001",
});

console.log(record.record_id, record.fields["任务名称"]);
```

读取值与写入值不是同一种结构。真实文档明确支持的常见写入值：

```javascript
const record = {
  "姓名": { text: "张三" },
  "年龄": { number: 20 },
  "部门": { select: "技术部" },
  "标签": { multi_select: ["研发", "后端"] },
  "入职日期": { date: "2026-01-15" },
};
```

日期记录使用 `{ date: "YYYY-MM-DD" }` 写入，新增和更新结构相同；查询和 `getRecord` 返回的 `fields` 中，日期展示值为同格式字符串。复选框、链接、邮箱、电话、图片、附件、人员等记录写入结构没有在真实 SDK 文档中完整定义。不要从 schema `config` 自行推断；仅在当前后端接口定义或实际响应已验证时生成这些字段的写入代码。

## 6. CRUD

新增参数名是 `record`，不是 `properties`：

```javascript
const created = await db.addRecord({
  database_id: DATABASE_ID,
  record: {
    "姓名": { text: "张三" },
    "年龄": { number: 20 },
    "入职日期": { date: "2026-01-15" },
  },
});

console.log(created.id);
```

增量更新：

```javascript
const updated = await db.updateRecord({
  database_id: DATABASE_ID,
  record_id: "100000001",
  properties: {
    "年龄": { number: 21 },
    "入职日期": { date: "2026-02-01" },
  },
});
```

删除：

```javascript
const deleted = await db.deleteRecord({
  database_id: DATABASE_ID,
  record_id: "100000001",
});
```

增删改都返回批量接口的第一项：

```javascript
{
  index: 0,
  id: "100000001",
  success: true,
}
```

记录 ID 字段是 `id`，不是 `record_id`。单项失败时 Promise reject，不会把 `success: false` 当成正常成功值返回。

## 7. 图片上传

运行期直接传 iframe 文件选择器得到的 `File`：

```javascript
const file = document.querySelector("#image-file").files[0];
const uploaded = await db.uploadImage({ file });
console.log(uploaded.url);
```

- 必须是当前 iframe 中的 `File` 实例；
- 最大 10 MiB；
- 返回 `{ url }`；
- 不需要 FileReader、base64、contentType 或 fileName；
- `uploadImage` 只上传并返回 URL，不触发 `onUpdated`；
- 把 URL 写入 Database 图片字段前，必须先验证真实后端的该字段写入结构。

## 8. 更新通知

```javascript
const unsubscribe = db.onUpdated(async (event) => {
  if (event.database_id !== DATABASE_ID) return;
  console.log(event.type, event.record_id);
  await reloadCurrentPage();
});
```

事件：

```javascript
{
  type: "add" | "update" | "delete",
  database_id: "db_001",
  record_id: "100000001", // 可选
}
```

`onUpdated` 同步返回取消订阅函数：

```javascript
unsubscribe();
```

通知范围只包括**当前 iframe 通过 SDK 成功完成的增删改**。它不是数据库实时订阅，不会通知其他用户、标签页、iframe、主应用或后端任务产生的修改。事件不携带完整记录，需要最新值时重新调用 `query` 或 `getRecord`。

## 9. 错误和页面状态

所有异步调用使用 `try/catch`。错误对象可能包含：

```javascript
{
  message,
  code,
  details,
}
```

常见 code：`INVALID_PARAMS`、`INVALID_RESPONSE`、`RECORD_OPERATION_FAILED`、`HTTP_401`、`HTTP_403`、`DATABASE_API_ERROR`、`DATABASE_BRIDGE_ERROR`。`onUpdated` 收到非函数时同步抛出 `INVALID_HANDLER`。

页面实现 loading、empty、ready、error、submitting。为避免 SDK 通道异常时 UI 永久 loading，可在业务层使用 Promise.race 超时：

```javascript
function withTimeout(promise, ms = 10000) {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error("操作超时")), ms);
    }),
  ]);
}
```

该包装只停止页面等待，不会取消已经发出的 SDK 或后端请求。

## 10. 页面产物约束

- SDK 只在 `/mspace/page/:id` 独立预览 iframe 中可用；
- 父页面把 SDK 注入 `<head>` 起始位置；
- HTML 最大 2 MiB；
- 父页面会注入 `<base href="完整预览 URL">`，相对资源按预览 URL 解析；
- 最终页面仍应尽量生成单 HTML，并按 Skill 生命周期上传、发布、清理和返回 publish URL。
