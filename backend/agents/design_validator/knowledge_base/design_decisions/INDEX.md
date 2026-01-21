# 设计决策索引

> ADR (Architecture Decision Record) 格式记录的重要设计决策

## 决策列表

| 编号 | 标题 | 分类 | 关键词 | 日期 | 状态 |
|------|------|------|--------|------|------|
| 001 | 登录页面全屏输入模式 | 交互 | 登录, 输入框, 小屏幕, 键盘 | 2026-01 | ✅ 已采纳 |

---

## 按分类查看

### 交互设计
- [001] 登录页面全屏输入模式

### 视觉设计
- （待补充）

### 信息架构
- （待补充）

### 导航设计
- （待补充）

---

## 快速搜索

```bash
# 搜索登录相关决策
grep -r "登录" knowledge_base/design_decisions/

# 搜索输入框相关决策
grep -r "输入" knowledge_base/design_decisions/

# 搜索已采纳的决策
grep -r "已采纳" knowledge_base/design_decisions/
```

---

## 决策文件格式 (ADR)

```markdown
---
title: 决策标题
category: interaction | visual | architecture | navigation
tags: [关键词1, 关键词2]
date: YYYY-MM-DD
status: 已采纳 | 已废弃 | 讨论中
designer: 设计者
related_cases: [case-xxx, case-yyy]
---

# 背景和问题

[描述面临的问题和背景]

# 决策

[做出的设计决策]

# 理由

[为什么做出这个决策]

# 后果

**优点**：
- ...

**缺点**：
- ...

**风险**：
- ...

# 备选方案

[被否决的其他方案]

# 参考资料

[相关规范、案例、数据]
```

---

## 如何添加新决策

1. 复制模板创建新文件
2. 编号规则：三位数字递增（001, 002, 003...）
3. 文件命名：`XXX-功能名-决策要点.md`
4. 更新本索引文件

