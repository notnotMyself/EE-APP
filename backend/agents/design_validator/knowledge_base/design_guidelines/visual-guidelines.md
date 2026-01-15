# 视觉设计规范

## 颜色系统

### 品牌色

- **Primary**: #4F46E5 (Indigo 600)
- **Secondary**: #10B981 (Emerald 500)
- **Accent**: #F59E0B (Amber 500)

### 语义色

- **Success**: #10B981 (Green)
- **Warning**: #F59E0B (Amber)
- **Error**: #EF4444 (Red)
- **Info**: #3B82F6 (Blue)

### 中性色

- **Text Primary**: #1F2937 (Gray 800)
- **Text Secondary**: #6B7280 (Gray 500)
- **Background**: #FFFFFF
- **Surface**: #F9FAFB (Gray 50)
- **Border**: #E5E7EB (Gray 200)

### 颜色使用原则

1. 60-30-10法则：主色60%，次要色30%，强调色10%
2. 一个界面不超过3种主要颜色
3. 保持对比度 >= 4.5:1 (WCAG AA)

## Typography (字体排版)

### Type Scale

```
H1: 32pt / Bold / Line height 1.2
H2: 28pt / Bold / Line height 1.3
H3: 24pt / Semibold / Line height 1.3
H4: 20pt / Semibold / Line height 1.4
Body: 16pt / Regular / Line height 1.5
Body Small: 14pt / Regular / Line height 1.5
Caption: 12pt / Regular / Line height 1.4
```

### 字体族

- **iOS**: SF Pro (系统默认)
- **Android**: Roboto (系统默认)
- **Web**: Inter, -apple-system, BlinkMacSystemFont

### 排版原则

1. 每行文字长度: 50-75 字符（中文 25-35 字）
2. 段落间距: 1.5-2 倍行高
3. 标题与正文间距: 0.75-1.25 倍标题行高

## 间距系统 (8pt Grid)

### 基础单位

- **Base Unit**: 8pt
- 所有间距必须是8的倍数

### 常用间距值

```
4pt  - 元素内微间距
8pt  - 元素内标准间距
12pt - 紧凑型组间距
16pt - 标准组间距
24pt - 松散组间距
32pt - Section间距
48pt - 大Section间距
64pt - Page margins
```

### 内边距 (Padding)

- 卡片: 16pt
- 按钮: 水平24pt, 垂直12pt
- 输入框: 水平16pt, 垂直12pt

### 外边距 (Margin)

- 屏幕边距: 16pt (移动端)
- 列表项间距: 8pt
- Section间距: 24pt

## 圆角 (Border Radius)

### 标准值

```
Small: 4pt   - Tag, Badge
Medium: 8pt  - Button, Input
Large: 12pt  - Card
Extra: 16pt  - Modal, Sheet
Full: 9999pt - Pill Button
```

### 使用原则

1. 同一界面使用一致的圆角值
2. 嵌套元素的圆角应递减（外 > 内）

## 阴影 (Elevation)

### 阴影层级

```
Level 0 (Flat):
  box-shadow: none

Level 1 (Raised):
  box-shadow: 0 1px 3px rgba(0,0,0,0.12)

Level 2 (Floating):
  box-shadow: 0 4px 6px rgba(0,0,0,0.1)

Level 3 (Modal):
  box-shadow: 0 10px 15px rgba(0,0,0,0.1)

Level 4 (Popover):
  box-shadow: 0 20px 25px rgba(0,0,0,0.15)
```

### 使用场景

- Flat: 平铺内容、列表项
- Raised: 卡片、按钮
- Floating: Floating Action Button
- Modal: 模态对话框
- Popover: 下拉菜单、Tooltip

## 图标系统

### 图标库

- **推荐**: Heroicons, Lucide Icons, Material Symbols
- **风格**: Outline（线性）或 Filled（填充），全局统一

### 图标尺寸

```
Small: 16x16pt  - Inline icon
Medium: 20x20pt - Button icon
Large: 24x24pt  - Tab bar icon
XLarge: 32x32pt - Feature icon
```

### 图标颜色

- 默认: Text Secondary (#6B7280)
- 活跃状态: Primary (#4F46E5)
- 禁用状态: #D1D5DB (Gray 300)

## 组件规范

### 按钮

**Primary Button**:
- 背景: Primary色
- 文字: 白色
- 高度: 48pt (移动端)
- 圆角: 8pt
- 最小宽度: 120pt

**Secondary Button**:
- 背景: 透明
- 边框: 1pt Primary色
- 文字: Primary色

**Ghost Button**:
- 背景: 透明
- 文字: Primary色
- 无边框

### 卡片

- 背景: 白色
- 圆角: 12pt
- 内边距: 16pt
- 阴影: Level 1
- 边框: 可选 1pt #E5E7EB

### 输入框

- 高度: 48pt
- 圆角: 8pt
- 边框: 1pt #E5E7EB
- Focus边框: 2pt Primary色
- Error边框: 2pt Error色

## 动效

### 缓动函数 (Easing)

```
Ease Out: cubic-bezier(0, 0, 0.2, 1)  - 进入动画
Ease In: cubic-bezier(0.4, 0, 1, 1)   - 退出动画
Ease In Out: cubic-bezier(0.4, 0, 0.2, 1) - 状态切换
```

### 动画时长

```
Fast: 100-200ms    - 微交互（Hover, Focus）
Normal: 200-300ms  - 状态切换（Fade, Slide）
Slow: 300-500ms    - 复杂动画（Modal出现）
```

### 动画原则

1. 不要滥用动画
2. 动画应有目的（引导注意、提供反馈、增强理解）
3. 提供"减少动画"选项（accessibility）

## 响应式断点

```
Mobile: < 640px
Tablet: 640px - 1024px
Desktop: >= 1024px
Wide: >= 1440px
```

## 品牌元素

### Logo使用

- 最小尺寸: 32x32pt
- 留白: Logo周围至少有Logo高度的1/2作为留白
- 颜色: 全彩版、单色版（白色、黑色）

### 品牌调性

- 关键词: 专业、现代、可靠、高效
- 视觉风格: 简洁、几何、科技感
- 避免: 过度装饰、复杂纹理、拟物化
