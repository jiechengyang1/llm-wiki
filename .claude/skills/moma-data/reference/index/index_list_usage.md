# 获取用户有权限的指标列表

## 指令

```bash
moma moma-data api GET_moma-data_index_metric-list --json -q "page_no=1&page_size=500"
```

## 指令参数说明

Query 参数（-q key=v&key2=v2）：
  page_no               页码 (必填)
  page_size             分页大小，最大500，建议固定使用500 (必填)
  word                  指标名搜索关键字 (选填)
  authentication_status 认证状态：1-已认证 2-认证中 3-未认证 4-撤销中 (选填)
  filter_index_list     过滤指标 ID 列表，逗号分隔 (选填)

## 返回数据

示例数据:

```json
{
    "errno": 0,
    "errmsg": "ok",
    "data": {
        "metrics": [
            {
                "id": "5431",
                "name": "贝壳用户数(uv)_贝壳增长_日(贝壳用户数(uv))",
                "indexLevel": 1,
                "authenticationStatus": 3,
                "cooRuleId": 0,
                "calculateCaliber": "device_id",
                "definition": "UV是unique visitor的简写，是指通过互联网访问、浏览这个网页的自然人。APP一般使用手机设备id作为用户的唯一id，M站和PC站通常采用cookie作为用户的唯一id。"
            },
            {
                "id": "6911",
                "name": "线下带看量_人店_日(带看量_集团)",
                "indexLevel": 2,
                "authenticationStatus": 1,
                "cooRuleId": 1,
                "calculateCaliber": "select showing_start_date,SUM(showing_cnt)\nfrom olap.olap_asm_show_agent_showing_cnt_indicator_da\nwhere pt = '${-1d_pt}'\ngroup by showing_start_date",
                "definition": "衡量经纪人每天产生的线下带看数量"
            }
        ],
        "pageNo": 1,
        "pageSize": 2,
        "totalCount": 4462,
        "hasMore": true
    }
}
```

## 返回字段说明

| 字段                  | 说明                                                                 |
|-----------------------|----------------------------------------------------------------------|
| `id`                  | 指标 ID，后续查询时作为 `targets` 参数使用                           |
| `name`                | 指标名称                                                             |
| `indexLevel`          | 指标等级：3-集团级 / 2-条线级 / 4-部门级 / 1-普通级，匹配优先级 3>2>4>1 |
| `authenticationStatus`| 认证状态：1-已认证 / 2-认证中 / 3-未认证 / 4-撤销中，匹配优先级 1>2>3>4 |
| `cooRuleId`           | 同环比规则：1-月同期 / 2-整月 / 3-月初                               |
| `calculateCaliber`    | 指标口径，描述指标的统计规则；内容形态不固定，可能是简短标识（如 `device_id`）、文字描述、SQL 语句或 `-`，可能为空字符串 |
| `definition`          | 指标说明，描述指标的业务含义，可能为空字符串                          |
| `pageNo`              | 当前页码                                                             |
| `pageSize`            | 每页条数                                                             |
| `totalCount`          | 指标总数                                                             |
| `hasMore`             | 是否还有下一页，`true` 时需继续翻页获取全量数据                       |
