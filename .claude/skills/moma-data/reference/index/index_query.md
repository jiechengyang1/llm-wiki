# 通过指标api获取数据标准流程

## 指令

从资产命中时在同一条指令里带上 `asset_id`：

```bash
moma moma-data api POST_moma-data_index_query --json -d '{"targets":"25667,120849","asset_id":821,"params":{"pageNo":1,"pageSize":10,"startDate":"20260601","endDate":"20260625","dateType":1,"dim":"performance_city_code"}}'
```

不是从资产来的查询不传 `asset_id`：

```bash
moma moma-data api POST_moma-data_index_query --json -d '{"targets":"25667,120849","params":{"pageNo":1,"pageSize":10,"startDate":"20260601","endDate":"20260625","dateType":1,"dim":"performance_city_code"}}'
```

**⚠️ 不要自己按 20/10 切批**：本接口服务端已内置分片(每片≤20)+按 dim 键的外连接合并+重试+熔断，
AI 侧**一次性把所有 targets(建议上限 100)传进来**即可拿到完整合并结果。自行分批多次调用
会因合并策略差异导致同 dim 组合的行错位、指标值缺失(相当于把 outer-join 变成按下标顺序拼)。

## 指令参数说明

请求体（-d JSON，所有字段合并为一个 JSON 字符串）：
  targets           待查询的指标ID，多个用逗号分隔，**单次上限 100**(≤20 直查,>20 服务端自动分片合并) (必填)
  asset_id          资产 ID。从资产命中时必填，传入后使用资产创建人的 ucid 发起查询，避免因当前用户无直接访问权限导致失败。不是从资产来的查询不传
  params.startDate  起始日期，格式 YYYYMMDD (必填)
  params.endDate    结束日期，格式 YYYYMMDD (必填)
  params.dateType   时间周期：日=1、周=2、月=3、季=5、年=6 (必填)
  params.dim        聚合维度，多个逗号分隔；dateType=1含date/2含sun_dt/3含month/5含quarter/6含year (必填)
  params.pageNo     页码，默认1 (选填)
  params.pageSize   每页数据量，默认1000，最大2000 (选填)
  params.filter     过滤条件，JSON 对象 (选填)

使用示例:

```bash
moma moma-data api POST_moma-data_index_query --json \
  -d '{"targets":"25667,120849","params":{"pageNo":1,"pageSize":10,"startDate":"20260601","endDate":"20260625","dateType":1,"dim":"performance_city_code","filter":{"type":"and","fields":[{"type":"in","dimension":"battle_region_code","values":["BKNJQY8888"]}]}}}'
```

## 返回数据

⚠️ 本接口返回体是**双层 `data`**：外层是 CLI 网关信封，中间层是上游指标 v2 业务信封（errno 为字符串 `"0"`），真正的数据（list / mapping 等）在 **`data.data`**（不是 `data`）。

```json
{
    "errno": 0,
    "errmsg": "ok",
    "data": {
        "errno": "0",
        "errmsg": "success",
        "data": {
            "list": [
                { "date": "20251219", "city_abbr_name": "株洲", "city_code": "430200", "omc_ershoumaimaishangjizhuanhuachengjiaodanliang": "3" },
                { "date": "20260101", "city_abbr_name": "苏州", "city_code": "320500", "omc_ershoumaimaishangjizhuanhuachengjiaodanliang": "70" }
            ],
            "mapping": {
                "date": "日期",
                "city_code": "编码",
                "city_abbr_name": "",
                "omc_ershoumaimaishangjizhuanhuachengjiaodanliang": "二手线上成交单量"
            },
            "codeMapping": { "city_code": "city_abbr_name" },
            "aggregateData": { "sum": {}, "avg": {}, "max": {}, "min": {}, "summary": {} },
            "pageNo": 1,
            "pageSize": 10,
            "totalCount": 20000,
            "totalPage": 2000
        },
        "cache": null
    }
}
```

提取 **data.data** 记为指标请求的数据载体（注意两层 data），记为: #{payload}

提取 data.data.list，为指标请求要向前端展示的数据，记为：#{data}

提取 data.data.mapping，为英文列名→中文名映射，记为：#{mapping}（注意个别字段中文名可能为空串，如 city_abbr_name，展示时回退用英文名或 codeMapping）

提取 data.data.codeMapping，为编码列→名称列的对应（如 city_code→city_abbr_name）

分页在 data.data.pageNo / pageSize / totalCount / totalPage

## 处理说明

**取错层级是本接口最常见的坑**：正确路径是 `data.data.list` / `data.data.mapping`，不要写成 `data.list`；另需判中间层业务 errno（`data.errno` 为字符串 `"0"` 才成功）。

#{mapping}的数据中，存在如：{"omc_ershouchunxinqiandanliang": "OMC_二手新签单量"}、{"kaohekoujingzaiguanfangyuanliang": "考核口径再管房源量"}的映射关系





