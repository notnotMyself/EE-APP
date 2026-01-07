# Agent SDK 迁移与实时通信架构升级

## 概述

将现有 `agent_manager.py` 迁移到官方 Claude Agent SDK，并实现 SSE + Supabase Realtime 的实时通信架构，支持客户端离开后 AI 继续执行任务。

## 背景

### 当前架构的问题

1. **自实现 Agent 框架**：需要维护 agentic loop、工具执行等代码
2. **非流式 API 调用**：`messages.create()` 等待完整响应，体验不够流畅
3. **连接依赖**：客户端断开连接后，AI 任务中断
4. **工具有限**：只有 4 个自实现工具，扩展困难

### 目标架构的优势

1. **官方 SDK**：利用 Claude Agent SDK 的成熟框架能力
2. **任务持久化**：客户端离开后 AI 继续执行，结果存入数据库
3. **实时同步**：通过 Supabase Realtime 实现多端同步
4. **可扩展工具**：MCP 自定义工具机制，轻松扩展

## 变更范围

### 新增
- `backend/agent_sdk/` - 基于 Claude Agent SDK 的新实现
- `backend/agent_sdk/mcp_tools/` - MCP 自定义工具
- 数据库表：`tasks`, `task_outputs`
- Supabase Realtime 触发器

### 修改
- `backend/agent_orchestrator/main.py` - 新增 SSE/Realtime 端点
- `supabase/migrations/` - 新增数据库迁移

### 废弃（后续删除）
- `backend/agent_orchestrator/agent_manager.py` - 旧的 Agent 实现

## 架构设计

详见：[specs/architecture/spec.md](specs/architecture/spec.md)

## API 设计

详见：[specs/api-design/spec.md](specs/api-design/spec.md)

## 数据库设计

详见：[specs/database-schema/spec.md](specs/database-schema/spec.md)

## Realtime 集成

详见：[specs/realtime-integration/spec.md](specs/realtime-integration/spec.md)

## 实施计划

### Phase 1: 基础迁移（1-2 天）
- [ ] 创建 `backend/agent_sdk/` 基础结构
- [ ] 实现 Agent SDK 封装层
- [ ] 迁移研发效能分析官

### Phase 2: 任务持久化（1 天）
- [ ] 创建 tasks 相关数据库表
- [ ] 实现任务异步执行机制
- [ ] 实现任务状态管理

### Phase 3: 实时通信（1 天）
- [ ] 实现 SSE 流式端点
- [ ] 配置 Supabase Realtime
- [ ] 实现消息实时追加

### Phase 4: 集成测试（0.5 天）
- [ ] 端到端测试
- [ ] 性能测试
- [ ] 断线恢复测试

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| httpx 版本冲突 | 中 | 使用虚拟环境隔离 |
| API Gateway 兼容性 | 低 | POC 已验证通过 |
| Realtime 性能 | 中 | 限制消息频率，批量更新 |

## 成功标准

1. 研发效能分析官功能完全迁移，无功能回归
2. 客户端离开后 AI 任务继续执行
3. 多端实时同步消息
4. SSE 流式输出延迟 < 100ms

## 相关文档

- [Claude Agent SDK POC 验证结果](../claude-agent-sdk-poc/tasks.md)
- [产品定位与技术方向](../../../CLAUDE.md)
- [项目技术规范](../../project.md)

---

*创建日期：2026-01-03*
*状态：Draft*
