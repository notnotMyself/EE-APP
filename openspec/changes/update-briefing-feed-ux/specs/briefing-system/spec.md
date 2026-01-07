## MODIFIED Requirements

### Requirement: Briefing Card Display
简报卡片 SHALL 以视觉吸引的方式展示关键信息，鼓励用户驻足停留。

#### Scenario: 卡片显示封面图
- **GIVEN** 简报已生成
- **WHEN** 用户打开信息流页面
- **THEN** 每个简报卡片应显示：
  - 封面图区域（240px 高度）
  - 封面图降级方案：渐变背景 + 类型图标（96px）
  - 优先级标签浮动在封面图左上角
  - 未读标记（12px 圆点）浮动在右上角

#### Scenario: 卡片信息层次
- **GIVEN** 简报卡片已渲染
- **WHEN** 用户扫描卡片
- **THEN** 信息应按以下层次展示：
  - Agent 头像（32px）+ 名称 + 角色标签 + 时间戳
  - 标题（titleLarge, 22px, 粗体，最多 2 行）
  - 摘要（bodyMedium, 16px, 灰色，最多 3 行）
  - 影响说明（可选，彩色背景卡片）

#### Scenario: 卡片无操作按钮
- **GIVEN** 简报卡片已渲染
- **WHEN** 用户查看卡片
- **THEN** 卡片底部不应显示任何操作按钮
- **AND** 整个卡片可点击跳转到详情页

#### Scenario: 卡片视觉间距
- **GIVEN** 多个简报卡片
- **WHEN** 用户滚动信息流
- **THEN** 卡片间距应为：
  - 垂直间距：12px
  - 水平边距：16px
  - 卡片内边距：16px

### Requirement: Briefing Detail Page
简报详情 SHALL 通过全屏页面展示，提供完整信息和快捷操作入口。

#### Scenario: 点击卡片跳转详情页
- **GIVEN** 用户在信息流页面
- **WHEN** 用户点击简报卡片
- **THEN** 应跳转到全屏详情页（移除 Bottom Sheet 弹窗）
- **AND** 自动标记该简报为已读

#### Scenario: 详情页 Hero 区域
- **GIVEN** 详情页已打开
- **WHEN** 用户查看页面顶部
- **THEN** 应显示：
  - Hero 封面大图（300px 高度）
  - 优先级标签（左上角浮动）
  - 未读标记（右上角浮动，如果适用）

#### Scenario: 详情页内容结构
- **GIVEN** 详情页已渲染
- **WHEN** 用户滚动页面
- **THEN** 内容应按以下顺序展示：
  - 标题（headlineMedium, 28-32px, 粗体）
  - 元数据行（类型标签、时间戳）
  - 分隔线
  - 影响说明（如果有，彩色卡片）
  - 完整摘要（bodyLarge, 行高 1.6）

#### Scenario: 详情页底部输入栏
- **GIVEN** 详情页已打开
- **WHEN** 用户查看页面底部
- **THEN** 应显示固定的底部栏：
  - 快捷问题 Chips（横向滚动）
  - 多行输入框（提示："有疑问？直接问 AI..."）
  - 发送按钮（圆形填充按钮）

#### Scenario: 快捷问题填充输入框
- **GIVEN** 详情页底部栏可见
- **WHEN** 用户点击快捷问题 Chip（如"为什么会这样？"）
- **THEN** 问题文本应自动填入输入框

#### Scenario: 发送消息创建对话
- **GIVEN** 用户在详情页输入框中输入消息
- **WHEN** 用户点击发送按钮
- **THEN** 系统应：
  - 如果简报无关联对话，创建新对话
  - 将消息发送到对话
  - 跳转到对话页面
  - 清空输入框

#### Scenario: 发送按钮加载状态
- **GIVEN** 用户点击发送按钮
- **WHEN** 消息正在发送
- **THEN** 发送按钮应显示：
  - 圆形进度指示器（20x20px, strokeWidth: 2）
  - 禁用点击

### Requirement: Briefing Card Visual Design
简报卡片 SHALL 使用渐变背景和图标作为封面图的降级方案，确保视觉吸引力。

#### Scenario: 封面图降级方案
- **GIVEN** 简报没有自定义封面图
- **WHEN** 卡片渲染
- **THEN** 应显示降级封面：
  - 渐变背景（根据简报类型）
    - Alert: 红色系渐变 (#FEE2E2 → #FECACA)
    - Insight: 紫色系渐变 (#EDE9FE → #DDD6FE)
    - Summary: 蓝色系渐变 (#DBEAFE → #BFDBFE)
    - Action: 绿色系渐变 (#D1FAE5 → #A7F3D0)
  - 类型图标（96px, 白色 40% 透明度）

#### Scenario: 优先级标签样式
- **GIVEN** 简报卡片/详情页渲染
- **WHEN** 显示优先级标签
- **THEN** 标签应：
  - 背景色：P0 红色 / P1 橙色 / P2 蓝色
  - 文字：白色、粗体
  - 圆角：4-6px
  - 内边距：horizontal 8-12px, vertical 4-6px
  - 文本：P0/P1/P2 或 "P0 - 紧急" 等

#### Scenario: 未读标记样式
- **GIVEN** 简报状态为"新"
- **WHEN** 卡片/详情页渲染
- **THEN** 应显示未读标记：
  - 圆形（12px 直径）
  - 颜色：优先级色
  - 白色边框（2px）
  - 浮动在右上角

## ADDED Requirements

### Requirement: Detail Page Navigation
用户 SHALL 能够从信息流直接跳转到全屏详情页，无需 Bottom Sheet 中间层。

#### Scenario: 移除 Bottom Sheet 弹窗
- **GIVEN** 用户在信息流页面
- **WHEN** 用户点击简报卡片
- **THEN** 系统不应显示 Bottom Sheet 弹窗
- **AND** 应直接使用 Navigator.push 跳转到全屏页面

#### Scenario: 详情页自动标记已读
- **GIVEN** 简报状态为"新"
- **WHEN** 详情页 initState 触发
- **THEN** 系统应自动调用 markAsRead API
- **AND** 刷新信息流的未读计数

### Requirement: Quick Question Chips
详情页 SHALL 提供快捷问题选项，降低用户输入成本。

#### Scenario: 显示预设快捷问题
- **GIVEN** 详情页已打开
- **WHEN** 用户查看底部栏
- **THEN** 应显示快捷问题 Chips：
  - "为什么会这样？"
  - "给我详细分析"
  - "如何改进？"

#### Scenario: 快捷问题横向滚动
- **GIVEN** 快捷问题 Chips 宽度超过屏幕
- **WHEN** 用户左右滑动
- **THEN** 问题列表应可横向滚动

### Requirement: AppBar Actions (Placeholder)
详情页 AppBar SHALL 提供分享和跟踪按钮（Phase 3/4 实现）。

#### Scenario: 显示分享按钮
- **GIVEN** 详情页已打开
- **WHEN** 用户查看 AppBar
- **THEN** 应显示分享按钮（share_outlined 图标）
- **AND** 点击时显示 "分享功能即将上线" 提示

#### Scenario: 显示跟踪按钮
- **GIVEN** 详情页已打开
- **WHEN** 用户查看 AppBar
- **THEN** 应显示跟踪按钮（track_changes_outlined 图标）
- **AND** 点击时显示 "跟踪功能即将上线" 提示

## REMOVED Requirements

### Requirement: Bottom Sheet Briefing Detail
**Reason**: Bottom Sheet 只显示部分信息，用户需要多次点击才能看到完整内容。全屏详情页提供更好的阅读体验。

**Migration**:
- 移除 `_showBriefingDetail` 方法
- 移除 `DraggableScrollableSheet` 相关代码
- 所有详情展示逻辑迁移到 `BriefingDetailPage`

### Requirement: Card Action Buttons
**Reason**: 卡片内操作按钮增加视觉噪音，影响浏览体验。将操作统一到详情页降低认知负担。

**Migration**:
- 移除 `_buildActions` 方法
- 移除 `onAction` 回调参数
- 操作按钮（分享、跟踪、忽略）迁移到详情页 AppBar 和菜单
- 问答功能迁移到详情页底部输入栏
