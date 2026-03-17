# 方案二 v2：SVG 液态折射玻璃（Liquid Glass）

> 视觉效果接近 Apple iOS 26 Liquid Glass 的"镜头折射"（Lensing）感。  
> 通过 SVG `feTurbulence + feDisplacementMap` 对 backdrop 内容进行动态扭曲，配合**鼠标追踪镜面高光**，模拟真实液态玻璃弯曲光线的物理属性。  
> **适用于关键视觉区域**（Hero、弹窗、通知卡片），不建议大面积铺开。

---

## 核心架构：五层叠加模型

```
┌─────────────────────────────────────────────────────┐
│  .lg-border    渐变边框（冷白 CSS Mask）              │  ← z-index: 5
│  .lg-specular  镜面高光（鼠标追踪 radial-gradient）   │  ← z-index: 4
│  .lg-tint      着色层（rgba 半透明白色）              │  ← z-index: 3
│  .lg-edge-ring 边缘光环（inset box-shadow）          │  ← z-index: 2
│  .lg-content   内容层                                │  ← z-index: 10
│  .lg-backdrop  backdrop-filter + SVG lg-lens 折射    │  ← z-index: 1
└─────────────────────────────────────────────────────┘
         ↕ 背景内容（被 feTurbulence 液态扭曲 + blur）
```

**与方案一的核心区别**：

| 对比项 | 方案一（磨砂）| 方案二 v2（液态）|
|--------|-------------|----------------|
| 背景处理 | 均匀高斯模糊 | SVG 湍流扭曲 + 模糊（Lensing）|
| 边框层 | `::before` CSS Mask | 独立 `.lg-border` div |
| 镜面高光 | 静态顶部渐变 | 鼠标追踪 `radial-gradient` |
| 动态感 | 静态 | SVG seed 动画 + 鼠标追踪 |
| 边框色调 | 纯白渐变 | 冷白（带微蓝色调）渐变 |
| 适用场景 | 全局通用 | 视觉焦点、关键通知 |

> ⚠️ **边框抖动陷阱**：不要把 SVG feTurbulence 滤镜直接应用到边框层（box-shadow）上。  
> seed 是整数离散跳跃，无法插值过渡，会导致边框瞬间位移抖动。  
> 正确做法：SVG 滤镜只作用于 `lg-backdrop`（扭曲背景内容），边框层保持静态。

---

## CSS 完整代码

### 卡片容器

```css
/* 卡片根容器：持有鼠标位置 CSS 变量 */
.lg-card {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  --mx: 50%;   /* 鼠标 X，由 useLiquidGlass hook 动态写入 */
  --my: 25%;   /* 鼠标 Y，默认偏上模拟顶部高光 */
  box-shadow:
    0 12px 48px rgba(0, 0, 0, 0.14),
    0 2px 8px rgba(0, 0, 0, 0.06);
}

/* Layer 1：背景模糊 + SVG 液态折射
   inset: -16px 让 backdrop 略大于容器，防止 blur 在边缘产生衰减 */
.lg-backdrop {
  position: absolute;
  inset: -16px;
  border-radius: 40px; /* 24 + 16 */
  backdrop-filter: blur(16px) saturate(180%) brightness(1.04);
  -webkit-backdrop-filter: blur(16px) saturate(180%) brightness(1.04);
  filter: url(#lg-lens);
  background: rgba(255, 255, 255, 0.08);
  z-index: 1;
  pointer-events: none;
}

/* Layer 2：边缘光环（静态 inset shadow，不加 SVG 滤镜）
   注意：不要在此层使用 feTurbulence，seed 跳跃会导致边框抖动 */
.lg-edge-ring {
  position: absolute;
  inset: 0;
  border-radius: 24px;
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.5),
    inset 0 0 24px rgba(255, 255, 255, 0.12);
  z-index: 2;
  pointer-events: none;
}

/* Layer 3：半透明着色（玻璃基底色） */
.lg-tint {
  position: absolute;
  inset: 0;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.18);
  z-index: 3;
  pointer-events: none;
}

/* Layer 4：镜面高光（核心交互层）
   radial-gradient 圆心跟随鼠标坐标，模拟玻璃曲面反射 */
.lg-specular {
  position: absolute;
  inset: 0;
  border-radius: 24px;
  background: radial-gradient(
    circle at var(--mx, 50%) var(--my, 25%),
    rgba(255, 255, 255, 0.38) 0%,
    rgba(255, 255, 255, 0.12) 28%,
    transparent 62%
  );
  z-index: 4;
  pointer-events: none;
  transition: background 0.06s linear;
}

/* Layer 5：渐变边框（CSS Mask 技术，冷白色调）
   右下角带微蓝 rgba(200,215,255) 模拟光谱色散 */
.lg-border {
  position: absolute;
  inset: 0;
  border-radius: 24px;
  padding: 1px;
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(255, 255, 255, 0.55) 18%,
    rgba(255, 255, 255, 0.12) 50%,
    rgba(200, 215, 255, 0.08) 75%,
    rgba(255, 255, 255, 0.22) 100%
  );
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  mask-composite: exclude;
  z-index: 5;
  pointer-events: none;
}

/* Layer 10：内容层（高于所有装饰层） */
.lg-content {
  position: relative;
  z-index: 10;
}
```

### 液态按钮

```css
/* 次要按钮 / 胶囊按钮：backdrop 毛玻璃 + 渐变边框 + 顶部扫光 */
.lg-btn-secondary,
.lg-btn-pill {
  position: relative;
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: rgba(0, 0, 0, 0.82);
  border: none;
  border-radius: 999px;      /* pill 形 */
  font-size: 13px;
  cursor: pointer;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.18s;
}

/* 渐变边框（CSS Mask） */
.lg-btn-secondary::before,
.lg-btn-pill::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 999px;
  padding: 1px;
  background: linear-gradient(145deg,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(255, 255, 255, 0.35) 50%,
    rgba(255, 255, 255, 0.1)  100%
  );
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  pointer-events: none;
}

/* 顶部扫光条（Illuminate 层） */
.lg-btn-secondary::after,
.lg-btn-pill::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 45%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.45) 0%, transparent 100%);
  border-radius: 999px 999px 0 0;
  pointer-events: none;
}

.lg-btn-secondary:hover,
.lg-btn-pill:hover {
  background: rgba(255, 255, 255, 0.42);
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
}

/* 幽灵按钮（深色背景场景） */
.lg-btn-ghost {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.88);
  border: none;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  box-shadow:
    0 0 0 0.5px rgba(255, 255, 255, 0.5),
    inset 0 0.5px 0 rgba(255, 255, 255, 0.35);
  transition: all 0.15s;
}
.lg-btn-ghost:hover { background: rgba(255, 255, 255, 0.2); }
```

### 快捷标签（Chip）

```css
.lg-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 5px 12px;
  height: 30px;
  background: rgba(255, 255, 255, 0.22);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  border-radius: 999px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.65);
  white-space: nowrap;
  box-shadow:
    0 0 0 0.5px rgba(255, 255, 255, 0.85),
    inset 0 0.5px 0 rgba(255, 255, 255, 0.7),
    0 1px 4px rgba(0, 0, 0, 0.06);
}
```

### 输入框

```css
/* 渐变边框 wrapper */
.lg-input-wrap {
  border-radius: 14px;
  padding: 1px;
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.9)  0%,
    rgba(255, 255, 255, 0.2)  40%,
    rgba(255, 255, 255, 0.05) 70%,
    rgba(255, 255, 255, 0.3)  100%
  );
}

/* 内部毛玻璃 */
.lg-input-inner {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: 13px;
  padding: 12px 16px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.4);
}
```

---

## SVG 滤镜定义

SVG 需要**放在 DOM 中**（`0×0` 隐藏元素），通过 `filter: url(#id)` 引用。  
**只作用于 `lg-backdrop`，不要应用到边框层**（会引发抖动，见下方说明）。

### lg-lens：主液态折射滤镜

```svg
<svg width="0" height="0" style="position:absolute;overflow:hidden" aria-hidden="true">
  <defs>
    <!--
      液态折射效果：
      - feTurbulence: 分形噪声，模拟液态扭曲场
      - feDisplacementMap: 根据噪声扭曲像素位置（Lensing）
      - feGaussianBlur: 轻微平滑，消除像素化锯齿
      - feComposite: 裁剪到原始形状，防止溢出

      seed 动画：整数离散跳跃无法插值，但应用到 backdrop 内容
      时视觉表现为"流动折射"，不会造成边框抖动。
    -->
    <filter id="lg-lens" x="-15%" y="-15%" width="130%" height="130%">
      <feTurbulence
        type="fractalNoise"
        baseFrequency="0.009 0.007"
        numOctaves="4"
        seed="5"
        result="noise"
      >
        <animate
          attributeName="seed"
          values="5;12;7;20;3;15;5"
          dur="12s"
          repeatCount="indefinite"
        />
      </feTurbulence>
      <feDisplacementMap
        in="SourceGraphic"
        in2="noise"
        scale="6"
        xChannelSelector="R"
        yChannelSelector="G"
        result="displaced"
      />
      <feGaussianBlur in="displaced" stdDeviation="0.3" result="smoothed" />
      <feComposite in="smoothed" in2="SourceGraphic" operator="in" />
    </filter>
  </defs>
</svg>
```

### 参数调节指南

| 参数 | 当前值 | 调小效果 | 调大效果 |
|------|--------|---------|---------|
| `baseFrequency` | `0.009 0.007` | 扭曲纹理更大块，粗犷 | 纹理细腻密集（性能↓）|
| `numOctaves` | `4` | 噪声层次少，平滑 | 层次丰富，细节更多 |
| `scale`（feDisplacementMap）| `6` | 折射幅度弱，接近磨砂 | 折射幅度强，液态感强 |
| `dur`（seed 动画）| `12s` | 越快越有"生命感" | 越慢越静谧 |
| `stdDeviation`（feGaussianBlur）| `0.3` | 扭曲边缘锐利 | 扭曲边缘柔和 |

---

## 鼠标追踪 Hook

```tsx
// useLiquidGlass：将鼠标坐标写入 CSS 变量 --mx / --my
// 绑定到 .lg-card 根元素上，lg-specular 层读取这两个变量
import { useRef, useEffect, RefObject } from 'react';

function useLiquidGlass(): RefObject<HTMLDivElement> {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const onMove = (e: MouseEvent) => {
      const r = el.getBoundingClientRect();
      el.style.setProperty('--mx', `${(((e.clientX - r.left) / r.width) * 100).toFixed(1)}%`);
      el.style.setProperty('--my', `${(((e.clientY - r.top) / r.height) * 100).toFixed(1)}%`);
    };
    const onLeave = () => {
      el.style.setProperty('--mx', '50%');
      el.style.setProperty('--my', '25%');  /* 默认：偏上模拟顶部高光 */
    };
    el.addEventListener('mousemove', onMove);
    el.addEventListener('mouseleave', onLeave);
    return () => {
      el.removeEventListener('mousemove', onMove);
      el.removeEventListener('mouseleave', onLeave);
    };
  }, []);
  return ref;
}
```

---

## React / Next.js 组件封装

```tsx
// app/glass-demo/page.tsx 或 components/ui/LiquidGlass.tsx
'use client';

/** SVG 液态滤镜定义，放在页面根层一次即可，不要在每个卡片内重复 */
export function LiquidGlassSVGFilters() {
  return (
    <svg
      width="0" height="0"
      style={{ position: 'absolute', overflow: 'hidden' }}
      aria-hidden="true"
    >
      <defs>
        <filter id="lg-lens" x="-15%" y="-15%" width="130%" height="130%">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.009 0.007"
            numOctaves="4"
            seed="5"
            result="noise"
          >
            <animate
              attributeName="seed"
              values="5;12;7;20;3;15;5"
              dur="12s"
              repeatCount="indefinite"
            />
          </feTurbulence>
          <feDisplacementMap
            in="SourceGraphic" in2="noise"
            scale="6" xChannelSelector="R" yChannelSelector="G"
            result="displaced"
          />
          <feGaussianBlur in="displaced" stdDeviation="0.3" result="smoothed" />
          <feComposite in="smoothed" in2="SourceGraphic" operator="in" />
        </filter>
      </defs>
    </svg>
  );
}

interface LiquidCardProps {
  children: React.ReactNode;
  showEdgeRing?: boolean;
  className?: string;
}

/** 液态玻璃卡片（五层架构） */
export function LiquidCard({ children, showEdgeRing = true, className = '' }: LiquidCardProps) {
  const ref = useLiquidGlass();
  return (
    <div className={`lg-card ${className}`} ref={ref}>
      <div className="lg-backdrop" />
      {showEdgeRing && <div className="lg-edge-ring" />}
      <div className="lg-tint" />
      <div className="lg-specular" />
      <div className="lg-border" />
      <div className="lg-content">{children}</div>
    </div>
  );
}

/** 液态快捷标签 */
export function LiquidChip({ label }: { label: string }) {
  return <span className="lg-chip">{label}</span>;
}
```

### 使用示例

```tsx
// app/layout.tsx 或页面根组件（注入一次 SVG Defs）
import { LiquidGlassSVGFilters } from '@/components/ui/LiquidGlass';

export default function Layout({ children }) {
  return (
    <>
      <LiquidGlassSVGFilters />
      {children}
    </>
  );
}
```

```tsx
// 业务组件
import { LiquidCard, LiquidChip } from '@/components/ui/LiquidGlass';

export function AINotificationCard() {
  return (
    <LiquidCard>
      <div className="p-6">
        <div className="lg-badge mb-4">AI 提醒</div>
        <p className="text-sm font-medium text-black/90 mb-1">设计效率分析完成</p>
        <p className="text-xs text-black/54 mt-1 leading-relaxed">
          本周 UI Review 平均耗时从 4.2h 降至 3.1h
        </p>
        <div className="mt-3 flex gap-2">
          <LiquidChip label="随便聊聊" />
          <LiquidChip label="视觉讨论" />
        </div>
        <div className="mt-4">
          <button className="lg-btn-pill">了解详情</button>
        </div>
      </div>
    </LiquidCard>
  );
}
```

---

## 浏览器兼容性

| 特性 | Chrome | Safari | Firefox | Edge |
|------|--------|--------|---------|------|
| `backdrop-filter` | ✅ 76+ | ✅ 9+ (`-webkit-`) | ✅ 103+ | ✅ 79+ |
| SVG `feTurbulence` | ✅ | ✅ | ✅ | ✅ |
| SVG `feDisplacementMap` | ✅ | ✅ | ✅ | ✅ |
| CSS Mask 渐变边框 | ✅ | ✅ (`-webkit-`) | ✅ | ✅ |
| `filter: url(#id)` + `backdrop-filter` 同元素 | ✅ | ⚠️ 部分限制 | ✅ | ✅ |
| CSS 变量 `var()` in `radial-gradient` | ✅ | ✅ | ✅ | ✅ |

> **Safari 降级**：`filter: url(#svg-filter)` 与 `backdrop-filter` 同时使用时，部分 Safari 版本渲染异常。
>
> ```css
> /* Safari 降级：去掉 SVG 折射，退化为方案一磨砂效果 */
> @supports (-webkit-hyphens: none) {
>   .lg-backdrop { filter: none; }
> }
> ```

---

## 性能建议

1. **SVG Defs 只注入一次**：在 `layout.tsx` 注入 `<LiquidGlassSVGFilters />`，不要在每个卡片内重复定义
2. **限制同屏数量**：SVG 滤镜有 GPU 渲染开销，建议页面内不超过 3-4 个 `lg-card` 同时可见
3. **不要对边框层使用 SVG 滤镜**：`feTurbulence` 的 seed 是整数离散跳跃，直接应用于 box-shadow 会造成边框抖动；滤镜只应用于 `lg-backdrop`
4. **`inset: -16px` 是必要的**：防止 SVG 滤镜在 backdrop 边缘产生透明裁切

---

## 设计参数速查表

| 元素 | 背景色 | blur | SVG 滤镜 | 边框 | 圆角 |
|------|--------|------|----------|------|------|
| 卡片（lg-card）| `rgba(255,255,255,0.08)` + tint `0.18` | `blur(16px) saturate(180%)` | `url(#lg-lens)` on backdrop | 冷白渐变 1px | `24px` |
| 次要按钮 / 胶囊 | `rgba(255,255,255,0.28)` | `blur(10px)` | — | 白渐变 1px + 顶部扫光 | `999px` |
| 幽灵按钮 | `rgba(255,255,255,0.1)` | — | — | `box-shadow 0 0 0 0.5px white` | `999px` |
| Chip | `rgba(255,255,255,0.22)` | `blur(6px)` | — | `box-shadow 0 0 0 0.5px white` | `999px` |

---

## 来源

- 灵感来源：[Apple Liquid Glass — WWDC 2025](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- CSS-Tricks 分析：[Getting Clarity on Apple's Liquid Glass](https://css-tricks.com/getting-clarity-on-apples-liquid-glass/)
- DEV 实现参考：[Recreating Apple's Liquid Glass Effect with Pure CSS](https://dev.to/kevinbism/recreating-apples-liquid-glass-effect-with-pure-css-3gpl)
- Figma 设计稿：[2025 设计工程效率提升](https://www.figma.com/design/5lIfGL2PaZqAwVqClaV0Vf/) — Node `1887:7467`
- Demo 页面：`web/src/app/glass-demo/page.tsx`
- CSS 定义：`web/src/app/glass-demo/glass-demo.css`
