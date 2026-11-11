# 奥丁取数获取异步下载结果

## 说明

本接口用于查询 Odin 异步下载任务的执行状态。**在 odinchart 工具的同步流程中，该接口由后台服务自动调用（轮询），通常不需要手动调用。** 仅在需要直接查询某个 taskId 状态时使用。

底层调用 Odin 接口：`odin_chart_query_api_asyn_download`

## 鉴权方式

与其他奥丁取数接口相同，使用 appkey + secret + ts 生成 MD5 签名：

```
sign = MD5("appkey={appkey}&secret={secret}&ts={ts}")
```

请求头：
- `ucid`: 操作人 ucid
- `appkey`: ke-moma-apps
- `ts`: 当前时间戳（毫秒）
- `sign`: MD5 签名
- `secret`: 固定密钥

## 接口参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| taskId | int | 是 | 异步任务 ID，由提交异步下载任务时返回 |

## 返回数据

```json
{
    "code": 1,
    "msg": "success",
    "data": {
        "taskId": 59072491,
        "status": 2,
        "fileUrl": "http://xxx.xxx/download/xxx.csv"
    }
}
```

| 字段 | 说明 |
|------|------|
| data.taskId | 任务 ID |
| data.status | 任务状态：0=待处理，1=进行中，2=完成，3=失败 |
| data.fileUrl | status=2 时有值，CSV 文件下载地址 |

## 处理说明

### 轮询策略

后台服务收到 taskId 后，按如下策略轮询：
- 每 3~5 秒查询一次状态
- status=2 时下载 fileUrl 对应的 CSV 文件
- status=3 时报错终止
- 超过最大等待时间（约 10 分钟）仍未完成则超时失败

### status=2 后的处理

1. 从 fileUrl 下载 CSV 文件（UTF-8 编码）
2. 解析 CSV，第一行为列名（中文），后续为数据行

### 与异步提交接口的关系

`odin_fetch_async_download`（提交任务）→ 返回 taskId → 本接口轮询状态 → status=2 → 下载 fileUrl → 解析 CSV 数据

小数据量时，提交接口会直接返回数据（`type=data`），跳过本轮询流程。
