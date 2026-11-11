# 获取表的列信息

## 指令

```bash
moma moma-data api GET_moma-data_hive_table_columns --json -q "table_code=xxx"
```

## 指令参数说明

Query 参数（-q key=v&key2=v2）：
  table_code      表名（code），必填
  odin_cluster   Odin 集群：standard | high_confidential，可选，默认 standard

使用示例:

```bash
moma moma-data api GET_moma-data_hive_table_columns --json -q "table_code=rpt_temp_yezhu_da"
```

## 指令返回数据说明

⚠️ 本接口返回体是**双层 `data`**：列数组在 **`data.data`**（不是 `data`）。

示例数据:

```json
{
    "errno": 0,
    "errmsg": "ok",
    "data": {
        "errno": 0,
        "errmsg": "ok",
        "data": [
            {
                "name": "pt",
                "dataType": "string",
                "comment": "hive分区标识",
                "nameInChinese": "分区字段",
                "defaultValue": null,
                "nullable": 1,
                "partitionKey": true,
                "primaryKey": true,
                "encrypted": false,
                "enumValue": [],
                "metaCode": "pt"
            },
            {
                "name": "stat_month",
                "dataType": "string",
                "comment": "",
                "nameInChinese": "年月",
                "defaultValue": null,
                "nullable": 1,
                "partitionKey": false,
                "primaryKey": true,
                "encrypted": false,
                "enumValue": [],
                "metaCode": "stat_month"
            },
            {
                "name": "resblock_name",
                "dataType": "string",
                "comment": "",
                "nameInChinese": "楼盘名称",
                "defaultValue": null,
                "nullable": 1,
                "partitionKey": false,
                "primaryKey": true,
                "encrypted": false,
                "enumValue": [],
                "metaCode": "resblock_name"
            }
        ]
    }
}
```

提取 **data.data** 数组（注意两层 data），为表的列信息列表，每列包含以下字段，记为：#{data.columns}

提取每列的 name，为 Hive 物理字段名（SELECT 可用），记为：#{col.name}

提取每列的 dataType，为字段数据类型（如 string、int、bigint），记为：#{col.dataType}

提取每列的 comment，为字段注释说明；为空时可用 nameInChinese（中文名）辅助辨识，记为：#{col.comment}

提取每列的 partitionKey，为 true 表示该列为分区字段，记为：#{col.partitionKey}

提取每列的 primaryKey，为 true 表示该列为主键，记为：#{col.primaryKey}

## 处理说明

errno != 0 时查询失败，将 errmsg 作为失败原因反馈给用户

table_code 需从 /tables 接口返回的 tableList[].code 获取，不可自行构造表名

分区字段（partitionKey=true）在 WHERE 条件中必须指定值或范围，否则全表扫描可能导致查询超时

data.data 中的 dataType 为 Hive 类型，编写 SQL 时注意类型匹配；数值字段的值通常以字符串返回，做汇总/计算时需注意类型转换
