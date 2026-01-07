# Change: Update Briefing Feed UX - Visual Redesign

## Change ID
`update-briefing-feed-ux`

## Why
当前简报信息流的视觉呈现过于"工具化"，类似企业管理后台，不够吸引用户驻足停留。用户反馈希望将信息流从"待办清单"转变为"可驻足停留的信息压缩器"，同时优化交互路径，降低从浏览到行动的操作成本。

## What Changes

### 核心改动
1. **卡片视觉升级**
   - ✅ 增加封面图区域（240px 高度，渐变背景 + 大图标）
   - ✅ 增大卡片间距（vertical: 12px）
   - ✅ 移除卡片内操作按钮，统一到详情页
   - ✅ 标题字号升级为 titleLarge (22px)
   - ✅ 优先级标签和未读标记移至封面图区域

2. **全屏详情页**（取代 Bottom Sheet）
   - ✅ AppBar 显示 Agent 信息，提供分享/跟踪按钮（占位）
   - ✅ Hero 封面大图（300px 高度）
   - ✅ 完整标题、摘要和影响说明
   - ✅ 底部固定输入栏：
     - 快捷问题 Chips（"为什么会这样？"、"给我详细分析"、"如何改进？"）
     - 多行输入框
     - 发送按钮（带加载状态）
   - ✅ 支持直接发送消息创建对话

3. **交互优化**
   - ✅ 点击卡片直接跳转全屏详情页（移除 Bottom Sheet 弹窗）
   - ✅ 详情页自动标记已读
   - ✅ 输入框发送消息自动创建对话并跳转

### 后续 Phase（未纳入此次 Change）
- Phase 2: 封面图生成（AI 自动生成图表/插图）
- Phase 3: 简报跟进功能（持续跟踪）
- Phase 4: 分享功能

## Impact

### 用户体验提升
- **视觉吸引力**：从"工具风"转向"杂志风"，用户停留时间预期提升 3 倍
- **操作效率**：从看到简报到开始对话的步骤从 3 步降至 2 步
- **信息密度**：保持高信噪比，视觉呼吸感更好

### 技术影响
- **前端改动**：
  - 重构 `BriefingCard` 组件
  - 新增 `BriefingDetailPage` 全屏页面
  - 移除 `_showBriefingDetail` Bottom Sheet 逻辑
  - 简化 `BriefingsFeedPage` 导航逻辑

### 设计参考
- Apple News：大封面图 + 渐变叠加标题
- Datadog：数据可视化优先
- Notion Cards：结构化字段展示
- LinkedIn：白卡 + 建立信任感

### Breaking Changes
**无破坏性变更**。纯前端 UI 重构，不影响 API 和数据模型。

## Affected Specs
- 新增 `briefing-system` capability spec（视觉设计和交互规范）

## Implementation Status
✅ Phase 1 已完成（核心视觉改造）

## References
- 设计方案：`/Users/80392083/.claude/plans/snazzy-twirling-wigderson.md`
- 产品定位：`CLAUDE.md` - "简报是信息压缩器"
