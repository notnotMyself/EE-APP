# 邮箱验证重定向解决方案

## 问题描述

用户可能在不同设备上打开验证邮件：
- 📱 在手机上打开：应该直接打开应用
- 💻 在电脑上打开：应该显示友好提示页面

## 推荐方案

### 方案A：HTTPS Universal Link（推荐用于生产）

**原理**：使用真实的 HTTPS 链接，智能判断打开方式

**配置步骤**：

#### 1. Supabase 配置

```
Site URL: https://super-niuma-cn.allawntech.com/auth/callback
Redirect URLs:
  - https://super-niuma-cn.allawntech.com/auth/callback
  - eeapp://auth  (备用)
```

#### 2. 在服务器创建重定向页面

需要在 `https://super-niuma-cn.allawntech.com/auth/callback` 创建一个 HTML 页面：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>邮箱验证中...</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 16px;
            text-align: center;
            max-width: 400px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .message {
            color: #333;
            margin: 20px 0;
        }
        .desktop-only {
            display: none;
        }
        @media (min-width: 768px) {
            .mobile-only { display: none; }
            .desktop-only { display: block; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="spinner mobile-only"></div>
        <h2 class="mobile-only">验证中...</h2>
        <p class="mobile-only message">正在打开应用...</p>

        <h2 class="desktop-only">📱 请在手机上打开</h2>
        <p class="desktop-only message">
            验证链接需要在安装了应用的手机上打开。<br>
            请在手机上检查您的邮箱。
        </p>

        <div id="error" style="color: #e53e3e; margin-top: 20px; display: none;">
            <p>未安装应用？</p>
            <a href="https://your-download-link.com"
               style="color: #667eea; text-decoration: none; font-weight: bold;">
                下载应用
            </a>
        </div>
    </div>

    <script>
        // 获取 URL 中的参数
        const params = new URLSearchParams(window.location.hash.substring(1));
        const token = params.get('access_token');
        const type = params.get('type');

        // 检测是否是移动设备
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

        if (isMobile) {
            // 尝试打开应用
            const deepLink = `eeapp://auth#access_token=${token}&type=${type}`;
            window.location.href = deepLink;

            // 3秒后如果还没打开，显示错误提示
            setTimeout(() => {
                document.getElementById('error').style.display = 'block';
            }, 3000);
        }
    </script>
</body>
</html>
```

#### 3. 配置 Universal Link（Android App Links）

在服务器根目录创建 `.well-known/assetlinks.json`:

```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.ee.aiagent",
    "sha256_cert_fingerprints": [
      "YOUR_APP_SHA256_FINGERPRINT"
    ]
  }
}]
```

获取 SHA256 指纹：
```bash
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android
```

### 方案B：纯自定义 Scheme（快速方案）

**优点**：无需服务器配置
**缺点**：电脑上打开会报错

**Supabase 配置**：
```
Site URL: eeapp://auth
Redirect URLs:
  - eeapp://auth
```

**用户体验**：
- 📱 手机：完美
- 💻 电脑：显示"无法识别协议"错误

### 方案C：混合方案（平衡方案）

同时配置两种方式，让 Supabase 邮件中使用 HTTPS，但提供 fallback：

**Supabase 配置**：
```
Site URL: https://super-niuma-cn.allawntech.com/auth/callback
Redirect URLs:
  - https://super-niuma-cn.allawntech.com/auth/callback
  - eeapp://auth
```

**邮件模板自定义**（在 Supabase Dashboard）：

在 `Authentication > Email Templates > Confirm signup` 中修改：

```html
<h2>确认您的注册</h2>
<p>请点击下面的按钮验证您的邮箱：</p>
<p>
  <a href="{{ .ConfirmationURL }}">验证邮箱</a>
</p>
<p style="color: #666; font-size: 12px;">
  请在安装了应用的手机上打开此链接。
  如果链接无法打开，请复制以下链接在应用中手动验证：
  {{ .ConfirmationURL }}
</p>
```

## 推荐实施步骤

### 快速上线（当前）

1. 使用方案B（纯自定义 scheme）
2. 在注册页面提示用户"请在手机上验证邮箱"
3. Supabase 配置：
   - Site URL: `eeapp://auth`
   - Redirect URLs: `eeapp://auth`

### 完善版（后续）

1. 在服务器配置重定向页面
2. 升级到方案A（Universal Link）
3. 改善跨平台体验

## 当前建议

鉴于你们已经有域名 `https://super-niuma-cn.allawntech.com`，建议：

**立即配置**：
```
Site URL: eeapp://auth
Redirect URLs: eeapp://auth
```

**在注册页面添加提示**：
"请在手机上打开验证邮件完成注册"

**后续优化**：
配置服务器重定向页面，升级为方案A
