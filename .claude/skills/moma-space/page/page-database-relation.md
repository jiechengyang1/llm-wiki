# Page ↔ Database 关系合同

本流程中的已明确 API 直接调用；写操作首次调用即携带 `--yes`。

页面与 Database 有两层不同关系，不能混为一谈。

## 1. 运行期依赖（必须）

最终 HTML 通过当前 SDK 使用的真实 `database_id` 是页面运行期关系的事实源：

```javascript
const db = window.__SPACE_PAGE__.database;
await db.query({ database_id: "db_real_id" });
```

创建、编辑和克隆完成后重新执行 `analyze_page.py`，验证 `sdk.database_ids` 与最终设计一致。多 Database 页面保留完整 ID 集，不能只记录第一个。

## 2. 服务端关系元数据（条件能力）

服务端 Page↔Database link/list/unlink 只在当前 `moma-space` 注册正式 API 时执行：

```bash
moma moma-space list
moma moma-space schema <FULL_API_NAME>
moma moma-space describe <FULL_API_NAME> \
  --request '{"body":{...}}' \
  --json
```

根据 live schema 组装参数，目标、接口和业务参数明确后直接调用；写调用第一次就追加 `--yes`。不要猜 API 名或字段。

当前已知注册 API 列表没有明确的 Page↔Database link/list/unlink API。因此在发现正式 API 前：

- 不调用 Library 的私有 `/space/api/agent/v1/link-page-database`、`list-page-database-relations`、`unlink-page-database`；
- 不自行获取 token 或让浏览器发 HTTP；
- 不把 parent node、文件夹层级或 move-node 当作关系元数据；
- 运行期 ID 正确时页面仍可上传和发布；只跳过不存在的元数据登记能力。

## 3. 各流程同步规则

### 新建页

1. 生成并 lint 最终 HTML；
2. upload-node 得到 page node ID；
3. 若存在正式 link API，对 final Database ID 集逐一登记；
4. publish-page。

### 编辑页

比较编辑前后的 ID 集：

```text
added = final_ids - original_ids
removed = original_ids - final_ids
```

有正式 API 时 link `added`、unlink `removed`；没有时只确保最终 HTML 运行期依赖正确。随后更新原节点并重新发布。

### 克隆页

- 独立数据副本：关系指向全部目标 Database ID；
- 共享数据：关系保留源 ID；
- 静态快照：最终 ID 集为空，并移除 SDK 调用。

## 4. 失败与交付

不得报告未执行的关系登记为成功。正式关系 API 存在但执行失败时，应明确记录后端错误并修复后继续。当前服务未提供该能力时，跳过元数据登记不改变最终交付合同：成功上传和发布后返回 publish URL，并清理中间产物。
