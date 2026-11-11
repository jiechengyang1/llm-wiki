# 通过 Hive 即席 SQL 执行查询

## 指令

```bash
# 命中资产：asset_id 必带。意图 A（复用 raw_sql）和意图 B（自造 SQL）都走这条
moma moma-data api POST_moma-data_hive_execute-sql --json -d '{"sql":"SELECT ...","asset_id":821}'

# 未命中任何资产的裸 SQL：不传 asset_id
moma moma-data api POST_moma-data_hive_execute-sql --json -d '{"sql":"SELECT ..."}'
```

## 指令参数说明

Body 参数（-d JSON 字符串）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sql | string | 是 | 要执行的 SQL 查询语句，标准 HiveQL |
| odin_cluster | string | 否 | Odin 集群：standard（普通）/ high_confidential（高密），默认 standard |
| asset_id | int | 从资产命中时必填 | 资产 ID。传入后使用资产创建人的 ucid 发起查询，避免因当前用户无直接表权限导致失败。不是从资产来的 SQL 不传 |

## 使用示例

```bash
# 命中资产（取数或探查都带 asset_id）
moma moma-data api POST_moma-data_hive_execute-sql --json -d '{"sql":"SELECT * FROM rpt.rpt_xxx WHERE pt = '\''20260625'\'' LIMIT 10","asset_id":821}'

# 未命中资产的裸查询
moma moma-data api POST_moma-data_hive_execute-sql --json -d '{"sql":"SELECT * FROM rpt.rpt_xxx WHERE pt = '\''20260625'\'' LIMIT 10"}'

# 高密集群查询
moma moma-data api POST_moma-data_hive_execute-sql --json -d '{"sql":"SELECT * FROM rpt.rpt_xxx LIMIT 10","odin_cluster":"high_confidential"}'
```

## 返回数据

```json
{
    "errno": 0,
    "errmsg": "ok",
    "data": {
        "list": [
            { "performance_city_abbr_name": "武汉", "cnt": "26395" }
        ],
        "queryId": 123456,
        "warn": null
    }
}
```

| 字段 | 说明 |
|------|------|
| data.list | 查询结果行集合，每行是 {列名: 值}，记为 #{data} |
| data.queryId | 本次即席查询任务 ID，记为 #{data.queryId} |
| data.warn | 查询告警信息，非空时需提示用户，记为 #{data.warn} |

## 处理说明

### 调用前：SQL 格式化

执行前对 SQL 做格式化：

0. **⚠️ 表名带库前缀 `db.table`**：`FROM` / `JOIN` 的表名一律写成 `库名.表名`（如 `rpt.rpt_xxx`），不要只写裸表名（会报表不存在）；库名取 `/tables` 返回的 `tableList[].db.dbName`、表名取 `tableList[].code`，拼成 `{db.dbName}.{code}`
1. **多行合并单行**：多余空白压缩为一个空格
2. **单引号转义**：bash 传参时单引号转义为 `'\''`
3. **去掉末尾分号**：SQL 末尾 `;` 移除，避免 Odin 解析异常

示例：
```
原始: SELECT city_name, count(1) AS cnt
      FROM rpt.rpt_xxx
      WHERE pt = '20260625'
      GROUP BY city_name
      LIMIT 10;

格式化: {"sql":"SELECT city_name, count(1) AS cnt FROM rpt.rpt_xxx WHERE pt = '\''20260625'\'' GROUP BY city_name LIMIT 10"}
```

### 调用后：结果展示

- 默认展示前 10 条，超过时提示总数（如"共 156 条，展示前 10 条"）
- 用户如需更多数据，调整 `LIMIT n`（不支持 OFFSET，无法服务端分页）或走导出流程

### 分区变量占位符

SQL 中包含 `${-1d_pt}`、`${-2d_pt}` 等分区变量时，说明用户已通过 Odin 变量系统管理分区，**直接使用原 SQL，不做任何修改**。

### 字段清洗（按需）

仅在以下情况对问题字段添加 `regexp_replace` 清洗：
- 返回结果中某字段值包含 `\r`、`\n`、`\t` 或大量空格，终端展示混乱
- 用户反馈数据"多了"或"少了"，怀疑特殊字符干扰

格式：`regexp_replace(col, '\\n|\\r|\\t|\\s+|,', '') as col`，聚合函数和表达式字段无需清洗。

### 常见错误

**errno=100 — 表权限校验异常**：

```json
{"errno": 100, "errmsg": "权限校验异常, 无权限的表为: [rpt_xxx, rpt_yyy] ...", "data": ""}
```

1. 从 errmsg 提取无权限表名告知用户
2. 引导申请权限：https://wiki.lianjia.com/pages/viewpage.action?pageId=1289200472
3. 如有替代表可建议换表重试

**errno=1 — 相同 SQL 正在执行**：

```json
{"errno": 1, "errmsg": "相同的sql正在执行，请到查询历史中查看...", "data": ""}
```

1. 告知用户无需重复提交
2. 引导到 Odin 查询历史查看结果
3. 确认上次任务已结束后可重试

**errno≠0 且非 100/1 — SQL 执行失败（语法错误 / 字段不存在 / 类型不匹配等）**：

这是 SQL "不对" 时最常见的返回。后端不做前置语法校验，SQL 由 Odin 引擎执行时校验，出错即以 `errno≠0` + `errmsg` 返回。处理：

1. 把 `errmsg` **完整透传给用户**，不要静默吞掉；
2. 结合 errmsg 定位问题（如字段名拼错、表未加分区、聚合缺 GROUP BY），提示用户或自行修正后重试；
3. 场景 B（自造 SQL）应回到 Step2，对照 `/table/columns` 的真实字段核对后重新构造。

**errno=0 但 data.list 为空**：查询成功但无匹配数据，检查分区条件或筛选条件。

### 注意事项

- data.list 中数值以字符串返回，汇总计算需类型转换
- 表名从 `/tables` 接口获取，列名从 `/table/columns` 获取，不可自行构造
- **表名务必带库前缀 `db.table`（如 `rpt.rpt_xxx`）**，库名取 `/tables` 的 `db.dbName`，不要只写裸表名
- 分区字段在 WHERE 中应明确指定值或范围，避免全表扫描
- **Odin 引擎不支持 OFFSET**：禁止写 `LIMIT ... OFFSET ...` 或 `LIMIT m, n`（offset 形式），会直接报错；需要更多数据用 `LIMIT n` 调整规模或走导出流程
