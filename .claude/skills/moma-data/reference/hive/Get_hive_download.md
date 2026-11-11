# 查询数据直接下载

## 指令

```bash
moma moma-data api GET_moma-data_hive_download -q "queryId=123456&fileType=4" -o adhoc_123456.xlsx
```

⚠️ **下载接口禁止加 `--json`**：本接口返回二进制文件流，加 `--json` 会导致 CLI 尝试解析响应为 JSON，文件写入内容错误（空文件或乱码）。

## 指令参数说明

Query 参数（-q key=v&key2=v2）：
  queryId        即席查询任务 ID（由 execute-sql 返回的 data.queryId），必填
  fileType       文件类型：1-CSV / 2-TSV / 3-TXT / 4-Excel，默认 4，可选
  odin_cluster   Odin 集群：standard | high_confidential，可选，默认 standard
  asset_id       资产 ID。从资产命中、且 execute-sql 带了 asset_id 时必填，下载必须带同一个值；传入后使用资产创建人的 ucid 发起查询，避免因当前用户无直接访问权限导致失败

注意：本接口返回的是文件附件（二进制流），需用 `-o <文件名>` 将结果保存到本地文件。

使用示例:

```bash
# 从资产查询得到的 queryId，下载必须带同一个 asset_id
moma moma-data api GET_moma-data_hive_download -q "queryId=123456&asset_id=821" -o adhoc_123456.xlsx

# 裸查询得到的 queryId
moma moma-data api GET_moma-data_hive_download -q "queryId=123456" -o adhoc_123456.xlsx

# 下载 CSV
moma moma-data api GET_moma-data_hive_download -q "queryId=123456&fileType=1" -o adhoc_123456.csv

# 高密集群下载
moma moma-data api GET_moma-data_hive_download -q "queryId=123456&fileType=4&odin_cluster=high_confidential" -o adhoc_123456.xlsx
```

## 指令返回数据说明

成功时直接返回文件内容（按 fileType 决定格式），文件名形如 `adhoc_<queryId>.<ext>`：

- fileType=1：CSV（UTF-8 BOM）
- fileType=2：TSV（UTF-8 BOM）
- fileType=3：TXT（制表符分隔，UTF-8 BOM）
- fileType=4：Excel（.xlsx）

失败时返回标准 JSON 错误结构：

```json
{
    "errno": -1,
    "errmsg": "下载查询结果失败: ...",
    "data": null
}
```

## 处理说明

- 本接口用于下载 execute-sql 任务的完整结果数据，适合数据量较大、需导出文件的场景。
- 调用前应先通过 GET_moma-data_hive_query_progress 确认任务状态为完成（FINISHED），否则可能下载到空文件或失败。
- 上游始终以 Excel 取原始数据，再按 fileType 转换；fileType 仅支持 1/2/3/4，其他值会返回错误。
- queryId 必须来自 execute-sql 返回的 data.queryId，不可自行构造。
- 高密集群下载时，odin_cluster 需与 execute-sql 提交时保持一致。

## 下载后必须验证文件有效性

下载完成后，**必须立即执行以下验证**，不可直接告知用户下载成功：

```bash
# 检查文件大小和类型
ls -lh <文件路径> && file <文件路径>
```

判断规则：
- 文件类型为 `Microsoft Excel` 或 `Zip archive data`（xlsx 本质是 zip）且大小 > 10KB → 下载成功，告知用户路径；
- 文件类型为 `JSON data` 或大小 < 1KB → 下载失败，读取文件内容提取 errmsg 告知用户具体错误，**不要声称下载成功**。
