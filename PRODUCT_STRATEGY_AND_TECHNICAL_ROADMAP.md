# 产品战略与技术演进路线图

## 一、产品定位与核心价值

### 1.1 产品定义
我们要做的不是一个“信息流APP”，也不是一个“BI报表工具”，而是一个**企业级AI数字员工平台（Cognitive Decision Auxiliary System）**。
核心隐喻是**“高层秘书班子”**：它由多个拥有特定职责的AI Agent（数字员工）组成，持续在后台监控、分析、总结，仅在关键时刻主动向决策者汇报。

### 1.2 目标用户
*   **核心用户**：企业内的决策者、管理者（TL、总监、VP）、关键项目负责人。
*   **用户特征**：信息过载、时间碎片化、需要靠“信息差”和“准确判断”来管理团队或业务。

### 1.3 核心价值：认知负担转移
我们的产品不是为了让用户“多看内容”，而是为了让用户**“少看内容，但不错过关键信息”**。
*   **省心（Peace of Mind）**：把“持续盯盘”的责任外包给AI。
*   **敏锐（Insight）**：从海量噪音中提取信号（异常、趋势、拐点）。
*   **闭环（Action）**：不仅仅是看，还能直接下达指令让AI跟进。

---

## 二、两条产品主线

我们的产品交互围绕“感知”与“行动”两大主线展开：

### 主线一：信息流（Information Flow）—— 任务感知流
这不是娱乐Feed流，而是**“AI员工的工作汇报流”**。
*   **性质**：被动接收，高信噪比。
*   **内容**：不是文章，而是**“判断型简报”**。
    *   🚨 **异常报警**：“某模块Review耗时连续3周上涨。”
    *   📉 **趋势预警**：“NPS在特定渠道出现拐点。”
    *   🆕 **机会/风险**：“竞品发布了新功能，可能影响我们。”
*   **原则**：
    *   宁缺毋滥（一天可能只有1-3条）。
    *   必须带有上下文和初步结论。
    *   **“错过有成本”**的信息才值得进流。

### 主线二：任务交付（Task Delivery）—— 对话即行动
这不是闲聊Chat，而是**“任务委派控制台”**。
*   **触发**：点击信息流中的简报，进入对话。
*   **交互**：
    *   **追问**：“展开讲讲为什么Review变慢？”
    *   **委派**：“帮我拉个会”、“生成一份报告发给XX”、“继续盯着，下周再报”。
*   **价值**：将“认知”瞬间转化为“行动”，形成闭环。

---

## 三、技术战略：Auto-Develop by AI (踩着Claude Code过河)

为了实现快速迭代并验证“AI生成应用”的可行性，我们将采用 **Spec-Driven Development (SDD)** 模式，利用 Claude Code (或 Cursor Agent) 实现高度自动化的开发流程。

### 3.1 核心理念
**“代码是生成的副产品，文档（Spec）才是源代码。”**
我们要像管理产品一样管理Spec，让AI充当“超级工程师”。

### 3.2 实施路径 (The "Claude Code" Workflow)

#### 阶段一：Prompt Engineering to Spec (P2S)
利用对话（如现在的过程）生成高质量的工程规格说明书（OpenSpec）。
*   **输入**：自然语言的需求、会议记录、脑暴。
*   **工具**：Claude / Cursor Chat。
*   **产出**：`openspec/` 目录下的 Markdown 文档（PRD、API定义、数据结构）。
    *   例如：`openspec/agents/dev_efficiency_analyst.md` (定义研发效能分析官的所有行为)。

#### 阶段二：Spec to Code (S2C)
利用 Agent 能力读取 Spec 并生成代码。
*   **操作**：
    1.  开发者（用户/我）确认 Spec 无误。
    2.  调用 Agent：“实现 `openspec/agents/dev_efficiency_analyst.md` 中定义的后端逻辑。”
    3.  Agent 读取 Spec，分析现有代码库，生成 Python/Dart 代码。
    4.  Agent 自动运行测试或请求人工验证。

#### 阶段三：Review & Iterate
*   **人工介入**：只在 Review 环节介入，检查逻辑漏洞或体验问题。
*   **迭代**：修改 Spec 而不是直接修改代码（尽可能保持单向流动），然后让 Agent 重新同步代码。

### 3.3 架构支撑 (Agent-Oriented Architecture)

为了支持这种开发模式，我们的架构需要保持高度模块化：

1.  **AI Agent Platform (`ai_agent_platform/`)**：
    *   通用底座，处理 LLM 调用、记忆、工具分发。
    *   这一层相对稳定，由 Core Team 维护。

2.  **业务 Agent (`backend/agents/`)**：
    *   **研发效能分析官**、**NPS洞察官**等。
    *   这些是**高度动态**的，完全可以通过 AI 根据 Spec 自动生成和调整。
    *   每个 Agent 包含：
        *   `profile.md` (角色设定)
        *   `skills.py` (工具函数，如查询 Gerrit)
        *   `workflow.yaml` (工作流定义)

3.  **前端壳 (`ai_agent_app/`)**：
    *   提供通用的渲染框架：`InfoCard` (信息流卡片) 和 `ChatInterface` (对话界面)。
    *   UI 尽量通用化，由后端 Agent 决定渲染内容（Server-Driven UI 思想），减少前端发版频率。

---

## 四、近期执行计划 (MVP: 研发效能分析官)

目标：**2周内上线“研发效能分析官”，验证“决策辅助”闭环。**

1.  **Day 1-3 (Spec & Data)**:
    *   [ ] 编写 `openspec/mvp/dev_efficiency_analyst_spec.md`。
    *   [ ] 确认数据源 (Gerrit/Jira) 及 API 访问权限。
    *   [ ] 设计“今日简报”的数据结构。

2.  **Day 4-7 (Backend & Agent)**:
    *   [ ] 使用 AI 生成数据抓取脚本。
    *   [ ] 实现简单的分析规则 (Rule-based + LLM Summary)。
    *   [ ] 搭建定时任务 (Daily Cron)。

3.  **Day 8-10 (App Integration)**:
    *   [ ] 在 Flutter 端实现“简报卡片”样式。
    *   [ ] 联调“点击卡片 -> 进入对话”的跳转。

4.  **Day 11-14 (Dogfooding)**:
    *   [ ] 内部发布，邀请 TL 级别用户试用。
    *   [ ] 收集“看没看”、“准不准”的反馈。

