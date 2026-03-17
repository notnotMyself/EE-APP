# Chris AI Web 前端

基于 Next.js 的 Web 前端，对应 Flutter 移动端 `ai_agent_app/` 的桌面浏览器版本。

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Next.js | 16.1.6 | React 全栈框架 (App Router) |
| React | 19.2.3 | UI 框架 |
| TypeScript | ^5 | 类型安全 |
| Tailwind CSS | v4 | 样式 |
| Supabase JS | ^2.99 | 用户认证 |
| Node.js | ≥ 20 | 运行环境 |

## 快速启动

```bash
# 1. 进入 web 目录
cd web

# 2. 安装依赖
npm install

# 3. 启动开发服务器 (默认端口 3000)
npm run dev

# 或指定端口
npx next dev -p 3002
```

启动后访问 http://localhost:3000

### 其他命令

```bash
npm run build    # 生产构建
npm run start    # 启动生产服务器
npm run lint     # ESLint 检查
```

## 项目结构

```
web/
├── public/                          # 静态资源
│   ├── icons/                       # 通用图标
│   │   ├── sidebar_nav.svg          #   侧边栏导航图标
│   │   ├── new_chat.svg             #   新建对话图标
│   │   ├── review_on/off.svg        #   AI 评审 tab 图标
│   │   ├── tips_on/off.svg          #   灵感资讯 tab 图标
│   │   ├── bookshelf_on/off.svg     #   资料库 tab 图标
│   │   └── account.svg              #   账户图标
│   └── icons/chat/                  # 聊天相关图标
│       ├── account_icon.svg         #   @ 提及按钮
│       ├── send_icon.svg            #   发送按钮 (白色，活跃态)
│       ├── send_icon_dark.svg       #   发送按钮 (深色，不活跃态)
│       ├── copy.svg                 #   复制消息
│       ├── forward_icon.svg         #   分享消息
│       └── regenerate.svg           #   下载/重新生成
│
├── src/
│   ├── app/                         # 页面路由 (Next.js App Router)
│   │   ├── layout.tsx               #   全局布局 + 字体 + AuthProvider
│   │   ├── globals.css              #   全局样式 (渐变边框等)
│   │   ├── page.tsx                 #   首页 (重定向到 /chat)
│   │   ├── login/page.tsx           #   登录页
│   │   ├── chat/page.tsx            #   聊天首页 (新对话)
│   │   ├── chat/[id]/page.tsx       #   对话详情页 (WebSocket 流式)
│   │   ├── inspiration/page.tsx     #   灵感资讯页 (占位)
│   │   └── library/page.tsx         #   资料库页 (占位)
│   │
│   ├── components/                  # 共享组件
│   │   ├── Sidebar.tsx              #   左侧边栏 (导航 + 历史对话 + 删除)
│   │   ├── TopBar.tsx               #   顶部栏 (侧边栏切换 + 新对话)
│   │   ├── AtMentionPopup.tsx       #   @ 应用选择弹窗 (毛玻璃风格)
│   │   ├── AttachmentMenu.tsx       #   附件菜单弹窗
│   │   ├── PersonalitySelector.tsx  #   人设选择弹窗
│   │   └── LoginModal.tsx           #   登录弹窗
│   │
│   ├── contexts/
│   │   └── AuthContext.tsx          #   认证上下文 (Supabase Auth)
│   │
│   ├── lib/                         # 工具库
│   │   ├── api.ts                   #   REST API 客户端
│   │   ├── websocket.ts            #   WebSocket 流式对话客户端
│   │   └── supabase.ts             #   Supabase 客户端初始化
│   │
│   └── assets/images/               # 内嵌图片资源
│       ├── chris_chen_avatar.jpeg   #   Chris Chen 头像
│       └── Saly-11.png             #   登录页插画
│
├── next.config.ts                   # Next.js 配置
├── tsconfig.json                    # TypeScript 配置
└── package.json                     # 依赖与脚本
```

## 页面说明

| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | 首页 | 自动重定向到 `/chat` |
| `/login` | 登录页 | Supabase Email/Password 登录 |
| `/chat` | 聊天首页 | Chris Chen 头像 + 输入框 + 建议标签 |
| `/chat/[id]` | 对话详情 | WebSocket 实时流式对话，支持打字机效果 |
| `/inspiration` | 灵感资讯 | 占位页 |
| `/library` | 资料库 | 占位页 |

## 后端依赖

| 服务 | 地址 | 用途 |
|------|------|------|
| REST API | `https://super-niuma-cn.allawntech.com` | 对话管理 (CRUD) |
| WebSocket | `wss://super-niuma-cn.allawntech.com` | 实时流式消息 |
| Supabase | `dwesyojvzbltqtgtctpt.supabase.co` | 用户认证 |

REST API 基地址可通过环境变量覆盖：

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

## 核心流程

### 用户认证

1. 用户在登录页输入邮箱密码
2. 调用 Supabase `signInWithPassword` 获取 session
3. `AuthContext` 全局管理登录状态和 `accessToken`
4. 未登录用户访问 `/chat` 会重定向到 `/login`

### 对话流程

1. 用户在 `/chat` 输入消息，调用 REST API 创建对话
2. 跳转到 `/chat/[id]`，建立 WebSocket 连接
3. 通过 WebSocket 发送消息，接收流式 `text_chunk` 响应
4. 双层缓冲 (网络缓冲 + 打字机动画) 实现平滑渲染

### UI 设计规范

- **弹窗统一风格**: 196px 宽，毛玻璃背景 `rgba(239,239,239,0.8)`，`backdrop-filter: blur(20px)`，圆角 24px
- **输入框**: 渐变边框效果 (CSS `input-gradient-border`)
- **建议标签**: 渐变边框胶囊按钮，点击仅填充输入框
- **发送按钮**: 无输入时浅色不活跃，有输入时深色活跃
- **图标**: 来源于 Figma 设计稿，SVG 格式
