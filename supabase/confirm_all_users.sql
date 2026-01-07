-- 确认所有未验证的用户
-- 这个脚本会让所有注册用户都可以直接登录

-- 1. 查看所有未确认的用户
SELECT
  id,
  email,
  created_at,
  email_confirmed_at,
  CASE
    WHEN email_confirmed_at IS NULL THEN '未确认'
    ELSE '已确认'
  END as status
FROM auth.users
ORDER BY created_at DESC;

-- 2. 确认所有未验证的用户
UPDATE auth.users
SET
  email_confirmed_at = COALESCE(email_confirmed_at, now()),
  updated_at = now()
WHERE email_confirmed_at IS NULL;

-- 3. 验证结果
SELECT
  email,
  email_confirmed_at,
  '✅ 已确认' as status
FROM auth.users
ORDER BY created_at DESC;
