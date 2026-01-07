# 创建测试数据说明

seed.sql文件包含5个内置AI员工的测试数据。

## 手动执行方式

### 方式1: Supabase Dashboard SQL Editor (推荐)

1. 打开: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt/sql/new

2. 复制 `supabase/seed.sql` 的全部内容

3. 粘贴到SQL Editor中

4. 点击 "RUN" 执行

### 方式2: 使用psql (如果已安装)

```bash
# 从Supabase Dashboard获取连接字符串
# Settings -> Database -> Connection string -> URI

psql "postgresql://postgres.dwesyojvzbltqtgtctpt:PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres" \
  -f supabase/seed.sql
```

## 验证数据

执行后可以查询验证:

```sql
-- 查看创建的AI员工
SELECT id, name, role, is_builtin, is_active
FROM agents
WHERE is_builtin = true;

-- 应该看到5个内置AI员工:
-- 1. 研发效能分析官 (dev_efficiency_analyst)
-- 2. NPS洞察官 (nps_analyst)
-- 3. 竞品情报官 (competitor_analyst)
-- 4. 舆情哨兵 (sentiment_monitor)
-- 5. AI营运助理 (operations_assistant)
```

## 下一步

创建测试数据后，就可以开始Flutter开发了！
