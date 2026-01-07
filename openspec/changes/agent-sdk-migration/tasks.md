# Agent SDK 迁移 - 任务清单

## 状态说明
- [ ] 待开始
- [x] 已完成
- [-] 进行中

---

## Phase 1: 基础迁移 ✅

### 1.1 项目结构搭建
- [x] 创建 `backend/agent_sdk/` 目录结构
- [x] 创建 `__init__.py` 和基础模块
- [x] 添加依赖到 `requirements.txt`
- [ ] 配置虚拟环境隔离 httpx 版本冲突（待后续处理）

### 1.2 Agent SDK 封装层
- [x] 实现 `AgentSDKService` 类
- [x] 实现 Agent 配置管理 (`config.py`)
- [x] 实现错误处理机制 (`exceptions.py`)
- [x] 添加日志记录

### 1.3 MCP 工具迁移
- [x] 创建 `gerrit_query` 工具
- [x] SDK 内置工具：Read, Write, Bash, Grep, Glob
- [x] 创建 `efficiency_trend` 工具
- [x] 创建 `generate_report` 工具

### 1.4 研发效能分析官迁移
- [x] 创建 Agent 配置 (`AgentRoleConfig`)
- [x] 迁移 system prompt（读取 CLAUDE.md）
- [x] 测试基础功能（配置、初始化、MCP 服务器创建通过）

---

## Phase 2: 任务持久化

### 2.1 数据库迁移
- [ ] 创建 `tasks` 表
- [ ] 扩展 `messages` 表
- [ ] 创建 `tool_executions` 表（可选）
- [ ] 配置 RLS 策略
- [ ] 测试迁移脚本

### 2.2 任务管理器
- [ ] 实现 `TaskManager` 类
- [ ] 实现任务创建逻辑
- [ ] 实现异步执行机制 (`asyncio.create_task`)
- [ ] 实现任务状态管理
- [ ] 实现任务取消功能

### 2.3 消息持久化
- [ ] 实现消息创建逻辑
- [ ] 实现流式内容更新（带节流）
- [ ] 实现工具调用记录
- [ ] 测试消息完整性

---

## Phase 3: 实时通信

### 3.1 SSE 端点
- [ ] 实现 `GET /api/v1/chat/{conversation_id}/stream`
- [ ] 实现增量内容推送
- [ ] 实现事件类型（chunk, tool_use, done, error）
- [ ] 添加超时处理
- [ ] 测试 SSE 流

### 3.2 REST API 端点
- [ ] 实现 `POST /api/v1/chat`
- [ ] 实现 `GET /api/v1/chat/{conversation_id}/messages`
- [ ] 实现 `GET /api/v1/tasks/{task_id}`
- [ ] 实现 `POST /api/v1/tasks/{task_id}/cancel`
- [ ] 添加认证中间件
- [ ] 添加速率限制

### 3.3 Supabase Realtime
- [ ] 启用 `messages` 表 Realtime
- [ ] 启用 `tasks` 表 Realtime
- [ ] 测试 Realtime 推送

---

## Phase 4: 集成测试

### 4.1 单元测试
- [ ] `AgentSDKService` 测试
- [ ] `TaskManager` 测试
- [ ] MCP 工具测试
- [ ] API 端点测试

### 4.2 端到端测试
- [ ] 完整对话流程测试
- [ ] 多轮对话测试
- [ ] 工具调用测试
- [ ] 错误恢复测试

### 4.3 性能测试
- [ ] SSE 延迟测试（目标 < 100ms）
- [ ] 消息更新频率测试
- [ ] 并发连接测试
- [ ] 数据库负载测试

### 4.4 断线恢复测试
- [ ] 客户端离开后 AI 继续执行
- [ ] 客户端重新进入后获取完整历史
- [ ] Realtime 重连后数据同步
- [ ] 网络抖动恢复

---

## Phase 5: 文档与清理

### 5.1 文档更新
- [ ] 更新 API 文档
- [ ] 更新架构文档
- [ ] 添加开发指南
- [ ] 添加部署指南

### 5.2 代码清理
- [ ] 标记 `agent_manager.py` 为废弃
- [ ] 移除未使用的代码
- [ ] 代码审查
- [ ] 合并到主分支

---

## 依赖关系

```
Phase 1.1 → Phase 1.2 → Phase 1.3 → Phase 1.4
                ↓
Phase 2.1 → Phase 2.2 → Phase 2.3
                ↓
Phase 3.2 → Phase 3.1 → Phase 3.3
                ↓
         Phase 4 (全部)
                ↓
         Phase 5 (全部)
```

---

## 风险跟踪

| 风险 | 状态 | 缓解措施 | 负责人 |
|------|------|----------|--------|
| httpx 版本冲突 | 待处理 | 虚拟环境隔离 | - |
| Realtime 性能 | 待验证 | 消息更新节流 | - |
| SDK API 变更 | 低风险 | 封装层隔离 | - |

---

## 验收标准

1. **功能完整**
   - [ ] 研发效能分析官全部功能可用
   - [ ] 支持多轮对话
   - [ ] 支持工具调用

2. **实时性**
   - [ ] SSE 流式输出正常
   - [ ] Realtime 同步正常
   - [ ] 延迟 < 100ms

3. **可靠性**
   - [ ] 客户端离开后任务继续执行
   - [ ] 重新进入后数据完整
   - [ ] 错误处理完善

4. **性能**
   - [ ] 单任务执行时间合理
   - [ ] 支持 10+ 并发用户
   - [ ] 数据库查询高效

---

*创建日期：2026-01-03*
*最后更新：2026-01-03*
