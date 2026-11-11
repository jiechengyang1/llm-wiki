# 获取指标的公共纬度

## 指令

```bash
moma moma-data api GET_moma-data_index_dims --json -q "indexIds=25667"
```

## 指令参数说明

Query 参数（-q key=v&key2=v2）：
  indexIds         指标ID，多个用逗号分隔，如: 25667,120849 (必传)
  showMultiHieDim  展示多层级维度，true/false，默认 false (选传)

使用示例:

```bash
moma moma-data api GET_moma-data_index_dims --json -q "indexIds=25667,120849"
```

## 指令返回数据说明

示例数据:

```json
{
  "errno": 0,
  "errmsg": "ok",
  "data": {
    "dimGroups": [
      [
        {
          "dimName": "区域",
          "dimCode": "battle_region_code",
          "dimTableCode": "dim_coo_leadercockpit_dimension_da",
          "hierarchyDimName": "贝联_区域",
          "level": 1,
          "levelName": "区域",
          "next": {
            "dimName": "业城",
            "dimCode": "performance_city_code",
            "dimTableCode": "dim_coo_leadercockpit_dimension_da",
            "hierarchyDimName": "贝联_区域",
            "level": 2,
            "levelName": "业城",
            "next": {
              "dimName": "地城",
              "dimCode": "city_code",
              "dimTableCode": "dim_coo_leadercockpit_dimension_da",
              "hierarchyDimName": "贝联_区域",
              "level": 3,
              "levelName": "地城",
              "next": {
                "dimName": "事业部",
                "dimCode": "corp_code",
                "dimTableCode": "dim_ref_shop_director_role_relation_da",
                "hierarchyDimName": "贝联_区域",
                "level": 4,
                "levelName": "事业部",
                "next": {
                  "dimName": "大部",
                  "dimCode": "marketing_code",
                  "dimTableCode": "dim_ref_shop_director_role_relation_da",
                  "hierarchyDimName": "贝联_区域",
                  "level": 5,
                  "levelName": "大部",
                  "next": {
                    "dimName": "大区",
                    "dimCode": "area_code",
                    "dimTableCode": "dim_ref_shop_director_role_relation_da",
                    "hierarchyDimName": "贝联_区域",
                    "level": 6,
                    "levelName": "大区",
                    "next": {
                      "dimName": "CA",
                      "dimCode": "shop_director_code",
                      "dimTableCode": "dim_ref_shop_director_role_relation_da",
                      "hierarchyDimName": "贝联_区域",
                      "level": 7,
                      "levelName": "CA",
                      "next": {
                        "dimName": "考核赋能区域",
                        "dimCode": "assess_ca_empower_region_name",
                        "dimTableCode": "dim_ref_shop_director_role_relation_da",
                        "hierarchyDimName": "贝联_区域",
                        "level": 8,
                        "levelName": "考核赋能区域",
                        "next": {
                          "dimName": "考核商圈",
                          "dimCode": "assess_region_code",
                          "dimTableCode": "dim_ref_shop_director_role_relation_da",
                          "hierarchyDimName": "贝联_区域",
                          "level": 9,
                          "levelName": "考核商圈",
                          "next": {
                            "dimName": "门店",
                            "dimCode": "shop_code",
                            "dimTableCode": "dim_ref_shop_director_role_relation_da",
                            "hierarchyDimName": "贝联_区域",
                            "level": 10,
                            "levelName": "门店"
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      ],
      [
        {
          "dimName": "区域名",
          "dimCode": "battle_region_abbr_name",
          "dimTableCode": "dim_coo_leadercockpit_dimension_da",
          "hierarchyDimName": "贝联_区域名",
          "level": 1,
          "levelName": "区域名",
          "next": {
            "dimName": "业城名",
            "dimCode": "performance_city_abbr_name",
            "dimTableCode": "dim_coo_leadercockpit_dimension_da",
            "hierarchyDimName": "贝联_区域名",
            "level": 2,
            "levelName": "业城名",
            "next": {
              "dimName": "地城名",
              "dimCode": "city_abbr_name",
              "dimTableCode": "dim_coo_leadercockpit_dimension_da",
              "hierarchyDimName": "贝联_区域名",
              "level": 3,
              "levelName": "地城名",
              "next": {
                "dimName": "事业部名",
                "dimCode": "corp_name",
                "dimTableCode": "dim_ref_shop_director_role_relation_da",
                "hierarchyDimName": "贝联_区域名",
                "level": 4,
                "levelName": "事业部名",
                "next": {
                  "dimName": "大部名",
                  "dimCode": "marketing_name",
                  "dimTableCode": "dim_ref_shop_director_role_relation_da",
                  "hierarchyDimName": "贝联_区域名",
                  "level": 5,
                  "levelName": "大部名",
                  "next": {
                    "dimName": "大区名",
                    "dimCode": "area_name",
                    "dimTableCode": "dim_ref_shop_director_role_relation_da",
                    "hierarchyDimName": "贝联_区域名",
                    "level": 6,
                    "levelName": "大区名",
                    "next": {
                      "dimName": "CA名",
                      "dimCode": "shop_director_name",
                      "dimTableCode": "dim_ref_shop_director_role_relation_da",
                      "hierarchyDimName": "贝联_区域名",
                      "level": 7,
                      "levelName": "CA名",
                      "next": {
                        "dimName": "考核商圈名",
                        "dimCode": "assess_region_name",
                        "dimTableCode": "dim_ref_shop_director_role_relation_da",
                        "hierarchyDimName": "贝联_区域名",
                        "level": 8,
                        "levelName": "考核商圈名",
                        "next": {
                          "dimName": "门店名",
                          "dimCode": "shop_name",
                          "dimTableCode": "dim_ref_shop_director_role_relation_da",
                          "hierarchyDimName": "贝联_区域名",
                          "level": 9,
                          "levelName": "门店名"
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      ],
      [
        {
          "dimName": "品牌",
          "dimCode": "brand_code",
          "dimTableCode": "dim_coo_leadercockpit_dimension_da",
          "hierarchyDimName": "品牌",
          "level": 1,
          "levelName": "品牌",
          "next": {
            "dimName": "子品牌编码",
            "dimCode": "sub_brand_code",
            "dimTableCode": "dim_ref_shop_director_role_relation_da",
            "hierarchyDimName": "品牌",
            "level": 2,
            "levelName": "子品牌编码"
          }
        }
      ],
      [
        {
          "dimName": "品牌名",
          "dimCode": "brand_name",
          "dimTableCode": "dim_coo_leadercockpit_dimension_da",
          "hierarchyDimName": "品牌名",
          "level": 1,
          "levelName": "品牌名",
          "next": {
            "dimName": "子品牌名称",
            "dimCode": "sub_brand_name",
            "dimTableCode": "dim_ref_shop_director_role_relation_da",
            "hierarchyDimName": "品牌名",
            "level": 2,
            "levelName": "子品牌名称"
          }
        }
      ]
    ]
  }
}
```

dimName: 纬度名 (用于确定用户是否需要使用该纬度)  
dimCode: 纬度的字段名 (与dim_enum结合使用) 
dimTableCode: 纬度字段对应的表名 (与dim_enum结合使用) 
next:    表示纬度之前存在父子间关系


