# 获取数据模型的维度与度量字段

> 根据 modelId 拉取模型可用的字段定义，区分维度（dimension）与度量（measure）。
> 后续 `model_query` 的 `query.dimensions` / `query.measures` 元素结构固定为 `{columnId, alias}`（度量额外含 `agg`），其中
> **`columnId` 取自本接口返回的 `modelColumnId`**、**`alias` 推荐取 `modelColumnName`**。

## 指令

```bash
moma moma-data api POST_moma-data_odin_model_columns --json -d '{"modelId":12345}'
```

## 指令参数说明

-d modelId: 模型 ID (必传)

ucId 由登录上下文自动注入，无需传入。

## 返回数据说明

示例数据：

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": [
    {
      "modelColumnId": 101,
      "modelColumnName": "统计日期",
      "columnType": "dimension",
      "dataType": "string",
      "dataFormat": 0,
      "oColumnInfo": "{\"column_id\":\"282560954\",\"column_code\":\"stat_date\",\"source_format\":\"\",\"column_name\":\"统计日期\",\"data_type\":\"string\",\"is_encryption\":2,\"source_type\":\"string\",\"secret_level\":\"1\",\"table_id\":6214996}",
      "exprType": 0,
      "function": "",
      "functionRely": "",
      "showStatus": 1
    },
    {
      "modelColumnId": 202,
      "modelColumnName": "新签单量",
      "columnType": "measure",
      "dataType": "bigint",
      "dataFormat": 0,
      "oColumnInfo": "{\"column_id\":\"282560955\",\"column_code\":\"new_sign_cnt\",\"source_format\":\"\",\"column_name\":\"新签单量\",\"data_type\":\"bigint\",\"is_encryption\":2,\"source_type\":\"bigint\",\"secret_level\":\"1\",\"table_id\":6214996}",
      "exprType": 2,
      "function": "sum(new_sign_cnt)",
      "functionRely": "new_sign_cnt",
      "showStatus": 1
    }
  ]
}
```

字段说明：

- `modelColumnId`：⚠️ **`model_query` 的 `columnId` 取值来源**（用于 `dimensions[]` / `measures[]` / `filter` 条件节点）；上游 ColumnRef 协议以此为准。
- `modelColumnName`：字段中文名，用于和用户语义匹配；同时**推荐作为 `model_query` 中的 `alias`**（决定结果集列名）。
- `columnType`：`dimension`（维度，用于分组 / 过滤）/ `measure`（度量，用于聚合）。
- `oColumnInfo`：**来源字段元信息，是一段被转义的 JSON 字符串**，需先 `JSON.parse` 反序列化为对象后再取字段。**仅用于辨识字段 / 排查上游报错，不直接作为 query 参数**。结构如下：

  | 内部字段        | 含义                                            | 用途 |
  |-----------------|-------------------------------------------------|------|
  | `column_code`   | 物理列编码（上游内部 SQL 列名）                  | 辅助辨识字段语义；**不是 query 入参** |
  | `column_name`   | 物理列中文名（与 `modelColumnName` 通常一致）    | 仅展示参考 |
  | `data_type`     | 物理列数据类型，如 `string` / `bigint`           | 类型校验 |
  | `column_id`     | 上游字段 ID（与 `modelColumnId` **不同**）       | 追溯排查；**不要**用作 `columnId` |
  | `table_id`      | 所属表 ID                                       | 追溯排查 |
  | `source_type` / `source_format` | 源端类型与格式            | 一般可忽略 |
  | `is_encryption` / `secret_level` | 加密标记与密级               | 高密模型相关元信息 |

- `exprType`：0-非表达式 / 1-表达式 / 2-含聚合函数表达式
- `showStatus`：0-隐藏 / 1-显示，**构造查询时只使用 `showStatus=1` 的字段**

字段匹配建议（面向 `model_query` 的下游用法）：

1. 优先用 `modelColumnName` 匹配用户自然语言（如"统计日期"、"新签单量"）。
2. 构造 `model_query` 的 `dimensions[]` / `measures[]` / `filter` 条件节点时：
   - **`columnId` = 本接口的 `modelColumnId`**（⚠️ 不是 `oColumnInfo.column_id`，也不是 `oColumnInfo.column_code`）；
   - **`alias` = 本接口的 `modelColumnName`**（决定结果集列名）；
   - `measure` 字段若需聚合，元素额外带 `agg`（可选 `SUM/AVG/COUNT/COUNT_DISTINCT/MAX/MIN/NONE`）；若用户想看明细，**把 measure 平移到 `dimensions` 且保持 `measures: []`**（见 model_query.md「度量作为维度」章节）。
3. `oColumnInfo` 是 JSON 字符串，需 `JSON.parse` 后使用；**不要**做字符串切分（如按冒号切），**不要**把 `column_code` 或 `column_id` 塞进 query。
4. 当用户描述无法精准映射到字段时，通过 AskUserQuestion 与用户确认。
