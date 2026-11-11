# 奥丁取数预览数据

## 指令

```bash
moma moma-data api POST_moma-data_odin-fetch-skill_preview --json -d '{"request_id":"xxx","creator":"1000000029391704","dateParams":{"occur_date":["20260701000000","20260709235959"]}}'
```

## 指令参数说明

Body 参数（-d JSON 字符串）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request_id | string | 是 | Odin 看板 Request ID，UUID 格式 |
| creator | string | 否 | 操作人 ucid，可不传，优先从 Moma-UserId Header 读取 |
| asset_id | int | 否 | 资产 ID；**从数据资产命中时必填**，传入后使用资产创建人的 ucid 发起查询，避免因当前用户无直接访问权限导致失败 |
| dateParams | object | 否 | 时间/枚举筛选参数，key 为 filterParams[].code，value 为对应值；时间字段传数组 [开始, 结束]，枚举字段也传数组 |


## 使用示例

```bash
# 按时间范围预览
moma moma-data api POST_moma-data_odin-fetch-skill_preview --json -d '{"request_id":"9028b2ee-fb2b-4f46-8646-ed0be054347e","creator":"1000000029391704","dateParams":{"occur_date":["20260701000000","20260709235959"]}}'

# 不传筛选参数
moma moma-data api POST_moma-data_odin-fetch-skill_preview --json -d '{"request_id":"9028b2ee-fb2b-4f46-8646-ed0be054347e","creator":"1000000029391704"}'
```

## 返回数据

```json
{
    "errno": 0,
    "errmsg": "success",
    "data": {
        "headers": ["发生日期", "城市", "订单量"],
        "data": [
            {"发生日期": "20260701000000", "城市": "北京", "订单量": "100"},
            {"发生日期": "20260701000000", "城市": "上海", "订单量": "80"}
        ],
        "page": {
            "pageNo": 1,
            "pageSize": 100,
            "totalCount": 1500,
            "totalPage": 15
        }
    }
}
```

| 字段 | 说明 |
|------|------|
| data.headers | 列名列表（中文），记为 #{headers} |
| data.data | 数据行列表，每行是 {列名: 值} 对象，记为 #{data} |
| data.page.totalCount | 总行数，超过 pageSize 时提示用户总数 |
| data.page.totalPage | 总页数 |

## 处理说明

### 调用前：获取筛选项

预览前先调用 `odin_fetch_filter_params` 获取该 request_id 的可用筛选字段及日期格式，再按格式组装 dateParams。

### 调用后：结果展示

- 默认展示前 100 条，totalCount 超过 pageSize 时提示："共 X 条，当前展示前 100 条"
- 数值以字符串返回，需要计算时做类型转换
- 若 totalCount 很大（>1 万），建议引导用户使用异步下载接口获取全量数据

### dateParams 格式

- 时间字段：传数组 `[开始时间, 结束时间]`，格式与 filterParams[].dateFormat 一致
- 枚举字段：传数组 `["北京", "上海"]`，即使只有一个值也用数组
- 空值字段会被自动忽略，无需传入

### 常见错误

**errno=1 — 数据查询失败**：可能原因：request_id 不存在、当前用户无查看权限、数据扫描量过大。errmsg 会包含具体原因，按提示处理。
