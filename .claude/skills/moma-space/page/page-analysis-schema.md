# 页面分析 Canonical Schema

本 Schema 是“需求/来源 → 页面路由 → Database/字段映射 → 生成与检查”的中间合同。分析器只描述证据和候选项；真实 Database schema 仍通过 Agent CLI 读取或创建。可机器校验的 JSON Schema 见 [`page-analysis.schema.json`](page-analysis.schema.json)。

## 1. 顶层结构

```typescript
type OutputMode = "static" | "database-readonly" | "database-readwrite";
type PageType = "display" | "form" | "mixed";
type EvidenceLevel = "strong" | "medium" | "weak" | "none";
type Confidence = "high" | "medium" | "low";
type ValueType = "text" | "number" | "select" | "multi_select" | "unknown";
type WriteSupport = "confirmed" | "readonly" | "unknown";

interface PageAnalysis {
  schema_version: "1.0";
  title: string;
  output_mode: OutputMode;
  page_type: PageType;
  needs_database: {
    level: EvidenceLevel;
    reason: string;
  };
  databases: DatabaseDependency[];
  sdk: {
    uses_current_sdk: boolean;
    methods: string[];
    database_ids: string[];
  };
  assets: AssetDependency[];
  signals: string[];
  source: string[];
  confidence: Confidence;
}
```

## 2. Database 与字段映射

```typescript
interface DatabaseDependency {
  source_database_id?: string;
  title: string;
  properties: Array<{
    name: string;
    config: Record<string, unknown>;
  }>;
  bindings: Record<string, {
    value_type: ValueType;
    write_support: WriteSupport;
    form_selector?: string;
    display_selector?: string;
    render_signal?: string;
  }>;
}
```

规则：

- `source_database_id` 只写分析器从当前 HTML 明确提取的 ID，不生成占位 ID；
- `properties[].config` 遵循 `{ text: "" }`、`{ number: 0 }` 等后端 schema 结构，不添加假想的通用 `type`；
- `write_support: confirmed` 只适用于当前真实 SDK 已验证的 `text`、`number`、`select`、`multi_select` 写入结构；
- date、checkbox、URL、邮箱、电话、图片、附件、人员等可以作为只读候选，但不得据此猜测运行期写入值；
- binding key 是 Database 的真实字段名或待创建字段名。

Selector 按稳定性选择：

```text
[name] → [data-field] → #id → 稳定 class → :nth-child
```

不要为已有稳定 selector 生成脆弱的深层 DOM 路径。

## 3. 资源结构

```typescript
interface AssetDependency {
  source: string;
  kind: "image" | "stylesheet" | "script" | "font" | "other";
  resolution: "inline" | "uploaded" | "remote" | "unresolved";
}
```

`resolution` 是分析时状态，不是上传承诺。最终状态由 [`resource-normalization.md`](resource-normalization.md) 和资源检查器验证。

## 4. 路由判据

- `strong`：当前 SDK、明确持久化/维护需求、提交表单后要保存、记录 CRUD；
- `medium`：有表单、筛选/分页或结构化数据，并且业务语义暗示后续更新；
- `weak`：只有表格、重复卡片、列表或可转成结构化数据的展示；
- `none`：纯叙事、报告、专题或一次性展示。

`weak` 和 `none` 默认 `static`；`medium` 根据业务意图选择 readonly/readwrite；`strong` 直接选择动态模式，不增加额外决策步骤。

## 5. 完整示例

```json
{
  "schema_version": "1.0",
  "title": "项目看板",
  "output_mode": "database-readwrite",
  "page_type": "mixed",
  "needs_database": {
    "level": "strong",
    "reason": "页面使用当前 Database SDK 并包含新增记录表单"
  },
  "databases": [
    {
      "source_database_id": "db_project_01",
      "title": "项目看板",
      "properties": [
        { "name": "任务名称", "config": { "text": "" } }
      ],
      "bindings": {
        "任务名称": {
          "value_type": "text",
          "write_support": "confirmed",
          "form_selector": "[name=\"任务名称\"]",
          "display_selector": "[data-field=\"任务名称\"]"
        }
      }
    }
  ],
  "sdk": {
    "uses_current_sdk": true,
    "methods": ["addRecord", "query"],
    "database_ids": ["db_project_01"]
  },
  "assets": [],
  "signals": ["current-sdk", "form", "record-write"],
  "source": ["page.html", "intent"],
  "confidence": "high"
}
```
