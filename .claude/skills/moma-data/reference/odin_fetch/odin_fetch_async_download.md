# 奥丁取数异步下载（Skill 专用全量取数）

## 指令

```bash
# Skill 专用：全量取数
moma moma-data api POST_moma-data_odin-fetch-skill_fetch --json -d '{"request_id":"xxx","creator":"1000000030606732","dateParams":{"网签时间":["20260701000000","20260712235959"]}}'
```

## 接口说明

**本接口为 Skill 专用**，与 `/api/odin-chart/request/sync` 的区别：

| | `/api/odin-fetch-skill/fetch`（本接口） | `/api/odin-chart/request/sync` |
|---|---|---|
| 用途 | Skill 取数，直接返回数据 | 写入 Supabase，供前端展示 |
| 返回 | 全量 headers + list | 任务已提交（后台执行） |
| 必填参数 | request_id（creator 可选，从 Header 读取） | request_id、creator、chatId、tableName |
| 阻塞 | 是（等待下载完成才返回） | 否（立即返回，后台执行） |

内部流程：
1. 调用 Odin `odin_data_query_api_async` 提交异步下载任务
2. 每 5 秒轮询一次，直到 status=2（完成）
3. 下载 CSV 文件并解析，返回全量数据

## 指令参数说明

Body 参数（-d JSON 字符串）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request_id | string | 是 | Odin 看板 Request ID，UUID 格式 |
| creator | string | 否 | 操作人 ucid，可不传，优先从 Moma-UserId Header 读取 |
| asset_id | int | 否 | 资产 ID；**从数据资产命中时必填**，传入后使用资产创建人的 ucid 发起查询，避免因当前用户无直接访问权限导致失败 |
| dateParams | object | 否 | 时间/枚举筛选参数，key 为 filterParams[].code，value 为数组 |

## 使用示例

```bash
# 不带时间筛选
moma moma-data api POST_moma-data_odin-fetch-skill_fetch --json -d '{"request_id":"76e5e256-93e0-43a2-bd69-d4117286104a","creator":"1000000030606732"}'

# 带时间筛选（dateFormat=yyyyMMddHHmmss）
moma moma-data api POST_moma-data_odin-fetch-skill_fetch --json -d '{"request_id":"410384f5-af96-473e-9fc1-ec17abdc9143","creator":"1000000030606732","dateParams":{"网签时间":["20260701000000","20260712235959"]}}'
```

## 返回数据

```json
{
    "errno": 0,
    "errmsg": "success",
    "data": {
        "headers": ["week", "total_count"],
        "list": [
            {"week": "2026-19", "total_count": 4561},
            {"week": "2026-20", "total_count": 3605}
        ],
        "total": 11
    }
}
```

| 字段 | 说明 |
|------|------|
| data.headers | 列名列表 |
| data.list | 全量数据行，每行是 {列名: 值} 对象 |
| data.total | 总行数 |

## 处理说明

### dateParams 格式

与预览接口完全一致，时间字段传 `[开始, 结束]` 数组，枚举字段传值数组，空字段自动忽略。

### 常见错误

**errno=1 — 异步下载任务失败**：Odin 侧任务执行失败（status=3），可重试。

**errno=1 — 异步下载任务超时**：轮询 60 次（约 5 分钟）仍未完成，数据量过大或 Odin 侧异常。
