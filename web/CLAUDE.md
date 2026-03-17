# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

```bash
npm run dev          # 启动开发服务器（默认 3000 端口）
npx next dev -p 3002 # 指定端口启动
npm run build        # 生产构建
npm run lint         # ESLint 检查
```

## 技术栈

- **Next.js 16.1.6**（App Router）+ **React 19** + **TypeScript 5**
- **Tailwind CSS v4**：样式使用 `@theme inline` 块（在 `globals.css`）定义设计 token，无 `tailwind.config.js`
- **Supabase JS**：仅用于用户认证，不做数据库直连

## 架构概览

### 页面路由（`src/app/`）

| 路由 | 说明 |
|------|------|
| `/` | 重定向到 `/chat` |
| `/login` | Supabase Email/Password 登录 |
| `/chat` | 新对话入口（含建议标签） |
| `/chat/[id]` | 对话详情，WebSocket 流式消息 + 打字机动画 |
| `/inspiration`, `/library` | 占位页 |

### 核心模块

**`src/contexts/AuthContext.tsx`**
全局认证状态。提供 `useAuth()` hook，暴露 `accessToken`（Supabase JWT）、`user`、`login()`、`logout()`。所有 API 调用都需要从此处取 token。

**`src/lib/api.ts`**
REST API 客户端，封装对话 CRUD。基地址 `NEXT_PUBLIC_API_BASE`（默认 `https://super-niuma-cn.allawntech.com`）。所有函数签名第一个参数为 `token: string`。

**`src/lib/websocket.ts`**
`ConversationWebSocket` 类，管理 WebSocket 生命周期。支持指数退避重连（最多 3 次）。WS 地址由 `NEXT_PUBLIC_WS_BASE` 环境变量覆盖（默认同后端域名，协议 `wss://`）。

**`src/lib/supabase.ts`**
Supabase 客户端单例，Anon Key 已硬编码（公开可读）。

### WebSocket 消息协议

服务端 → 客户端：`connected` | `text_chunk` | `tool_use` | `tool_result` | `done` | `ping` | `error`
客户端 → 服务端：`{ type: "message", content }` | `{ type: "pong" }`

### 设计系统（`src/app/globals.css`）

自定义颜色 token（Tailwind v4 `@theme inline`）：
- `bg-bg-gray` (#F0F1F2) — 页面背景
- `bg-bg-sidebar` (#F8F8F8) — 侧边栏
- `text-secondary-text` (rgba 0,0,0,0.54)
- `text-blue` (#0066FF)

弹窗统一规格：196px 宽，毛玻璃背景 `rgba(239,239,239,0.8)` + `backdrop-filter: blur(20px)`，圆角 24px。
输入框使用 `input-gradient-border` CSS 类（渐变边框效果，定义在 `globals.css`）。

### 环境变量

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000  # 覆盖后端 REST 地址
NEXT_PUBLIC_WS_BASE=ws://localhost:8000     # 覆盖 WebSocket 地址
```
