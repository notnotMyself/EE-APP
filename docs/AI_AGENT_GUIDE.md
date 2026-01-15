# AI 员工定义与管理指南

## 📊 当前 AI 员工清单

### 1. AI资讯追踪官 (ai_news_crawler)

**角色定位**: 信息前哨官
**核心价值**: 让团队不错过关键行业动态

| 项目 | 详情 |
|------|------|
| **ID** | `ai_news_crawler` |
| **模型** | Claude Sonnet 4.5 |
| **状态** | ✅ 生产运行中 |
| **可见性** | 公开（App 市场可订阅） |

**核心能力**:
- 📰 爬取 AI 行业资讯（ai-bot.cn, BestBlogs.dev）
- 📊 生成每日/每周摘要报告
- 🎯 智能过滤高价值内容
- 📱 推送到用户信息流

**定时任务**:
- 每天 9:00 - 爬取每日资讯并生成简报

**技能清单** (Skills):
1. `news_crawler.py` - 爬取和分析资讯（超时 10 分钟）

**工具权限**:
- Read, Write, Bash, Grep, Glob, WebFetch

**它替谁负责？**
- 技术主管/产品经理 - 不用每天浏览各种资讯网站

**它盯什么长期问题？**
- AI 行业是否有重大技术突破？
- 竞品是否发布新产品？
- 行业监管是否有新动向？

**什么时候会主动找人？**
- 发现 ≥3 篇高分文章（≥90 分）时推送
- 发现重大新闻（融资、新模型发布）时推送
- 用户订阅了该 Agent 且有新内容时推送

---

### 2. 研发效能分析官 (dev_efficiency_analyst)

**角色定位**: 效率守护者
**核心价值**: 让团队持续优化研发流程

| 项目 | 详情 |
|------|------|
| **ID** | `dev_efficiency_analyst` |
| **模型** | Claude Sonnet 4.5 |
| **状态** | ✅ 生产运行中 |
| **可见性** | 公开（App 市场可订阅） |

**核心能力**:
- 📈 监控代码审查效率（Gerrit 数据库）
- 🏗️ 分析构建效率（门禁构建数据库）
- 🔍 检测异常趋势和瓶颈
- 📊 生成效能报告和优化建议

**定时任务**:
- 工作日 9:00 - 生成每日效能简报
- 周五 18:00 - 生成周度分析报告（已禁用）

**技能清单** (Skills):
1. `build_analysis.py` - 分析 CI/CD 构建数据（超时 5 分钟）

**工具权限**:
- Read, Write, Bash, Grep, Glob, WebFetch

**数据源**:
- Gerrit MySQL 数据库（只读）
- 门禁构建 MySQL 数据库（只读）

**它替谁负责？**
- 研发 Leader/效能团队 - 不用每天手动查看和分析数据

**它盯什么长期问题？**
- Review 队列是否积压？
- 构建耗时是否恶化？
- 哪些模块/平台效率最差？

**什么时候会主动找人？**
- Review P95 耗时超过阈值（2 小时）
- 构建效率周环比下降 > 20%
- 发现明显的瓶颈或异常趋势

---

### 3. Chris 设计评审员 (design_validator)

**角色定位**: 设计质量把关者
**核心价值**: 用 AI 视觉能力辅助设计审查

| 项目 | 详情 |
|------|------|
| **ID** | `design_validator` |
| **模型** | Claude Opus 4.5（支持视觉分析） |
| **状态** | ✅ 已配置 |
| **可见性** | 公开 |

**核心能力**:
- 👁️ 视觉分析设计稿（支持多模态）
- ✅ 交互可用性验证（Jakob Nielsen 5 维度）
- 🎨 视觉一致性检查（颜色、字体、间距）
- 🆚 多方案对比分析
- 📚 知识库管理（ADR 风格）

**定时任务**: 无（按需调用）

**技能清单** (Skills):
1. `vision_analysis.py` - 视觉分析（超时 5 分钟）
2. `interaction_check.py` - 交互验证（超时 5 分钟）
3. `visual_consistency.py` - 一致性检查（超时 5 分钟）
4. `compare_designs.py` - 方案对比（超时 5 分钟）
5. `search_cases.py` - 检索历史案例（超时 1 分钟）

**工具权限**:
- Read, Write, Grep, Glob

**知识库**:
- design_decisions/ - 设计决策（ADR）
- design_guidelines/ - 设计规范
- case_studies/ - 成功案例
- user_feedback/ - 用户反馈

**它替谁负责？**
- 设计师/设计 Leader - 提供第二双眼睛审查设计

**它盯什么长期问题？**
- 设计是否符合可用性原则？
- 设计是否与品牌规范一致？
- 历史上类似设计的经验教训是什么？

**什么时候会主动找人？**
- 发现严重可用性问题（P0）
- 发现与品牌规范明显不一致
- 需要设计决策时

---

### 4. EE 研发员工 (ee_developer)

**角色定位**: 代码执行者
**核心价值**: 自动化代码修改和测试流程

| 项目 | 详情 |
|------|------|
| **ID** | `ee_developer` |
| **模型** | Claude Opus 4.5 |
| **状态** | ✅ 已配置 |
| **可见性** | 公开 |

**核心能力**:
- 💻 代码修改（Edit 工具）
- 🧪 自动化测试（pytest, flutter test）
- 🌿 Git 分支管理（feature 分支隔离）
- 📝 代码审查（静态分析）
- 🔀 创建 Pull Request

**定时任务**: 无（按需调用）

**技能清单** (Skills):
1. `git_operations.py` - Git 操作（超时 10 分钟）
2. `code_review.py` - 代码审查（超时 5 分钟）
3. `test_runner.py` - 运行测试（超时 10 分钟）

**工具权限**:
- Read, Write, Edit, Bash, Grep, Glob

**工作区安全**:
- 允许路径: `ee_app_claude/**`
- 拒绝访问: `.env`, `*.key`, `*secret*`

**安全铁律**:
- ❌ 永不直接修改 main 分支
- ✅ 所有修改在 feature 分支上
- ✅ 修改后必须运行测试
- ✅ 重要文件修改需确认

**它替谁负责？**
- 开发者 - 自动化执行代码修改任务

**它盯什么长期问题？**
- 代码是否符合规范？
- 测试是否通过？
- 是否遵循 Git 最佳实践？

**什么时候会主动找人？**
- 测试失败需要人工介入
- 修改重要文件需要确认
- 遇到 Git 冲突无法自动解决

---

## 🎯 AI 员工设计原则

### 1. 三问原则（必须回答）

每个 AI 员工必须明确回答：

| 问题 | 说明 | 示例（AI资讯追踪官） |
|------|------|---------------------|
| **它替谁负责？** | 这个 Agent 代替哪个角色的哪部分职责？ | 替技术主管盯行业动态 |
| **它盯什么长期问题？** | 它持续关注的核心问题是什么？ | AI 行业是否有重大突破？ |
| **什么时候会主动找人？** | 在什么情况下它会推送信息？ | 发现高价值内容（≥90 分） |

### 2. 信息流铁律（避免打扰）

- **一天最多 5 条** - 不要用无价值信息打扰用户
- **宁可不发，也不刷存在感** - 如果不确定是否值得发，就不发
- **每一条都必须能接上对话** - 用户看完会想问"为什么"或"怎么办"

### 3. 能力定义原则

**核心能力 vs 辅助能力**:
- 核心能力：Agent 的主要价值（如爬取资讯、分析效能）
- 辅助能力：支持核心能力的工具（如读写文件、执行脚本）

**自动化 vs 按需调用**:
- 自动化：定时执行，主动推送（如每日资讯简报）
- 按需调用：用户发起对话，响应需求（如设计评审）

---

## 📋 如何定义新的 AI 员工

### 步骤 1: 角色规划

使用三问原则明确角色：

```yaml
角色名称: [中文名称]
英文ID: [role_id]

# 三问
它替谁负责: [具体角色和职责]
它盯什么长期问题: [3-5个核心问题]
什么时候会主动找人: [触发条件]

# 价值主张
核心价值: [一句话说明为什么需要这个Agent]
使用场景: [典型使用场景]
```

### 步骤 2: 创建 Agent 目录

```bash
cd backend/agents
mkdir <role_id>
cd <role_id>

# 创建必要文件
touch agent.yaml           # Agent 配置
touch CLAUDE.md            # 角色定义
mkdir -p .claude/skills    # Skills 脚本目录
mkdir reports              # 报告输出目录
```

### 步骤 3: 编写 agent.yaml

```yaml
metadata:
  id: <role_id>                    # 唯一标识（小写字母+下划线）
  uuid: <uuid>                     # UUID（可从数据库生成）
  name: <中文名称>                  # 显示名称
  description: <简短描述>           # 一句话说明职责
  model: saas/claude-sonnet-4.5    # 模型选择（sonnet/opus）
  visibility: public               # 可见性（public/private）
  owner_team: null                 # 所属团队（可选）

skills:
  - name: <skill_name>             # 技能名称
    entry: .claude/skills/<skill_name>.py  # 入口脚本
    description: <技能描述>        # 说明这个技能做什么
    timeout: 300                   # 超时时间（秒）

schedule:                          # 定时任务（可选）
  - cron: "0 9 * * *"              # Cron 表达式
    task: <任务描述>               # 任务说明
    enabled: true                  # 是否启用

secrets:                           # 密钥（可选）
  - name: <SECRET_NAME>
    source: env                    # 来源（env/vault）
    key: null

allowed_tools:                     # 允许的工具
  - Read                           # 读取文件
  - Write                          # 写入文件
  - Edit                           # 编辑文件
  - Bash                           # 执行命令
  - Grep                           # 搜索代码
  - Glob                           # 查找文件
  - WebFetch                       # 获取网页

max_turns: 20                      # 最大对话轮次

# 高级配置（可选）
multimodal:                        # 多模态（如需视觉分析）
  enabled: true
  supported_types:
    - image/png
    - image/jpeg
    - image/webp

workspace:                         # 工作区（如需文件访问控制）
  base_dir: /path/to/workspace
  allowed_paths:
    - project/**
  denied_paths:
    - project/.env
    - project/**/*.key

security:                          # 安全配置
  file_access_control: true
  git_audit_logging: true
  important_file_confirmation: true
```

### 步骤 4: 编写 CLAUDE.md（角色定义）

```markdown
# [Agent 中文名称] - Agent 角色定义

## 角色定义

你是[角色描述]，专注于[核心职责]。

## 核心职责

1. **[职责1]**
   - [具体内容]
   - [具体内容]

2. **[职责2]**
   - [具体内容]
   - [具体内容]

## 数据源配置（如适用）

### 数据源1
- URL: [地址]
- 访问方式: [API/数据库/爬虫]
- 认证: [密钥/账号密码]

## 可用能力

### 数据获取
- 使用 `<skill_name>` skill 获取数据
- 使用 `read_file` 读取缓存

### 数据分析
- 使用 `bash` 执行分析脚本
- 使用 `grep` 搜索关键信息

### 结果输出
- 使用 `write_file` 保存结果
- 使用 `<report_skill>` 生成报告

## 工作流程

### 日常工作流程
```
1. [步骤1描述]
2. [步骤2描述]
3. [步骤3描述]
```

### 命令示例
```bash
# 示例命令
echo '{"action": "xxx"}' | python .claude/skills/xxx.py
```

### 用户对话流程
```
当用户询问XXX时：
1. [步骤1]
2. [步骤2]
3. [步骤3]
```

## 关键阈值配置（如适用）

- **阈值1**: [数值] [说明]
- **阈值2**: [数值] [说明]

## 输出格式要求

### [场景1]格式
```
[示例输出]
```

### [场景2]格式
```
[示例输出]
```

## 工作原则

1. **[原则1]**: [说明]
2. **[原则2]**: [说明]
3. **[原则3]**: [说明]

## 与其他 AI 员工的协作

- 当用户询问XXX时，可以结合[其他Agent]的视角
- 当发现XXX时，可以推荐给[其他Agent]

## 注意事项

- ⚠️ [注意事项1]
- ⚠️ [注意事项2]
```

### 步骤 5: 实现 Skills

在 `.claude/skills/` 目录下创建技能脚本：

```python
#!/usr/bin/env python3
"""
[Skill 名称] - [简短描述]
"""
import json
import sys
from typing import Dict, Any

def execute_skill(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行技能逻辑

    Args:
        params: 输入参数

    Returns:
        执行结果（JSON 格式）
    """
    try:
        # 1. 解析参数
        action = params.get('action', 'default')

        # 2. 执行核心逻辑
        result = {}

        if action == 'xxx':
            # 实现具体逻辑
            result = {'status': 'success', 'data': []}
        else:
            result = {'status': 'error', 'message': f'Unknown action: {action}'}

        return result

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def main():
    """标准 Skill 入口"""
    try:
        # 从 stdin 读取 JSON 输入
        input_data = sys.stdin.read()
        params = json.loads(input_data) if input_data else {}

        # 执行技能
        result = execute_skill(params)

        # 输出 JSON 结果到 stdout
        print(json.dumps(result, ensure_ascii=False, indent=2))

        # 返回状态码
        sys.exit(0 if result.get('status') == 'success' else 1)

    except json.JSONDecodeError as e:
        error_result = {
            'status': 'error',
            'message': f'Invalid JSON input: {e}'
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)

    except Exception as e:
        error_result = {
            'status': 'error',
            'message': f'Skill execution failed: {e}'
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)

if __name__ == '__main__':
    main()
```

记得添加执行权限：
```bash
chmod +x .claude/skills/<skill_name>.py
```

### 步骤 6: 注册到数据库

```sql
-- 在 Supabase Dashboard 执行

-- 1. 注册 Agent
INSERT INTO agents (
    role,
    name,
    description,
    model,
    workdir,
    allowed_tools,
    visibility,
    status
) VALUES (
    '<role_id>',
    '<中文名称>',
    '<描述>',
    'saas/claude-sonnet-4.5',
    '/path/to/agents/<role_id>',
    ARRAY['Read', 'Write', 'Bash'],
    'public',
    'active'
);

-- 2. 创建定时任务（如需要）
INSERT INTO scheduled_jobs (
    agent_id,
    job_name,
    cron_expression,
    task_description,
    is_active
) VALUES (
    (SELECT id FROM agents WHERE role = '<role_id>'),
    '<job_name>',
    '0 9 * * *',
    '<任务描述>',
    true
);
```

### 步骤 7: 测试验证

```bash
# 1. 测试 Skill 脚本
cd backend/agents/<role_id>
echo '{"action": "test"}' | python3 .claude/skills/<skill_name>.py

# 2. 测试 Agent 注册
curl http://localhost:8000/api/v1/agents | jq '.agents[] | select(.role=="<role_id>")'

# 3. 测试 Agent 详情
curl http://localhost:8000/api/v1/agents/<role_id> | jq .

# 4. 手动触发定时任务（如有）
curl -X POST http://localhost:8000/api/v1/scheduler/jobs/<job_id>/run
```

---

## 📚 Agent 配置字段详解

### 模型选择

| 模型 | 适用场景 | 成本 | 速度 |
|------|---------|------|------|
| `saas/claude-sonnet-4.5` | 通用任务、分析、生成 | 中 | 快 |
| `saas/claude-opus-4.5` | 复杂任务、视觉分析、代码生成 | 高 | 慢 |
| `saas/claude-haiku-4` | 简单任务、快速响应 | 低 | 极快 |

**选择建议**:
- 定时任务 → Sonnet（平衡性能和成本）
- 视觉分析 → Opus（必须，支持多模态）
- 代码修改 → Opus（质量优先）
- 简单查询 → Haiku（速度优先）

### allowed_tools 说明

| 工具 | 用途 | 安全等级 | 建议 |
|------|------|---------|------|
| Read | 读取文件 | ✅ 安全 | 默认启用 |
| Write | 写入文件 | ⚠️ 注意 | 需要明确的输出目录 |
| Edit | 编辑文件 | ⚠️ 注意 | 仅用于代码修改 Agent |
| Bash | 执行命令 | ⚠️ 危险 | 严格限制，审计日志 |
| Grep | 搜索内容 | ✅ 安全 | 推荐用于分析 |
| Glob | 查找文件 | ✅ 安全 | 推荐用于导航 |
| WebFetch | 获取网页 | ⚠️ 注意 | 注意速率限制 |

### Cron 表达式参考

```
# 格式: 分 时 日 月 星期
# * * * * * 表示每分钟

# 常用示例
"0 9 * * *"       # 每天 9:00
"0 9 * * 1-5"     # 工作日 9:00
"0 18 * * 5"      # 每周五 18:00
"0 */4 * * *"     # 每 4 小时
"0 9,18 * * *"    # 每天 9:00 和 18:00
```

---

## 🔄 AI 员工生命周期管理

### 开发阶段
1. 角色规划（三问原则）
2. 创建文件结构
3. 编写配置和定义
4. 实现 Skills
5. 本地测试

### 测试阶段
1. 单元测试（Skills）
2. 集成测试（Agent API）
3. 端到端测试（用户流程）
4. 压力测试（定时任务）

### 上线阶段
1. 注册到数据库
2. 配置定时任务
3. 设置监控告警
4. 灰度发布（少量用户）

### 运维阶段
1. 监控执行日志
2. 分析用户反馈
3. 优化 Prompt 和逻辑
4. 迭代更新

### 下线阶段
1. 禁用定时任务
2. 通知已订阅用户
3. 归档历史数据
4. 更新文档

---

## 🎨 AI 员工设计模式

### 模式 1: 监控型（Watcher）
**特征**: 持续监控数据，发现异常时推送
**示例**: 研发效能分析官
**关键要素**:
- 明确的监控指标和阈值
- 定时任务（通常每天或每小时）
- 简报生成 + 异常检测
- should_push 逻辑（避免噪音）

### 模式 2: 采集型（Crawler）
**特征**: 定期采集外部数据，整理推送
**示例**: AI 资讯追踪官
**关键要素**:
- 数据源配置（URL、API、数据库）
- 增量更新逻辑（避免重复）
- 数据清洗和格式化
- 优先级判断（高价值内容优先）

### 模式 3: 工具型（Tool）
**特征**: 按需调用，提供专业服务
**示例**: Chris 设计评审员
**关键要素**:
- 明确的使用场景
- 输入输出格式定义
- 知识库/规则库
- 无定时任务，纯对话驱动

### 模式 4: 执行型（Executor）
**特征**: 自动化执行特定任务
**示例**: EE 研发员工
**关键要素**:
- 明确的安全边界
- 审计日志
- 确认机制（重要操作）
- 回滚能力

---

## ✅ 最佳实践 Checklist

**角色设计** □
- [ ] 回答了三问（替谁负责、盯什么、何时找人）
- [ ] 价值主张清晰（为什么需要这个 Agent）
- [ ] 与现有 Agent 职责不重叠

**配置完整性** □
- [ ] agent.yaml 所有字段正确填写
- [ ] CLAUDE.md 包含完整的角色定义
- [ ] Skills 脚本实现并可执行
- [ ] 数据库中已注册

**安全性** □
- [ ] allowed_tools 最小化原则
- [ ] 敏感数据访问控制
- [ ] Bash 命令审计（如使用）
- [ ] 重要操作需确认

**可维护性** □
- [ ] 代码注释清晰
- [ ] 输入输出格式文档化
- [ ] 错误处理完善
- [ ] 日志记录充分

**用户体验** □
- [ ] 遵循信息流铁律（不打扰）
- [ ] 推送内容有价值（can take action）
- [ ] 输出格式友好（Markdown）
- [ ] 响应速度合理

---

## 📖 参考资料

- **Agent 配置示例**: `backend/agents/*/agent.yaml`
- **角色定义示例**: `backend/agents/*/CLAUDE.md`
- **Skill 实现示例**: `backend/agents/*/.claude/skills/*.py`
- **API 文档**: http://localhost:8000/docs
- **数据库 Schema**: `supabase/migrations/*.sql`

---

**最后更新**: 2026-01-15
**维护者**: AI Agent Platform Team
