-- 应用版本管理表
-- 用于支持 APP 在线更新功能

-- 创建 app_versions 表
CREATE TABLE IF NOT EXISTS app_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 版本信息
  version_code INT NOT NULL UNIQUE,           -- 版本号（递增数字，如：1, 2, 3）
  version_name VARCHAR(20) NOT NULL,          -- 版本名称（如：0.1.0, 0.1.1）

  -- APK 下载信息
  apk_url TEXT NOT NULL,                      -- APK 下载地址（支持任意存储服务）
  apk_size BIGINT,                            -- APK 文件大小（字节）
  apk_md5 VARCHAR(32),                        -- APK 文件 MD5 校验值

  -- 可选：多个下载源（灾备/CDN 加速）
  apk_mirror_urls JSONB DEFAULT '[]'::jsonb,  -- 备用下载地址数组

  -- 更新说明
  release_notes TEXT,                         -- 更新日志（支持 Markdown）
  release_notes_en TEXT,                      -- 英文更新日志（可选）

  -- 更新策略
  force_update BOOLEAN DEFAULT false,         -- 是否强制更新
  min_support_version INT,                    -- 最低支持的旧版本号

  -- 发布状态
  is_active BOOLEAN DEFAULT true,             -- 是否激活（用于灰度发布）
  published_at TIMESTAMP,                     -- 正式发布时间

  -- 审计字段
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  created_by UUID REFERENCES auth.users(id)
);

-- 创建索引
CREATE INDEX idx_app_versions_code ON app_versions(version_code DESC);
CREATE INDEX idx_app_versions_active ON app_versions(is_active) WHERE is_active = true;
CREATE INDEX idx_app_versions_published ON app_versions(published_at DESC) WHERE published_at IS NOT NULL;

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_app_versions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_app_versions_updated_at
  BEFORE UPDATE ON app_versions
  FOR EACH ROW
  EXECUTE FUNCTION update_app_versions_updated_at();

-- 添加注释
COMMENT ON TABLE app_versions IS '应用版本管理表，用于支持 APP 在线更新';
COMMENT ON COLUMN app_versions.version_code IS '版本号（递增数字）';
COMMENT ON COLUMN app_versions.version_name IS '版本名称（语义化版本）';
COMMENT ON COLUMN app_versions.apk_url IS 'APK 下载地址（支持任意存储服务，完全由后端控制）';
COMMENT ON COLUMN app_versions.apk_mirror_urls IS '备用下载地址（JSON 数组），用于灾备和加速';
COMMENT ON COLUMN app_versions.force_update IS '是否强制更新（强制更新时用户必须升级才能使用）';
COMMENT ON COLUMN app_versions.min_support_version IS '最低支持的旧版本号（低于此版本的 APP 必须更新）';
COMMENT ON COLUMN app_versions.is_active IS '是否激活（用于灰度发布，可以先创建版本但不激活）';

-- RLS 策略：公开读取（所有用户都可以检查更新）
ALTER TABLE app_versions ENABLE ROW LEVEL SECURITY;

-- 允许所有人读取激活的版本信息
CREATE POLICY "Allow public read active versions"
  ON app_versions
  FOR SELECT
  USING (is_active = true);

-- 只允许管理员进行写操作（后续可以通过后端 service_role 来操作）
CREATE POLICY "Allow admin insert"
  ON app_versions
  FOR INSERT
  WITH CHECK (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Allow admin update"
  ON app_versions
  FOR UPDATE
  USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Allow admin delete"
  ON app_versions
  FOR DELETE
  USING (auth.jwt() ->> 'role' = 'admin');

-- 插入初始版本（当前版本）
INSERT INTO app_versions (
  version_code,
  version_name,
  apk_url,
  apk_size,
  release_notes,
  force_update,
  is_active,
  published_at
) VALUES (
  1,
  '0.1.0',
  'https://github.com/notnotMyself/EE-APP/releases/download/v0.1.0/app-release.apk',
  0,
  '# 初始版本

- 🎉 AI 数字员工平台首次发布
- ✨ 支持与 AI 员工对话
- 📱 多会话管理
- 🎨 全新 UI 设计',
  false,
  true,
  NOW()
) ON CONFLICT (version_code) DO NOTHING;
