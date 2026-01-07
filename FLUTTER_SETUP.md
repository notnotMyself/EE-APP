# Flutter项目设置指南

## 📱 步骤1: 创建Flutter项目

在终端中运行：

```bash
cd /Users/80392083/develop/ee_app_claude
./init_flutter.sh
```

这会创建一个名为 `ai_agent_app` 的Flutter项目。

---

## 📦 步骤2: 替换配置文件

项目创建完成后，替换配置文件：

```bash
cd ai_agent_app

# 替换pubspec.yaml
cp ../flutter_config/pubspec.yaml ./pubspec.yaml

# 替换整个lib目录
rm -rf lib
cp -r ../flutter_config/lib ./lib

# 安装依赖
flutter pub get
```

---

## 🏗️ 项目结构

```
ai_agent_app/
├── lib/
│   ├── main.dart                           # 应用入口
│   ├── core/
│   │   ├── config/
│   │   │   └── app_config.dart            # Supabase和API配置
│   │   ├── theme/
│   │   │   └── app_theme.dart             # 主题配置
│   │   └── router/
│   │       └── app_router.dart            # 路由配置(GoRouter)
│   └── features/
│       ├── auth/
│       │   └── presentation/pages/
│       │       ├── login_page.dart        # 登录页
│       │       └── register_page.dart     # 注册页
│       ├── home/
│       │   └── presentation/pages/
│       │       └── home_page.dart         # 首页
│       ├── agents/
│       │   └── presentation/pages/
│       │       └── agents_page.dart       # AI员工列表
│       ├── conversations/
│       │   └── presentation/pages/
│       │       └── conversation_page.dart # 对话页
│       ├── alerts/
│       │   └── presentation/pages/
│       │       └── alerts_page.dart       # 提醒列表
│       └── profile/
│           └── presentation/pages/
│               └── profile_page.dart      # 个人中心
└── pubspec.yaml                            # 依赖配置
```

---

## 🔑 核心依赖

```yaml
# Supabase
supabase_flutter: ^2.5.0

# 状态管理
flutter_riverpod: ^2.5.1

# 路由
go_router: ^14.0.0

# HTTP客户端
dio: ^5.4.0

# SSE (Server-Sent Events)
eventsource_client: ^1.1.1

# UI
google_fonts: ^6.1.0
```

---

## ▶️ 步骤3: 运行项目

### iOS模拟器
```bash
flutter run
```

### Android模拟器
```bash
# 先启动Android模拟器，然后
flutter run
```

### Chrome (Web调试)
```bash
flutter run -d chrome
```

---

## 🔧 配置说明

### Supabase配置 (已配置)

在 `lib/core/config/app_config.dart` 中：

```dart
static const String supabaseUrl = 'https://dwesyojvzbltqtgtctpt.supabase.co';
static const String supabaseAnonKey = 'eyJhbGciOi...';
```

### FastAPI配置 (本地开发)

```dart
static const String apiBaseUrl = 'http://localhost:8000';
```

如果在真机测试，需要改为电脑的局域网IP：
```dart
static const String apiBaseUrl = 'http://192.168.x.x:8000';
```

---

## 🎨 当前功能

### ✅ 已实现的基础功能

1. **应用框架**
   - Material Design 3主题
   - 深色/浅色模式支持
   - GoRouter路由管理
   - Riverpod状态管理

2. **认证页面**
   - 登录页面 (UI完成)
   - 注册页面 (UI完成)
   - 表单验证

3. **主页**
   - 欢迎页面
   - 导航结构

4. **占位页面**
   - AI员工列表页
   - 对话页
   - 提醒列表页
   - 个人中心页

### 🚧 待实现的功能

1. **认证逻辑**
   - Supabase Auth集成
   - Token管理
   - 登录状态持久化

2. **AI员工功能**
   - 从Supabase查询agents
   - 订阅/取消订阅
   - Agent详情页

3. **对话功能**
   - 创建对话
   - SSE流式接收AI响应
   - 消息列表
   - 发送消息

4. **提醒功能**
   - Alerts列表
   - 实时订阅(Supabase Realtime)
   - 点击alert进入对话

---

## 🧪 测试运行

运行项目后，你应该看到：

1. **登录页** - 带有邮箱和密码输入框
2. **注册页** - 从登录页点击"立即注册"进入
3. **首页** - 登录后显示欢迎页面

目前登录功能是**临时实现**，点击登录直接跳转到首页（未连接Supabase Auth）。

---

## 🔗 下一步开发

### Phase 1: 认证功能
1. 实现Supabase Auth登录
2. 实现注册功能
3. Token管理和自动刷新

### Phase 2: AI员工列表
1. 查询agents表
2. 显示AI员工卡片
3. 订阅功能

### Phase 3: 对话功能
1. 创建conversation
2. SSE流式对话
3. 消息历史

### Phase 4: 实时提醒
1. Alerts列表
2. Realtime订阅
3. Push通知

---

## 📞 常见问题

### Q: Flutter命令找不到？
A: 确保Flutter已添加到PATH:
```bash
export PATH="$PATH:/path/to/flutter/bin"
```

### Q: 依赖安装失败？
A: 清理缓存重试:
```bash
flutter clean
flutter pub get
```

### Q: iOS编译错误？
A: 更新CocoaPods:
```bash
cd ios
pod install
```

---

## 🎯 快速开始

```bash
# 1. 创建项目
cd /Users/80392083/develop/ee_app_claude
./init_flutter.sh

# 2. 替换配置
cd ai_agent_app
cp ../flutter_config/pubspec.yaml ./
rm -rf lib && cp -r ../flutter_config/lib ./

# 3. 安装依赖
flutter pub get

# 4. 运行
flutter run
```

完成后，你应该能看到登录页面！
