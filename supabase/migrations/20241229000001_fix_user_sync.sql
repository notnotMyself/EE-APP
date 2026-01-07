-- 修复用户同步问题
-- 1. 修改users表，让hashed_password可以为NULL（因为我们使用Supabase Auth）
ALTER TABLE public.users ALTER COLUMN hashed_password DROP NOT NULL;

-- 2. 创建或替换处理新用户的函数
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, username, created_at, updated_at)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'username', split_part(NEW.email, '@', 1)),
    NEW.created_at,
    NEW.updated_at
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. 创建触发器（如果不存在）
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- 4. 同步现有的auth.users到public.users
INSERT INTO public.users (id, email, username, created_at, updated_at)
SELECT
  id,
  email,
  COALESCE(raw_user_meta_data->>'username', split_part(email, '@', 1)) as username,
  created_at,
  COALESCE(updated_at, created_at) as updated_at
FROM auth.users
ON CONFLICT (id) DO NOTHING;

-- 5. 验证同步结果
SELECT
  'auth.users count' as table_name,
  COUNT(*) as count
FROM auth.users
UNION ALL
SELECT
  'public.users count' as table_name,
  COUNT(*) as count
FROM public.users;

