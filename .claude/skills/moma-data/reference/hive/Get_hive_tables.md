# 获取用户有权限的表(分页接口)

## 指令

```bash
moma moma-data api GET_moma-data_hive_tables --json -q "page_no=1&page_size=10"
```

## 指令参数说明

Query 参数（-q key=v&key2=v2）：
  page_no        页码，默认为 1，必填
  page_size      每页大小，默认为 20，必填
  keywords       表名关键词，支持模糊检索，可选
  odin_cluster   Odin 集群：standard | high_confidential，可选，默认 standard

使用示例:

```bash
moma moma-data api GET_moma-data_hive_tables --json -q "page_no=1&page_size=10"
```

## 指令返回数据说明

示例数据:

```json
{
    "errno": 0,
    "errmsg": "ok",
    "data": {
        "totalNum": 126,
        "currentPage": 1,
        "pageSize": 10,
        "tableList": [
            {
                "code": "rpt_temp_yezhu_da",
                "name": "业主-符合要求房源与用户全量表",
                "description": "hhhh测试表",
                "db": {
                    "dbId": 3,
                    "dbName": "rpt"
                },
                "owner": {
                    "name": "曹丹枫【caodanfeng002@ke.com】",
                    "ucid": 1000000026740591
                },
                "tableId": 6661596
            },
            {
                "code": "rpt_all_resblock_info_detail",
                "name": "全量楼盘家装信息明细表",
                "description": "全量楼盘家装信息明细表",
                "db": {
                    "dbId": 3,
                    "dbName": "rpt"
                },
                "owner": {
                    "name": "王姿茜【wangziqian010@ke.com】",
                    "ucid": 1000000031102848
                },
                "tableId": 6660812
            },
            {
                "code": "rpt_bsm_ba_pay_new_trans_indicator_di",
                "name": "战略集市-经营日报-付费拉新转化指标表",
                "description": "【表用途】：对外输出\n【业务过程】：经营日报付费拉新转化指标表，包含统计日期、时间类型、城市信息、业务线信息、平台、端，用于计算付费拉新商机转化指标\n【表粒度】：date_type ,city_code ,city_name ,business_code ,business_name ,site ,dp\n【分区范围】：20260624-至今",
                "db": {
                    "dbId": 3,
                    "dbName": "rpt"
                },
                "owner": {
                    "name": "卓宝臻【zhuobaozhen001@ke.com】",
                    "ucid": 1000000026724666
                },
                "tableId": 6642349
            },
            {
                "code": "olap_dau_user_seg_da",
                "name": "dau_用户来源拆解",
                "description": "hhhh",
                "db": {
                    "dbId": 5,
                    "dbName": "olap"
                },
                "owner": {
                    "name": "曹丹枫(26740591)",
                    "ucid": 1000000026740591
                },
                "tableId": 6634105
            },
            {
                "code": "dim_ref_new_user_pay_di",
                "name": "参照维-新增用户付费参照维表",
                "description": "表用途：公共模型\n业务过程：新增用户付费参照维表，用于计算新增用户付费指标使用\n表粒度：duid\n分区范围：20260621-至今",
                "db": {
                    "dbId": 6,
                    "dbName": "dim"
                },
                "owner": {
                    "name": "卓宝臻【zhuobaozhen001@ke.com】",
                    "ucid": 1000000026724666
                },
                "tableId": 6626822
            },
            {
                "code": "ods_plat_prd_online_agentic_metric_data_source_da",
                "name": "指标数据源配置表",
                "description": "https://ones.ke.com/project/orders/1/detail/102770?currentKey=%23basic",
                "db": {
                    "dbId": 7,
                    "dbName": "ods"
                },
                "owner": {
                    "name": "董家齐(29361950)",
                    "ucid": 1000000029361950
                },
                "tableId": 6602583
            },
            {
                "code": "ods_plat_prd_online_agentic_hive_sql_data_source_da",
                "name": "hive数据源配置表",
                "description": "https://ones.ke.com/project/orders/1/detail/102770?currentKey=%23basic",
                "db": {
                    "dbId": 7,
                    "dbName": "ods"
                },
                "owner": {
                    "name": "董家齐(29361950)",
                    "ucid": 1000000029361950
                },
                "tableId": 6602536
            },
            {
                "code": "olap_alm_osu_housedel_anzhu_scale_deal_city_indicator_di",
                "name": "事务线集市-业主服务升级-房源-安住规模与成交指标表",
                "description": "【表用途】：对外输出 【业务过程】：事务线集市-业主服务升级-房源-安住规模与成交指标表，包含大盘及安住的在售业主量、在售房源量、成交、核销、带看、去化周期、挂牌天数等规模与效率指标，用于安住产品核心监控分析及战略日报。 【表粒度】：stat_date, statistical_code, statistical_name, city_code, city_name 【分区范围】：20260521-至今",
                "db": {
                    "dbId": 5,
                    "dbName": "olap"
                },
                "owner": {
                    "name": "王云娜【wangyunna002@ke.com】",
                    "ucid": 1000000030995132
                },
                "tableId": 6602137
            },
            {
                "code": "rpt_bsm_osu_anzhu_indicator_di",
                "name": "业主服务升级-安住-指标表",
                "description": "【表用途】：对外输出 【业务过程】：业主服务升级-安住核心指标表，包含大盘及安住的在售业主量、在售房源量、成交、核销、带看、去化周期、挂牌天数等规模与效率指标，用于安住产品核心监控分析及战略日报。 【表粒度】：stat_date, statistical_code, statistical_name, city_code, city_name 【分区范围】：20260521-至今",
                "db": {
                    "dbId": 3,
                    "dbName": "rpt"
                },
                "owner": {
                    "name": "王云娜【wangyunna002@ke.com】",
                    "ucid": 1000000030995132
                },
                "tableId": 6600995
            },
            {
                "code": "rpt_bsm_ba_cdel_bl_stock_custdel_di",
                "name": "战略集市-经营分析-客源-北链库存客源指标表",
                "description": "【表用途】：战略集市-北链客源库存指标表 ； 【业务场景】：天维度带看客源相关指标数据 【表粒度】：stat_date+city_code+shop_code+agent_ucid； 【数据范围】：25年1月至今；【分区范围】：。\n",
                "db": {
                    "dbId": 3,
                    "dbName": "rpt"
                },
                "owner": {
                    "name": "李翱【liao029@ke.com】",
                    "ucid": 1000000029161802
                },
                "tableId": 6589917
            }
        ]
    }
}
```
totalNum 总数

