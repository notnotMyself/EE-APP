# Supabase 邮箱验证配置指南

## 问题描述

默认情况下，Supabase 的邮箱验证链接会跳转到 `localhost`，这在移动应用中无法正常工作。

## 解决方案

我们已经为应用配置了深度链接（Deep Link），现在需要在 Supabase Dashboard 中配置相应的重定向 URL。

## 配置步骤

### 1. 登录 Supabase Dashboard

访问: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt

### 2. 配置 Redirect URLs

1. 点击左侧菜单 **Authentication** → **URL Configuration**
2. 在 **Redirect URLs** 部分添加以下 URL：

```
eeapp://auth
https://super-niuma-cn.allawntech.com/auth/callback
```

### 3. 配置 Site URL

在 **Site URL** 中设置：

```
https://super-niuma-cn.allawntech.com
```

### 4. 保存设置

点击页面底部的 **Save** 按钮保存配置。

## 深度链接说明

### Android
- **Custom Scheme**: `eeapp://auth`
- **Universal Link**: `https://super-niuma-cn.allawntech.com/*`

配置文件位置: `ai_agent_app/android/app/src/main/AndroidManifest.xml`

### iOS
- **Custom Scheme**: `eeapp://auth`

配置文件位置: `ai_agent_app/ios/Runner/Info.plist`

## 验证流程

1. 用户在应用中注册
2. 用户收到邮箱验证邮件
3. 用户点击邮件中的验证链接
4. 链接格式：`eeapp://auth?token=xxx&type=signup`
5. 应用自动打开并完成验证
6. 用户可以直接登录

## 测试步骤

1. 在真机或模拟器上运行应用
2. 使用 `@oppo.com` 邮箱注册
3. 检查邮箱，点击验证链接
4. 确认应用是否自动打开
5. 确认是否成功验证并登录

## 常见问题

### Q: 点击邮件链接后，应用没有打开？
A:
- 确保已重新编译并安装应用
- 检查 Supabase Dashboard 中的 Redirect URLs 是否正确配置
- Android: 确保已启用自动验证（`android:autoVerify="true"`）

### Q: 如何测试深度链接？
A:
```bash
# Android
adb shell am start -W -a android.intent.action.VIEW -d "eeapp://auth?token=test"

# iOS (使用 Xcode)
xcrun simctl openurl booted "eeapp://auth?token=test"
```

### Q: 生产环境 vs 开发环境？
A:
- 开发环境：使用 `eeapp://` 自定义 scheme
- 生产环境：同时支持自定义 scheme 和 Universal Link
- 如需区分环境，可以使用不同的 scheme（如 `eeapp-dev://`）

## 相关文档

- [Supabase Auth Deep Linking](https://supabase.com/docs/guides/auth/auth-deep-linking)
- [Android App Links](https://developer.android.com/training/app-links)
- [iOS Universal Links](https://developer.apple.com/ios/universal-links/)
