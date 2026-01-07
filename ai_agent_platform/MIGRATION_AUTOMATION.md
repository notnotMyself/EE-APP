# Database Migration - Automation Guide

## 问题总结

我们遇到的核心问题：
- ✅ Supabase CLI 已安装并link成功
- ❌ 直接数据库连接失败（所有格式都尝试过）
- ❌ psql未安装
- ✅ psycopg2可用但连接字符串不正确

## 最佳自动化方案

### 选项A：使用Supabase CLI + 正确的项目结构 ⭐️ 推荐

```bash
# 1. 初始化Supabase项目结构
cd ai_agent_platform/backend
supabase init

# 2. 将迁移文件移到正确位置
mkdir -p supabase/migrations
cp migrations/001_initial_schema.sql supabase/migrations/20241228_initial_schema.sql

# 3. 执行迁移（自动化）
supabase db push --linked
```

### 选项B：使用正确的连接字符串

从Dashboard获取连接字符串后：

```python
# save_connection.py
import os

# 从Dashboard复制的完整连接字符串
CONNECTION_STRING = "postgresql://postgres:[PASSWORD]@actual-host:port/postgres"

# 保存到环境变量
with open('.env.migration', 'w') as f:
    f.write(f"DATABASE_URL={CONNECTION_STRING}\n")

print("✅ Connection string saved!")
```

然后执行迁移：
```bash
python3 run_migration_with_env.py
```

### 选项C：使用Supabase Management API

```python
# 使用service_role key执行SQL
import requests

url = "https://dwesyojvzbltqtgtctpt.supabase.co/rest/v1/rpc/exec_sql"
headers = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}

# 注意：这需要在数据库中创建一个RPC函数
```

## 推荐流程（最实用）

### 立即：手动执行一次
1. 在Dashboard运行SQL（2分钟）
2. 验证表创建成功

### 未来：建立自动化
1. 使用Supabase CLI的正确结构
2. 所有后续迁移都通过 `supabase db push`
3. 集成到CI/CD

## 下一步

**立即操作**（二选一）：

1. **快速方案**：复制实际的连接字符串给我
   - 我会立即执行迁移
   - 同时设置好自动化工具

2. **标准方案**：在Dashboard手动运行一次
   - 然后我建立正确的Supabase CLI结构
   - 后续所有迁移都自动化

哪个方案你更prefer?
