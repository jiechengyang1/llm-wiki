# 页面美化执行流程

本流程负责把已核对的内容母本转成清晰、有辨识度且可发布的页面。视觉细节继续以 [`beautify/beautify-guide.md`](beautify/beautify-guide.md) 和 [`beautify/visual-techniques.md`](beautify/visual-techniques.md) 为准，本文件只编排步骤。

## 1. 先整理内容母本

提取标题、结论、章节、数据、引用、行动项和来源。先解决重复、缺失和叙事顺序，再设计视觉；不以装饰掩盖内容问题。

多素材输入要融合成一条叙事：

```text
背景 → 核心结论 → 证据/数据 → 细节 → 行动
```

## 2. 选择页面形态

- 静态长页：报告、专题、总结、图文叙事；
- Database readonly：持续数据、看板、筛选、排序、分页；
- Database readwrite：表单、记录维护、操作型应用。

页面形态来自 [`page-analysis-schema.md`](page-analysis-schema.md)，不能为了展示效果把静态数据虚构成动态 Database。

## 3. 定义视觉方向

选择一个明确主风格，并从 `visual-techniques.md` 选择 2–3 种与内容匹配的技巧。建立有限的颜色、字号、间距、圆角和阴影 token；避免同时堆叠所有技巧。

优先级：

1. 信息层级和阅读路径；
2. 数据与结论可理解；
3. 交互反馈和状态；
4. 装饰与品牌气质。

**已有应用修复例外：** 加载 [`repair-guide.md`](repair-guide.md) 后，优先级改为核心交互可用、交互反馈清晰、视觉样式完善、最小必要代码调整。SDK 及其成功返回的数据无条件可信，不通过数据纠错或 fallback 掩盖页面侧问题。

## 4. 响应式实现

至少检查桌面、平板和移动窄屏：

- 不出现无意横向滚动；
- 导航、表格和图表在窄屏可使用；
- 点击/触控目标足够大；
- 键盘焦点顺序合理，`:focus-visible` 清晰；
- disabled/submitting 状态明确，不允许重复提交；
- 弹层、菜单、滚动和关闭路径在鼠标、键盘与触控下都可用；
- 文字行长和间距保持可读；
- 动效服从 `prefers-reduced-motion`；
- 关键信息不只依赖颜色表达。

## 5. 动态页状态

动态页必须包含 loading、empty、ready、error；写操作额外包含 submitting/disabled。图表提供文字摘要。`onUpdated` 只刷新当前 iframe 自己通过 SDK 完成的写操作，不设计为跨用户实时体验。

## 6. 归一化和发布前检查

```text
完成内容和视觉
→ resource normalization
→ SDK lint（动态页）
→ resource lint
→ 2 MiB 检查
→ upload/update
→ publish
→ 返回 publish URL
→ 清理中间产物
```

美化不能改变唯一交付物：最终只交付发布 URL，不以截图、本地 HTML 或节点 ID 代替。
