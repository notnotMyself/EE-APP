# OpenSpec 快速入门

## ✅ 初始化完成

OpenSpec 已成功初始化！创建的文件结构：

```
openspec/
├── project.md           # ✅ 已填充项目信息（技术栈、架构、约束等）
├── AGENTS.md           # ✅ AI 助手工作流程说明
├── changes/            # 📁 提议的变更（尚未合并）
│   └── .gitkeep
└── specs/              # 📁 当前规范（已合并的功能规范）
    └── .gitkeep
```

---

## 🎯 OpenSpec 工作流程

### 三阶段流程

```
Stage 1: 创建变更提案       Stage 2: 实现变更       Stage 3: 归档变更
   (Changes)                                        (Archive)
       ↓                         ↓                      ↓
   草拟规范              → 实现功能代码      →  更新主规范文档
   review 对齐                                  移至 archive/
```

### Stage 1: 创建变更提案 (Creating Changes)

**何时创建提案？**
- ✅ 添加新功能
- ✅ 架构变更
- ✅ API 变更
- ✅ 性能优化（改变行为）
- ❌ Bug 修复（无需提案）
- ❌ 注释/格式化（无需提案）

**流程**：
```bash
# 1. 查看现有规范和变更
openspec list --specs    # 查看已有功能规范
openspec list            # 查看进行中的变更

# 2. 你告诉我："我想添加 [功能]，请创建 OpenSpec 变更提案"

# 3. 我会创建：
openspec/changes/add-your-feature/
├── proposal.md          # 变更提案
├── tasks.md            # 实现清单
├── design.md           # 技术设计（可选）
└── specs/              # 规范变更（delta）
    └── capability/
        └── spec.md     # 只包含新增/修改/删除的部分

# 4. 验证提案
openspec validate add-your-feature --strict

# 5. 你 review 并批准后，我开始实现
```

### Stage 2: 实现变更 (Implementing)

```bash
# 我会：
1. 阅读 proposal.md - 理解要构建什么
2. 阅读 design.md - 技术方案
3. 阅读 tasks.md - 实现清单
4. 逐个完成任务
5. 更新 tasks.md 的勾选状态 ✅
```

### Stage 3: 归档变更 (Archiving)

```bash
# 功能部署后：
openspec archive add-your-feature --yes

# 会自动：
# - 移动 changes/add-your-feature/ → changes/archive/2024-12-30-add-your-feature/
# - 合并 spec delta 到 specs/ 主规范
```

---

## 🚀 实际使用示例

### 示例 1: 添加新 AI 员工

**你说**：
> "我想添加 NPS 洞察官，请创建 OpenSpec 变更提案"

**我会**：
1. 创建 `openspec/changes/add-nps-insight-analyst/`
2. 编写 `proposal.md`：
   ```markdown
   # Add NPS Insight Analyst

   ## Objective
   Create a new AI agent to analyze NPS feedback...

   ## Affected Capabilities
   - backend-agents (NEW agent)
   - api-endpoints (NEW routes)
   ```
3. 编写 `tasks.md`：
   ```markdown
   - [ ] Create workspace: backend/agents/nps_insight_analyst/
   - [ ] Write CLAUDE.md
   - [ ] Create 2 skills: feedback_analysis.py, report_generation.py
   - [ ] Register in agent_manager.py
   - [ ] Update API docs
   ```
4. 编写 spec delta（新增的功能规范）
5. 运行 `openspec validate add-nps-insight-analyst --strict`
6. 等你批准后开始实现

### 示例 2: 修改现有功能

**你说**：
> "我想让研发效能分析官支持生成图表，请创建提案"

**我会**：
1. 创建 `openspec/changes/update-dev-analyst-charts/`
2. 在 spec delta 中标记：
   ```markdown
   ## MODIFIED Requirements

   ### Chart Generation
   #### Scenario: Generate trend chart
   GIVEN user requests a trend chart
   WHEN AI calls chart_generation skill
   THEN PNG chart is saved to reports/
   ```

---

## 📋 常用命令

```bash
# 查看所有规范
openspec list --specs

# 查看进行中的变更
openspec list

# 查看某个规范详情
openspec show backend-agents

# 查看某个变更详情
openspec show add-your-feature

# 验证变更
openspec validate add-your-feature --strict

# 归档完成的变更
openspec archive add-your-feature --yes

# 打开交互式仪表板
openspec view
```

---

## 💡 使用技巧

### 对于你（用户）

**创建新功能时**：
```
"我想添加 [功能描述]，请创建 OpenSpec 变更提案"
```

**修改现有功能时**：
```
"我想修改 [功能] 来支持 [新能力]，请创建提案"
```

**批准提案**：
```
"提案看起来不错，开始实现吧"
或
"proposal 需要修改：[反馈]"
```

### 对于我（AI 助手）

**创建提案前**：
- ✅ 先运行 `openspec list --specs` 查看现有规范
- ✅ 检查是否已有类似功能
- ✅ 读取 `openspec/project.md` 了解项目约束
- ✅ 使用 kebab-case 命名：`add-feature`, `update-component`, `remove-deprecated`

**实现时**：
- ✅ 严格按照 proposal.md 和 tasks.md 执行
- ✅ 不偏离已批准的规范
- ✅ 完成一项勾选一项

**归档时**：
- ✅ 确保功能已部署
- ✅ 运行 `openspec archive <change-id> --yes`
- ✅ 验证 `openspec validate --strict` 通过

---

## 🎯 当前项目状态

### 已有规范（specs/）
- 🔲 暂无（首次使用 OpenSpec）

### 待创建规范
- `backend-agents` - AI 员工架构规范
- `tool-calling` - 工具执行规范
- `api-design` - FastAPI 接口规范
- `frontend-architecture` - Flutter 架构规范

### 建议第一个变更
创建基础规范文档，记录已实现的架构：

```
"请创建 OpenSpec 变更提案：为已实现的 AI 员工系统创建规范文档"
```

这样后续的变更就有明确的"当前真相"可以参考。

---

## 📚 更多信息

- **OpenSpec 官方文档**: https://github.com/Fission-AI/OpenSpec
- **项目信息**: `openspec/project.md`
- **工作流程**: `openspec/AGENTS.md`

---

**准备好开始了吗？试试这个命令：**

```
"请创建 OpenSpec 变更提案：为研发效能分析官添加图表生成能力"
```

或者：

```
"请为现有的 AI 员工系统创建规范文档"
```
