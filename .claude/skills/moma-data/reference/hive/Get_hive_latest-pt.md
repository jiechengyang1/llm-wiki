# 获取指定表最新的 n 个分区

## 指令

```bash
moma moma-data api GET_moma-data_hive_latest-pt --json -q "table_code=rpt_xxx&n=3"
```

## 指令参数说明

Query 参数（-q key=v&key2=v2）：
  table_code 表的物理 code（即 #{table_code} 的值），必填
  n          返回最新 n 个分区，默认 1，必填

使用示例:

```bash
moma moma-data api GET_moma-data_hive_latest-pt --json -q "table_code=rpt_temp_yezhu_da&n=3"
```

## 指令返回数据说明

示例数据:

```json
{
    "errno": 0,
    "errmsg": "ok",
    "data": {
        "pts": [
            {
                "pt": "20260628",
                "createTime": "2026-06-29 02:30:00"
            },
            {
                "pt": "20260627",
                "createTime": "2026-06-28 02:30:00"
            },
            {
                "pt": "20260626",
                "createTime": "2026-06-27 02:30:00"
            }
        ]
    }
}
```

提取 data.pts，为分区列表，每个分区含 pt（分区值）和 createTime（创建时间），记为：#{data.pts}

提取 data.pts[0].pt，为最新分区值（格式 yyyyMMdd），记为：#{latest_pt}

## 处理说明

errno != 0 时查询失败，将 errmsg 作为失败原因反馈给用户

table 需从 /tables 接口返回的 tableList[].code 获取，不可自行构造表名

分区值（pt）通常为日期格式 yyyyMMdd，在构造 SQL WHERE 条件时可直接使用，如 `WHERE pt = '20260628'`

获取最新分区后，可将其作为 execute-sql 中 SQL 的分区过滤条件，确保查询数据为最新分区
