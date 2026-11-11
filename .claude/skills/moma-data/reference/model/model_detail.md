# 获取数据模型详情及 SQL

> 根据 modelId 获取模型的元信息、原始 SQL 以及可选的解析后 SQL。

## 指令

```bash
moma moma-data api POST_moma-data_odin_model_detail --json -d '{"modelId":12345}'
```

## 指令参数说明

-d modelId:  模型 ID (必传)
-d sqlParse: 是否进行SQL解析、1-是，默认 0 (选传)

指令使用示例：

```bash
moma moma-data api POST_moma-data_odin_model_detail --json \
  -d '{"modelId":12345,"sqlParse":1}'
```

## 返回数据说明

示例数据：

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": {
    "modelId": 12345,
    "modelName": "业绩明细模型",
    "projectId": 678,
    "configType": 0,
    "maintainerId": 26706295,
    "sqlInfo": "SELECT ... FROM rpt_xxx WHERE ...",
    "sqlParseInfo": "SELECT ... FROM rpt_xxx WHERE ...",
    "modelSize": "1.2GB"
  }
}
```

字段说明：

- `sqlInfo`：模型原始 SQL（含占位符）
- `sqlParseInfo`：仅在 `sqlParse=1` 时返回，可直接执行的解析后 SQL
- `modelSize`：模型数据大小（参考用）

当需要查看模型字段定义时请改用 `model_columns.md`；
当需要执行模型取数时请改用 `model_query.md`。
