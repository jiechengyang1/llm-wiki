# 读取资产详情

[管理流程与接口索引](../index.md)。身份、写入确认及错误处理遵循入口规则。

## 指令

```bash
moma moma-data api 'GET_moma-data_cli_asset-management_{data_asset_id}' --json -p 'data_asset_id=123'
```

返回 data 为当前有权访问的资产详情，核对 id、asset_type、state、name/description/tags 和 detail。修改 Hive 草稿或同步前读取现值；state=1 为草稿，state=2 为已发布。无权限/不存在时停止，不切换身份。

[Hive 草稿回写](../create/update_hive.md) 要保留完整编辑字段；[同步配置](../sync/get_config.md) 另有独立读接口。没有同步行时，Hive 分片和索引配置仍可从 detail 查看。
