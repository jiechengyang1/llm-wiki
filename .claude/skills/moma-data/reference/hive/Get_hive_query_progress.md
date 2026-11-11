# 异步查询结果查询（任务执行进度）

## 指令

```bash
moma moma-data api GET_moma-data_hive_query_progress --json -q "queryId=123456"
```

## 指令参数说明

Query 参数（-q key=v&key2=v2）：
  queryId        即席查询任务 ID（由 execute-sql 返回的 data.queryId），必填
  odin_cluster   Odin 集群：standard | high_confidential，可选，默认 standard

使用示例:

```bash
# 普通集群
moma moma-data api GET_moma-data_hive_query_progress --json -q "queryId=123456"

# 高密集群
moma moma-data api GET_moma-data_hive_query_progress --json -q "queryId=123456&odin_cluster=high_confidential"
```

## 指令返回数据说明

示例数据（data 段为上游进度原文）：

```json
{
    "errno": 0,
    "errmsg": "ok",
    "data": {
        "errno": 0,
        "data": {
            "queryId": 123456,
            "queryStatus": "FINISHED",
            "warn": null
        }
    }
}
```

提取 data.data.queryStatus，为任务执行状态，记为：#{query_status}

提取 data.data.warn，为查询告警信息，非空时需提示用户，记为：#{warn}

## 处理说明

- 本接口用于轮询 execute-sql 提交后的异步任务状态。queryStatus 常见取值：执行中（RUNNING/QUEUED 等）/ 完成（FINISHED）/ 失败（FAILED）。
- 轮询到任务完成（FINISHED）后，再调用 GET_moma-data_hive_download 下载查询结果数据。
- 外层 errno != 0 时进度查询失败，将 errmsg 作为失败原因反馈给用户。
- queryId 必须来自 execute-sql 返回的 data.queryId，不可自行构造。
- 高密集群查询时，odin_cluster 需与 execute-sql 提交时保持一致。
