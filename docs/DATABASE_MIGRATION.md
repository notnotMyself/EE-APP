# 数据库迁移指南

## 快速执行

使用封装好的迁移脚本：

```bash
./scripts/migrate_db.sh
```

该脚本会自动：
1. 检查 supabase CLI 是否安装
2. 链接到 Supabase 项目
3. 列出待执行的迁移
4. 执行 `supabase db push`
5. 提供错误处理和提示

---

## 手动执行

如果需要手动执行迁移：

### 1. 链接项目（首次）

```bash
supabase link --project-ref dwesyojvzbltqtgtctpt --password "ee-for-everything1"
```

### 2. 推送迁移

```bash
supabase db push
```

### 3. 验证结果

登录 Supabase Dashboard 验证：
- 表结构是否创建
- RLS 策略是否启用
- 索引是否正确
- Storage Buckets 是否创建

---

## 项目配置

- **Project Reference**: `dwesyojvzbltqtgtctpt`
- **Project URL**: https://supabase.com/dashboard/project/dwesyojvzbltqtgtctpt
- **Database URL**: `postgresql://postgres.dwesyojvzbltqtgtctpt:ee-for-everything1@aws-0-us-east-1.pooler.supabase.com:6543/postgres`

---

## 迁移文件位置

所有迁移文件位于：`supabase/migrations/`

文件命名规范：`YYYYMMDDHHMMSS_description.sql`

示例：
- `20260114000000_add_cover_image_to_briefings.sql`
- `20260115000000_add_design_review_tables.sql`

---

## 创建新迁移

### 方法 1：使用 Supabase CLI

```bash
supabase migration new your_migration_name
```

这会在 `supabase/migrations/` 创建一个带时间戳的新文件。

### 方法 2：手动创建

1. 创建文件：`supabase/migrations/YYYYMMDDHHMMSS_your_migration.sql`
2. 编写 SQL（包含 IF NOT EXISTS 等幂等性检查）
3. 执行 `supabase db push`

---

## 迁移最佳实践

### ✅ 推荐做法

1. **幂等性**：使用 `IF NOT EXISTS`、`ON CONFLICT` 等确保可重复执行
   ```sql
   CREATE TABLE IF NOT EXISTS my_table (...);
   ALTER TABLE my_table ADD COLUMN IF NOT EXISTS my_column TEXT;
   ```

2. **RLS 策略**：总是配置 Row Level Security
   ```sql
   ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;

   CREATE POLICY "Users can read own data"
     ON my_table FOR SELECT
     USING (auth.uid() = user_id);
   ```

3. **索引**：为常用查询字段创建索引
   ```sql
   CREATE INDEX IF NOT EXISTS idx_table_column ON my_table(column);
   ```

4. **注释**：添加表和列的注释
   ```sql
   COMMENT ON TABLE my_table IS 'Table description';
   COMMENT ON COLUMN my_table.my_column IS 'Column description';
   ```

5. **Storage Buckets**：使用 `ON CONFLICT DO NOTHING`
   ```sql
   INSERT INTO storage.buckets (id, name, public)
   VALUES ('my-bucket', 'my-bucket', true)
   ON CONFLICT (id) DO NOTHING;
   ```

### ❌ 避免的做法

- ❌ 直接删除表或列（会导致数据丢失）
- ❌ 不加 `IF NOT EXISTS` 的 CREATE 语句
- ❌ 忘记配置 RLS 策略
- ❌ 在迁移中包含测试数据（应该用 seed）

---

## 回滚迁移

Supabase CLI 不直接支持回滚，需要手动处理：

1. 创建新的迁移来撤销更改
2. 例如，如果添加了列，创建迁移删除该列：
   ```sql
   ALTER TABLE my_table DROP COLUMN IF EXISTS my_column;
   ```

---

## 常见问题

### Q: 迁移失败怎么办？

1. 查看错误信息
2. 检查 SQL 语法
3. 检查是否与现有 schema 冲突
4. 在本地测试 SQL（使用 `supabase start` 启动本地实例）
5. 修复后重新执行 `supabase db push`

### Q: 如何查看已应用的迁移？

```sql
SELECT * FROM supabase_migrations.schema_migrations
ORDER BY version DESC;
```

### Q: 本地开发如何处理迁移？

```bash
# 启动本地 Supabase
supabase start

# 推送到本地
supabase db push --local

# 重置本地数据库
supabase db reset --local
```

---

## 测试迁移

在推送到生产之前，务必在本地测试：

```bash
# 1. 启动本地 Supabase
supabase start

# 2. 推送迁移
supabase db push --local

# 3. 验证表结构
psql postgresql://postgres:postgres@localhost:54322/postgres \
  -c "\d your_table_name"

# 4. 测试 RLS 策略
# 在 Supabase Dashboard (本地) 中手动测试

# 5. 如果有问题，重置并修复
supabase db reset --local
```

---

## CI/CD 集成

在 GitHub Actions 中自动执行迁移：

```yaml
name: Database Migration

on:
  push:
    branches: [main]
    paths:
      - 'supabase/migrations/**'

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Supabase CLI
        uses: supabase/setup-cli@v1

      - name: Link project
        run: |
          supabase link --project-ref ${{ secrets.SUPABASE_PROJECT_REF }} \
            --password ${{ secrets.SUPABASE_DB_PASSWORD }}

      - name: Push migrations
        run: supabase db push
```

---

## 维护建议

1. **定期备份**：在执行重要迁移前备份数据库
2. **版本控制**：所有迁移文件提交到 Git
3. **文档记录**：在迁移 SQL 中添加详细注释
4. **团队沟通**：迁移前通知团队，避免冲突
5. **监控验证**：迁移后检查应用日志和错误率

---

## 相关资源

- [Supabase CLI 文档](https://supabase.com/docs/guides/cli)
- [Supabase Migrations 指南](https://supabase.com/docs/guides/cli/managing-database-migrations)
- [PostgreSQL 最佳实践](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
