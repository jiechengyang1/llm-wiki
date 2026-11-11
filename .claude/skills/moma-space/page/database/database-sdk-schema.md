# Database SDK 参数与返回 Schema

本文件是生成页面运行时代码时的结构速查。使用合同和示例见 [`database-sdk-contract.md`](database-sdk-contract.md)。

## 1. 全局入口

```typescript
interface Window {
  __SPACE_PAGE__: {
    database: SpacePageDatabase;
  };
}
```

```javascript
const db = window.__SPACE_PAGE__.database;
```

## 2. 公共类型

```typescript
type JsonObject = Record<string, unknown>;
type SortDirection = "ascending" | "descending";

interface DatabaseRecord {
  record_id: string;
  fields: JsonObject;
}

interface DatabaseSort {
  property: string;
  direction: SortDirection;
}

interface Property {
  id?: string;
  name: string;
  config: JsonObject;
}

interface DatabaseSchema {
  id: string;
  title: string;
  properties: Property[];
}

interface BatchRecordResult {
  index: number;
  id?: string;
  success: boolean;
  error?: string;
}

interface UploadImageResult {
  url: string;
}

interface DatabaseUpdatedEvent {
  type: "add" | "update" | "delete";
  database_id: string;
  record_id?: string;
}

interface DatabaseSdkError extends Error {
  code?: string;
  details?: unknown;
}
```

## 3. 查询

```typescript
interface QueryParams {
  database_id: string;
  filter?: DatabaseFilter;
  sorts?: DatabaseSort[];
  cursor?: string;
  page_size?: number;
}

interface QueryResult {
  results: DatabaseRecord[];
  next_cursor: string | null;
  has_more: boolean;
}
```

约束：

- `database_id`：trim 后非空，最长 64 字符；
- `cursor`：提供时必须是 trim 后非空字符串；
- `page_size`：1–1000 的整数；
- `sorts`：对象数组；
- 多余字段不会发送给后端。

## 4. Filter

```typescript
type DatabaseFilter =
  | {
      property: {
        property: string;
        text?: {
          equals?: string;
          contains?: string;
        };
        number?: {
          equals?: number;
          greater_than?: number;
          less_than?: number;
          greater_than_or_equal?: number;
          less_than_or_equal?: number;
          is_empty?: boolean;
        };
        select?: {
          equals?: string;
          does_not_equal?: string;
        };
        date?: {
          equals?: string;
          before?: string;
          after?: string;
        };
        checkbox?: {
          equals?: boolean;
          does_not_equal?: boolean;
        };
        person?: {
          equals?: string;
          does_not_equal?: string;
          contains?: string;
          does_not_contain?: string;
          is_empty?: boolean;
        };
      };
    }
  | { and: DatabaseFilter[] }
  | { or: DatabaseFilter[] };
```

每个节点只使用 `property`、`and`、`or` 中的一种。字段名使用 `getSchema()` 返回的真实 `Property.name`。

## 5. 已验证的记录写入值

```typescript
interface TextValue {
  text: string;
}

interface NumberValue {
  number: number;
}

interface SelectValue {
  select: string;
}

interface MultiSelectValue {
  multi_select: string[];
}

interface DateValue {
  date: string; // YYYY-MM-DD
}

type ConfirmedRecordValue =
  | TextValue
  | NumberValue
  | SelectValue
  | MultiSelectValue
  | DateValue;

type ConfirmedRecordProperties = Record<
  string,
  ConfirmedRecordValue
>;
```

当前真实 SDK 文档明确上述五类记录写入值。日期使用 `{ date: "YYYY-MM-DD" }`，例如 `{ date: "2026-01-15" }`；查询和 `getRecord` 读取时返回同格式字符串。复选框、URL、邮箱、电话、图片、附件和人员等字段必须在真实后端写入合同已验证后再扩展，不根据 schema `config` 猜测。

## 6. 方法参数

```typescript
interface GetSchemaParams {
  database_id: string;
}

interface GetRecordParams {
  database_id: string;
  record_id: string;
}

interface AddRecordParams {
  database_id: string;
  record: JsonObject;
}

interface UpdateRecordParams {
  database_id: string;
  record_id: string;
  properties: JsonObject;
}

interface DeleteRecordParams {
  database_id: string;
  record_id: string;
}

interface UploadImageParams {
  file: File;
}
```

约束：

- `record_id`：trim 后非空字符串；
- `record`、`properties`：非数组对象；
- `file`：当前 iframe 中的 `File` 实例，最大 10 MiB。

## 7. SDK 方法

```typescript
interface SpacePageDatabase {
  query(params: QueryParams): Promise<QueryResult>;

  addRecord(
    params: AddRecordParams
  ): Promise<BatchRecordResult>;

  getRecord(
    params: GetRecordParams
  ): Promise<DatabaseRecord>;

  updateRecord(
    params: UpdateRecordParams
  ): Promise<BatchRecordResult>;

  deleteRecord(
    params: DeleteRecordParams
  ): Promise<BatchRecordResult>;

  getSchema(
    params: GetSchemaParams
  ): Promise<DatabaseSchema>;

  uploadImage(
    params: UploadImageParams
  ): Promise<UploadImageResult>;

  onUpdated(
    handler: (event: DatabaseUpdatedEvent) => void
  ): () => boolean;
}
```

除 `onUpdated` 外，所有方法返回 Promise。`onUpdated` 同步返回取消订阅函数。

## 8. 错误

异步方法 reject 的 Error 可能包含：

```typescript
interface DatabaseSdkError extends Error {
  code?:
    | "INVALID_PARAMS"
    | "INVALID_RESPONSE"
    | "RECORD_OPERATION_FAILED"
    | "DATABASE_API_ERROR"
    | "DATABASE_BRIDGE_ERROR"
    | `HTTP_${number}`
    | string;
  details?: unknown;
}
```

`onUpdated` 参数不是函数时同步抛出 code 为 `INVALID_HANDLER` 的 TypeError。
