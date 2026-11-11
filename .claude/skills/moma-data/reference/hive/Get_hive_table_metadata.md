# 获取表的元数据信息

## 指令

```bash
moma moma-data api GET_moma-data_hive_table_metadata --json -q "table_code=xxx"
```

## 指令参数说明

Query 参数（-q key=v&key2=v2）：
  table_code      表名（code），必填
  odin_cluster   Odin 集群：standard | high_confidential，可选，默认 standard

使用示例:

```bash
moma moma-data api GET_moma-data_hive_table_metadata --json -q "table_code=rpt_temp_yezhu_da"
```

## 指令返回数据说明

⚠️ 本接口返回体是**双层 `data`**：表元数据对象在 **`data.data`**（不是 `data`）。

示例数据:

```json
{
    "errno": 0,
    "errmsg": "ok",
    "data": {
        "errno": 0,
        "errmsg": "ok",
        "data": {
            "code": "rpt_all_resblock_info_detail",
            "name": "全量楼盘家装信息明细表",
            "description": "全量楼盘家装信息明细表",
            "db": { "dbId": 123, "dbName": "rpt" },
            "owner": { "name": "王姿茜", "ucid": 1000001 },
            "tableId": 456789,
            "partitionColumn": "pt",
            "clusterType": "default"
        }
    }
}
```

提取 data.data.code，为表的 code 标识（Hive 物理表名），记为：#{data.code}

提取 data.data.name，为表的中文名称，记为：#{data.name}

提取 data.data.description，为表的描述信息，记为：#{data.description}

提取 data.data.db.dbName，为表所属库名，记为：#{data.dbName}

提取 data.data.owner.name，为表负责人姓名，记为：#{data.owner}

提取 data.data.partitionColumn，为分区字段名（常见值为 pt）；仅当上游有分区配置时才有，缺失时回退到列信息里 partitionKey=true 的字段，记为：#{data.partitionColumn}

提取 data.data.tableId，为表的唯一 ID，记为：#{data.tableId}

## 处理说明

errno != 0 时查询失败，将 errmsg 作为失败原因反馈给用户

注意路径是 data.data.xxx（两层 data），不要写成 data.xxx

table_code 需从 /tables 接口返回的 tableList[].code 获取，不可自行构造表名
