# 方案一：纯 CSS 磨砂玻璃（Frosted Glass）

> 生产环境首选方案。基于 `backdrop-filter: blur()` + 半透明背景 + CSS Mask 渐变边框实现。  
> 对应 Figma 设计稿 `rgba(255,255,255,0.68)` 规格，兼容 95%+ 浏览器。

---

## 核心原理

```
┌─────────────────────────────────────────┐
│  ::before  渐变边框（CSS Mask 技术）     │  ← 左上亮白 → 右下渐淡
│  ::after   顶部高光弧（Highlight 层）    │  ← 玻璃内部漫反射
│  content   半透明内容层                  │  ← rgba(255,255,255,0.68)
│  backdrop  backdrop-filter: blur(20px)  │  ← 磨砂核心
└─────────────────────────────────────────┘
         ↕ 背景内容（被模糊的底层）
```

---

## CSS 完整代码

### 卡片（Card）

```css
.glass-card {
  position: relative;
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 20px;
  /* 内阴影：对应 Figma inset 0px 4px 16px rgba(6,6,6,0.03) */
  box-shadow: inset 0 4px 16px rgba(6, 6, 6, 0.03);
  overflow: hidden;
}

/* 渐变边框（CSS Mask 技术：上亮下淡） */
.glass-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 20px;
  padding: 1px;                              /* 边框宽度 */
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 1)    0%,            /* 左上角：纯白高光 */
    rgba(255, 255, 255, 0.8) 20%,
    rgba(255, 255, 255, 0.3) 55%,            /* 中间渐淡 */
    rgba(255, 255, 255, 0.15) 75%,
    rgba(255, 255, 255, 0.4) 100%
  );
  /* 关键：镂空内部，只保留 1px 边框区域 */
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  mask-composite: exclude;
  pointer-events: none;
  z-index: 2;
}

/* 顶部内侧高光弧（Highlight 层，玻璃顶部集光效果） */
.glass-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 42%;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.38) 0%,
    rgba(255, 255, 255, 0) 100%
  );
  border-radius: 20px 20px 0 0;
  pointer-events: none;
  z-index: 1;
}
```

### 快捷标签（Chip / Tag）

```css
/* 对应 Figma: border 0.506px solid white + bg rgba(0,0,0,0.04) */
.glass-chip {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 5px 12px;
  height: 32px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 999px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.54);
  white-space: nowrap;
  /* box-shadow 模拟 0.5px 白边 + 顶部内高光 */
  box-shadow:
    0 0 0 0.5px rgba(255, 255, 255, 0.95),
    inset 0 0.5px 0 rgba(255, 255, 255, 0.8);
}
```

### 输入框（Input）

```css
/* 竖向渐变边框：上白 → 中透明 → 下白（上下高光，左右透明） */
.glass-input-wrap {
  border-radius: 14px;
  padding: 1px;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 1)    0%,
    rgba(255, 255, 255, 0)   45%,
    rgba(255, 255, 255, 0)   55%,
    rgba(255, 255, 255, 0.8) 100%
  );
}

.glass-input-inner {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 13px;
  padding: 12px 16px;
  box-shadow: inset 0 4px 16px rgba(6, 6, 6, 0.03);
}
```

### 次要按钮（Secondary Button）

```css
.glass-btn-secondary {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: rgba(0, 0, 0, 0.8);
  border: none;
  border-radius: 999px;
  box-shadow:
    0 0 0 0.5px rgba(255, 255, 255, 0.95),    /* 外框白边 */
    0 2px 8px rgba(0, 0, 0, 0.06),             /* 外部阴影 */
    inset 0 1px 0 rgba(255, 255, 255, 0.9);    /* 顶部内高光 */
  cursor: pointer;
  transition: all 0.15s;
}

.glass-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.85);
}
```

### 深色模式适配

```css
@media (prefers-color-scheme: dark) {
  .glass-card {
    background: rgba(30, 30, 35, 0.72);
    box-shadow: inset 0 4px 16px rgba(0, 0, 0, 0.12);
  }

  .glass-card::before {
    background: linear-gradient(
      145deg,
      rgba(255, 255, 255, 0.25) 0%,
      rgba(255, 255, 255, 0.08) 55%,
      rgba(255, 255, 255, 0.04) 75%,
      rgba(255, 255, 255, 0.12) 100%
    );
  }
}
```

### 无障碍降级

```css
/* 高对比模式：降级为实色背景 */
@media (prefers-contrast: more) {
  .glass-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: none;
  }
}

/* 减少动效 */
@media (prefers-reduced-motion: reduce) {
  .glass-card::after {
    display: none;
  }
}
```

---

## React / Next.js 组件封装

```tsx
// components/ui/GlassCard.tsx
import { ReactNode, CSSProperties } from 'react';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
  padding?: string;
  radius?: number;
}

export function GlassCard({
  children,
  className = '',
  style,
  padding = 'p-6',
  radius = 20,
}: GlassCardProps) {
  return (
    <div
      className={`glass-card ${padding} ${className}`}
      style={{ borderRadius: radius, ...style }}
    >
      {children}
    </div>
  );
}

// 快捷标签
export function GlassChip({ label }: { label: string }) {
  return <span className="glass-chip">{label}</span>;
}

// 输入框
export function GlassInput({ placeholder }: { placeholder?: string }) {
  return (
    <div className="glass-input-wrap">
      <div className="glass-input-inner">
        <input
          type="text"
          placeholder={placeholder}
          className="w-full bg-transparent border-none outline-none text-sm"
        />
      </div>
    </div>
  );
}
```

### 使用示例

```tsx
import { GlassCard, GlassChip, GlassInput } from '@/components/ui/GlassCard';

export function DescriptionContainer() {
  const chips = ['随便聊聊', '交互验证', '视觉讨论', '方案PK'];

  return (
    <GlassCard>
      <GlassInput placeholder="简单描述设计方案背景与目标" />
      <div className="mt-3 flex gap-2 flex-wrap">
        {chips.map((chip) => (
          <GlassChip key={chip} label={chip} />
        ))}
      </div>
    </GlassCard>
  );
}
```

---

## Tailwind v4 Token 定义

```css
/* globals.css — @theme inline 块中添加 */
@theme inline {
  --glass-bg: rgba(255, 255, 255, 0.68);
  --glass-bg-subtle: rgba(0, 0, 0, 0.04);
  --glass-border-white: rgba(255, 255, 255, 1);
  --glass-shadow-inner: inset 0px 4px 16px rgba(6, 6, 6, 0.03);
  --glass-blur: blur(20px) saturate(180%);
  --glass-radius-card: 20px;
  --glass-radius-chip: 999px;
  --glass-radius-input: 14px;
}
```

---

## 设计参数速查表

| 元素 | 背景色 | blur | 边框 | 内阴影 | 圆角 |
|------|--------|------|------|--------|------|
| 卡片 | `rgba(255,255,255,0.68)` | `blur(20px) saturate(180%)` | 渐变 1px（145deg 白→淡） | `inset 0 4px 16px rgba(6,6,6,0.03)` | `20px` |
| 输入框 | `rgba(255,255,255,0.72)` | `blur(20px) saturate(180%)` | 竖向渐变 wrapper | 同上 | `13px` |
| Chip | `rgba(0,0,0,0.04)` | — | `box-shadow 0 0 0 0.5px white` | `inset 0 0.5px 0 rgba(255,255,255,0.8)` | `999px` |
| 次要按钮 | `rgba(255,255,255,0.68)` | `blur(8px)` | `box-shadow 0 0 0 0.5px white` | `inset 0 1px 0 rgba(255,255,255,0.9)` | `999px` |

---

## 注意事项

1. **必须有有内容的背景**：`backdrop-filter` 需要元素后方有可模糊的内容（渐变背景/图片/文字），纯白页面上效果不明显
2. **`overflow: hidden` 是必须的**：防止 `::before` / `::after` 伪元素溢出圆角
3. **CSS Mask 边框原理**：通过 `padding: 1px` + mask 镂空内部，只让 1px 边框区域显示渐变色
4. **`::before` 已被占用**：如果组件内还需要用 `::before`，需改用 wrapper 元素 + `padding: 1px` 方式替代

---

## 来源

- Figma 设计稿：[2025 设计工程效率提升](https://www.figma.com/design/5lIfGL2PaZqAwVqClaV0Vf/) — Node `1887:7467`
- Demo 页面：`web/src/app/glass-demo/page.tsx`
- CSS 定义：`web/src/app/globals.css` — `/* Glass Demo — 方案一 */` 区块
