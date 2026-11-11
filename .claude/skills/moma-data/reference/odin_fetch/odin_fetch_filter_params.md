# 根据 request_id 获取奥丁取数筛选项

## 指令

```bash
moma moma-data api POST_moma-data_odin-fetch-skill_filter-params --json -d '{"request_id":"xxx","creator":"100000020205565"}'
```

api_odin-fetch-skill_filter-params
## 指令参数说明

Body 参数（-d JSON 字符串）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request_id | string | 是 | Odin 看板 Request ID，UUID 格式，如 7088b12e-9749-4615-beeb-3bdbf7cf77c3 |
| creator | string | 否 | 操作人 ucid，可不传，优先从 Moma-UserId Header 读取 |

## 使用示例

```bash
moma moma-data api POST_moma-data_odin-fetch-skill_filter-params --json -d '{"request_id":"7088b12e-9749-4615-beeb-3bdbf7cf77c3","creator":"1000000020205565"}'
```

## 返回数据

```json
{
    "errno": 0,
    "errmsg": "success",
    "data": {
        "filterParams": [
            {
                "code": "occur_date",
                "name": "发生日期",
                "dataType": "date",
                "dateFormat": "yyyyMMddHHmmss",
                "dateArrayCnt": 2,
                "defaultValues": []
            },
            {
                "code": "sign_date",
                "name": "签约日期",
                "dataType": "date",
                "dateFormat": "yyyyMMddHHmmss",
                "dateArrayCnt": 1,
                "defaultValues": []
            },
            {
                "code": "city",
                "name": "城市",
                "dataType": "string",
                "defaultValues": [
                    {"code": "北京", "name": "北京"},
                    {"code": "上海", "name": "上海"}
                ]
            }
        ],
        "specialDS": 0
    }
}
```

| 字段 | 说明 |
|------|------|
| data.filterParams | 筛选参数列表，记为 #{filterParams} |
| data.filterParams[].code | 筛选字段代码，用于后续 preview / 下载接口的 dateParams key |
| data.filterParams[].name | 筛选字段中文名 |
| data.filterParams[].dataType | 字段类型：date（日期）/ string（枚举）/ int 等 |
| data.filterParams[].dateFormat | 日期格式，dataType=date 时有效，如 yyyyMMddHHmmss |
| data.filterParams[].dateArrayCnt | 日期数组元素个数：**1=单点时间**（只传一个时间值），**2=时间范围**（传开始+结束两个值）|
| data.filterParams[].defaultValues | 枚举类型的可选值列表 |
| data.specialDS | 高密标志，0=普通数据，>0=高密数据 |

## 处理说明

### 调用时机

在调用预览或异步下载前，先调用本接口获取筛选项，了解该 request_id 支持哪些时间/枚举筛选参数，以及各字段的日期格式要求。

### 日期格式处理

**传参格式统一为 `yyyyMMddHHmmss`**，无论 dateFormat 字段是什么值，传参时一律使用此格式：
- 开始时间 HHmmss 固定为 `000000`
- 结束时间 HHmmss 固定为 `235959`

**根据 `dateArrayCnt` 决定数组长度**：

| dateArrayCnt | 含义 | 传参示例 |
|---|---|---|
| 1 | 单点时间，只传一个值 | `["20260713000000"]` |
| 2 | 时间范围，传开始+结束 | `["20260701000000", "20260713235959"]` |

- dateArrayCnt=1 时，向用户询问具体某一天（或某个时间点）
- dateArrayCnt=2 时，向用户询问开始日期和结束日期

### request_id 格式

request_id 必须是 UUID v4 格式（如 `7088b12e-9749-4615-beeb-3bdbf7cf77c3`），不能是：
- 纯数字
- Odin 报表链接（http://... 或 https://...）

### 常见错误

**errno=1 — 接口返回异常**：检查 request_id 是否正确，确认 Odin 数据源是否已正确配置并加载完毕。
