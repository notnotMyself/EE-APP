-- ========================================
-- 隐私政策和用户协议表
-- 支持多版本管理和用户同意记录
-- ========================================

-- Step 1: 创建法律文档表
CREATE TABLE IF NOT EXISTS legal_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_type VARCHAR(50) NOT NULL, -- 'privacy_policy' | 'terms_of_service'
  version VARCHAR(20) NOT NULL, -- 版本号（如 '1.0.0'）
  title TEXT NOT NULL,
  content TEXT NOT NULL, -- Markdown格式内容
  effective_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- 确保每种文档类型的版本唯一
  CONSTRAINT unique_document_version UNIQUE (document_type, version)
);

-- Step 2: 创建用户同意记录表
CREATE TABLE IF NOT EXISTS user_consents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  document_id UUID NOT NULL REFERENCES legal_documents(id) ON DELETE CASCADE,
  document_type VARCHAR(50) NOT NULL,
  document_version VARCHAR(20) NOT NULL,
  consented_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ip_address VARCHAR(50), -- 记录IP地址（可选，用于合规审计）
  user_agent TEXT, -- 记录用户代理（可选）

  -- 确保用户对同一文档只同意一次
  CONSTRAINT unique_user_consent UNIQUE (user_id, document_id)
);

-- Step 3: 创建索引
CREATE INDEX IF NOT EXISTS idx_legal_documents_type_active
  ON legal_documents(document_type, is_active);

CREATE INDEX IF NOT EXISTS idx_user_consents_user_id
  ON user_consents(user_id);

CREATE INDEX IF NOT EXISTS idx_user_consents_document_type
  ON user_consents(user_id, document_type);

-- Step 4: 启用RLS（行级安全）
ALTER TABLE legal_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_consents ENABLE ROW LEVEL SECURITY;

-- Step 5: 创建RLS策略

-- 法律文档：所有人可读（公开）
DROP POLICY IF EXISTS "Legal documents are publicly readable" ON legal_documents;
CREATE POLICY "Legal documents are publicly readable"
  ON legal_documents FOR SELECT
  USING (true);

-- 用户同意记录：仅用户本人可读
DROP POLICY IF EXISTS "Users can read own consents" ON user_consents;
CREATE POLICY "Users can read own consents"
  ON user_consents FOR SELECT
  USING (auth.uid() = user_id);

-- 用户同意记录：仅用户本人可插入
DROP POLICY IF EXISTS "Users can insert own consents" ON user_consents;
CREATE POLICY "Users can insert own consents"
  ON user_consents FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Step 6: 插入初始法律文档（v1.0）

-- 隐私政策 v1.0
INSERT INTO legal_documents (document_type, version, title, content, effective_date, is_active)
VALUES (
  'privacy_policy',
  '1.0.0',
  'AI数字员工平台 隐私政策',
  E'# 隐私政策

**生效日期**: 2026年1月23日
**版本**: 1.0.0

欢迎使用AI数字员工平台（以下简称"本平台"或"我们"）。我们重视您的隐私，并致力于保护您的个人信息。本隐私政策说明我们如何收集、使用、存储和保护您的信息。

## 1. 信息收集

### 1.1 我们收集的信息

- **账户信息**: 注册时您提供的邮箱地址、用户名
- **使用数据**: 您与AI员工的对话记录、创建的任务、收到的简报
- **设备信息**: 设备型号、操作系统版本、应用版本
- **日志信息**: IP地址、访问时间、使用功能等日志数据

### 1.2 信息收集方式

- 您主动提供的信息（注册、填写表单等）
- 自动收集的信息（设备标识、日志等）
- 第三方服务收集（如极光推送）

## 2. 信息使用

我们收集信息的目的包括：

- **提供服务**: 创建和管理您的账户，提供AI对话和任务管理功能
- **改善产品**: 分析使用情况，优化产品功能和性能
- **通知推送**: 发送重要简报和系统通知
- **安全保障**: 检测和防止欺诈、滥用和非法活动
- **客户支持**: 响应您的问题和请求

## 3. 信息存储与安全

- **数据存储**: 我们使用Supabase（基于PostgreSQL）存储数据，数据中心位于新加坡
- **加密传输**: 所有数据通过HTTPS/TLS加密传输
- **访问控制**: 严格限制员工对用户数据的访问权限
- **备份机制**: 定期备份数据以防丢失

## 4. 第三方服务

我们使用以下第三方服务，它们可能收集和处理您的信息：

- **Supabase**: 数据库和认证服务
- **极光推送(JPush)**: 消息推送服务
- **Anthropic Claude**: AI对话服务（您的对话内容会发送给Claude API）

## 5. 信息共享

我们不会出售您的个人信息。我们仅在以下情况下共享信息：

- **经您同意**: 在获得您明确同意的情况下
- **服务提供商**: 与帮助我们提供服务的第三方（如上述服务）
- **法律要求**: 遵守法律法规、法院命令或政府要求
- **保护权益**: 保护我们或他人的权利、财产和安全

## 6. 您的权利

您拥有以下权利：

- **访问权**: 查看我们持有的您的个人信息
- **更正权**: 更正不准确或不完整的信息
- **删除权**: 请求删除您的账户和数据
- **反对权**: 反对某些类型的数据处理
- **导出权**: 请求导出您的数据副本

如需行使这些权利，请联系我们：support@eeplatform.com

## 7. 儿童隐私

本平台不向13岁以下儿童提供服务。如果我们发现无意中收集了儿童信息，将立即删除。

## 8. Cookie和跟踪技术

我们使用Cookie和类似技术来：
- 保持登录状态
- 记住用户偏好设置
- 分析使用情况

您可以通过浏览器设置管理Cookie偏好。

## 9. 隐私政策更新

我们可能不时更新本隐私政策。重大更改时，我们会通过应用内通知或邮件通知您。继续使用服务即表示您接受更新后的政策。

## 10. 联系我们

如对本隐私政策有任何疑问，请联系：
- 邮箱: support@eeplatform.com
- 地址: [公司地址待补充]

---

_最后更新: 2026年1月23日_',
  '2026-01-23 00:00:00+00',
  true
)
ON CONFLICT (document_type, version) DO NOTHING;

-- 用户协议 v1.0
INSERT INTO legal_documents (document_type, version, title, content, effective_date, is_active)
VALUES (
  'terms_of_service',
  '1.0.0',
  'AI数字员工平台 用户协议',
  E'# 用户服务协议

**生效日期**: 2026年1月23日
**版本**: 1.0.0

欢迎使用AI数字员工平台。在使用我们的服务之前，请仔细阅读并理解本协议。

## 1. 服务说明

### 1.1 服务内容

本平台提供AI驱动的数字员工服务，包括但不限于：
- AI对话和咨询
- 任务管理和执行
- 数据分析和简报生成
- 消息推送和通知

### 1.2 服务限制

- 本服务仅供合法用途使用
- AI回复仅供参考，不构成专业建议
- 我们不保证服务100%可用和无错误

## 2. 账户注册与管理

### 2.1 注册要求

- 您必须年满13岁
- 提供真实、准确的注册信息
- 保护账户安全，不得共享账户

### 2.2 账户责任

您对使用您账户进行的所有活动负责，包括：
- 发送的消息和创建的内容
- 账户安全（密码保护）
- 遵守本协议和适用法律

## 3. 用户行为规范

禁止以下行为：

- **非法活动**: 使用服务进行任何违法活动
- **滥用服务**: 恶意攻击、过度请求、自动化脚本
- **侵权行为**: 侵犯他人知识产权、隐私或其他权利
- **有害内容**: 发送垃圾信息、恶意软件、暴力或仇恨内容
- **欺诈行为**: 冒充他人、提供虚假信息

违反规范可能导致账户暂停或终止。

## 4. 知识产权

### 4.1 平台所有权

本平台的所有内容、功能、代码、设计和商标均归我们所有，受知识产权法保护。

### 4.2 用户内容

- 您保留对自己创建内容的所有权
- 您授予我们使用、存储、处理这些内容以提供服务的许可
- 我们不会将您的对话内容用于其他目的（AI训练除外，如Anthropic的使用政策）

## 5. 免责声明

### 5.1 AI限制

- AI回复可能不准确、不完整或过时
- AI回复不构成法律、医疗、财务或其他专业建议
- 重要决策前请咨询专业人士

### 5.2 服务可用性

- 服务可能因维护、升级或不可抗力而中断
- 我们不保证服务永久运行
- 我们不对服务中断造成的损失负责

### 5.3 第三方服务

- 我们集成的第三方服务（如Claude API）受其自身条款约束
- 我们不对第三方服务的行为负责

## 6. 责任限制

在法律允许的最大范围内：

- 我们的责任限于您支付的费用（如适用）
- 我们不对间接、偶然或惩罚性损害负责
- 我们不对数据丢失、业务中断或利润损失负责

## 7. 服务变更与终止

### 7.1 我们的权利

我们保留以下权利：
- 随时修改、暂停或终止服务
- 更新本协议（重大更改会提前通知）
- 拒绝为任何人提供服务

### 7.2 您的权利

您可以随时：
- 停止使用服务
- 删除您的账户
- 导出您的数据

## 8. 争议解决

### 8.1 适用法律

本协议受[国家/地区]法律管辖，不考虑法律冲突条款。

### 8.2 争议处理

- 首先尝试友好协商解决
- 无法协商解决的，提交[仲裁机构/法院]

## 9. 其他条款

### 9.1 完整协议

本协议与隐私政策构成您与我们之间的完整协议。

### 9.2 可分割性

如协议任何条款无效，其余条款仍然有效。

### 9.3 弃权

我们未行使某项权利不构成对该权利的放弃。

## 10. 联系我们

如对本协议有任何疑问：
- 邮箱: support@eeplatform.com
- 地址: [公司地址待补充]

---

**重要提示**: 使用本服务即表示您已阅读、理解并同意受本协议约束。如不同意，请勿使用服务。

_最后更新: 2026年1月23日_',
  '2026-01-23 00:00:00+00',
  true
)
ON CONFLICT (document_type, version) DO NOTHING;

-- 添加注释
COMMENT ON TABLE legal_documents IS '法律文档表 - 存储隐私政策和用户协议';
COMMENT ON TABLE user_consents IS '用户同意记录表 - 记录用户对法律文档的同意';
COMMENT ON COLUMN legal_documents.document_type IS '文档类型: privacy_policy(隐私政策) | terms_of_service(用户协议)';
COMMENT ON COLUMN legal_documents.content IS 'Markdown格式的文档内容';
COMMENT ON COLUMN legal_documents.is_active IS '是否为当前有效版本（用于支持多版本）';
COMMENT ON COLUMN user_consents.ip_address IS 'IP地址（可选，用于合规审计）';
