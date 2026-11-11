# 获取指标纬度对应的枚举值

## 指令

```bash
moma moma-data api POST_moma-data_index_dims_enum --json -d '{"indexIds":"25667","dimTableCode":"dim_coo_leadercockpit_dimension_da","dimCode":"area_name","pageSize":1000}'
```

## 指令参数说明

请求体（-d JSON，所有字段合并为一个 JSON 字符串）：
  indexIds      指标ID，多个用逗号分隔，如 25667,120849 (必传)
  dimTableCode  枚举表名，与获取指标公共纬度接口对应 (必传)
  dimCode       枚举字段，与获取指标公共纬度接口对应 (必传)
  parentDimCode 上级维度字段 (选传)
  pageSize      分页大小，默认1000 (选传)
  filter        枚举值过滤条件，JSON 对象 (选传)

使用示例：

```bash
moma moma-data api POST_moma-data_index_dims_enum --json \
  -d '{"indexIds":"25667","dimTableCode":"dim_coo_leadercockpit_dimension_da","dimCode":"area_name","pageSize":1000}'
```

## 返回数据说明

```json
  {
      "errno": 0,
      "errmsg": "ok",
      "data": {
          "list": [
              {
                  "code": "-911",
                  "name": "ALL"
              },
              {
                  "code": "420100",
                  "name": "武汉"
              },
              {
                  "code": "310000",
                  "name": "上海"
              }
          ],
          "totalCount": 100
      }
  }
```
