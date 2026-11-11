# 获取数据模型列表

> 分页获取当前登录用户有权限的奥丁数据模型列表，支持模糊检索。
> ucId 由登录上下文自动注入，无需传入。

## 指令

```bash
moma moma-data api POST_moma-data_odin_model_list --json -d '{"page":1,"pageSize":10}'
```

## 指令参数说明

-d modelName: 模型名称，模糊检索 (选传)
-d page:      分页页码，默认 1 (选传)
-d pageSize:  每页数量，默认 10，最大 100 (选传)

指令使用示例：

```bash
moma moma-data api POST_moma-data_odin_model_list --json \
  -d '{"modelName":"业绩","page":1,"pageSize":50}'
```

## 返回数据说明

示例数据：

```json
{
  "errno": 0,
  "errmsg": "操作成功",
  "data": {
    "modelList": [
      {
        "modelId": 191976,
        "modelName": "moma模型接入",
        "projectId": 0,
        "configType": 0,
        "maintainerId": 1000000031085672,
        "clusterType": "default",
        "odinCluster": "public"
      }
    ],
    "totalCount": 1,
    "page": 1,
    "pageSize": 10
  }
}
```

字段说明：

- `modelId`：模型 ID，后续 detail / columns / query 都需要它
- `modelName`：模型名称（用于匹配用户描述）
- `projectId`：模型所属项目 ID
- `configType`：模型类型，0-可视化，1-SQL
- `maintainerId`：模型维护人 ucId
- `clusterType`：上游模型集群类型，取值 `default`（默认公共）/ `finance`（金融）/ `hfc`（人力）/ `secret`（高密）
- `odinCluster`：本服务派生字段，由 `clusterType` 映射得到，可**直接**作为 `/odin/model/query` 的 `odin_cluster` 入参

`clusterType` ↔ `odinCluster` 映射关系：

| clusterType | odinCluster          | 含义     | 查询 Host                      |
|-------------|----------------------|----------|--------------------------------|
| `default`   | `public`             | 默认公共 | ODIN_DATA_MODEL_QUERY_HOST     |
| `finance`   | `public`             | 金融     | ODIN_DATA_MODEL_QUERY_HOST     |
| `hfc`       | `public`             | 人力     | ODIN_DATA_MODEL_QUERY_HOST     |
| `secret`    | `high_confidential`  | 高密     | ODIN_DATA_MODEL_HC_QUERY_HOST  |

**注意**：4 类上游集群在查询侧只分两条路径——仅 `secret` 走高密 Host，其余三类共用默认公共 Host。
后续 `model_query` 必须根据这里的 `odinCluster` 字段透传，**严禁猜测**模型集群归属；
当无法在单页中匹配到目标模型时，按 `page` 翻页或通过 `modelName` 模糊检索缩小范围；
仍然无法精准匹配时，使用 AskUserQuestion 与用户确认。
