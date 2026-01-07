## 1. Phase 1: 核心视觉改造
- [x] 1.1 重构 BriefingCard 组件
  - [x] 增加封面图区域（240px，渐变背景 + 图标）
  - [x] 移除操作按钮区域
  - [x] 调整卡片间距（vertical: 12px）
  - [x] 标题升级为 titleLarge
  - [x] 优先级标签移至封面图左上角
  - [x] 未读标记移至封面图右上角
- [x] 1.2 创建全屏详情页 BriefingDetailPage
  - [x] AppBar：Agent 信息 + 分享/跟踪按钮
  - [x] Hero 封面大图（300px）
  - [x] 完整标题和元数据行
  - [x] 影响说明区域（彩色卡片）
  - [x] 完整摘要内容
- [x] 1.3 实现底部固定输入栏
  - [x] 快捷问题 Chips
  - [x] 多行输入框
  - [x] 发送按钮（带加载状态）
  - [x] 消息发送逻辑（创建对话并跳转）
- [x] 1.4 更新 Feed 页面导航
  - [x] 移除 Bottom Sheet 弹窗逻辑
  - [x] 移除 onAction 相关代码
  - [x] 点击卡片跳转全屏详情页
  - [x] 简化 _onBriefingTap 方法

## 2. Phase 2: 封面图生成（待实施）
- [ ] 2.1 数据库迁移
  - [ ] 增加 cover_image_url 字段
  - [ ] 增加 cover_image_type 字段
- [ ] 2.2 创建图表生成服务 ChartService
  - [ ] 实现 matplotlib 图表生成
  - [ ] 集成 Supabase Storage 上传
  - [ ] 实现降级方案（纯色背景）
- [ ] 2.3 集成封面图生成到简报服务
  - [ ] 更新 BriefingService.execute_and_generate_briefing()
  - [ ] 根据简报类型调用图表生成
- [ ] 2.4 前端适配封面图加载
  - [ ] 更新数据模型（coverImageUrl 字段）
  - [ ] 实现网络图片加载
  - [ ] 实现骨架屏占位
  - [ ] 处理加载失败降级

## 3. Phase 3: 简报跟进功能（待实施）
- [ ] 3.1 数据库设计
  - [ ] 创建 briefing_trackings 表
  - [ ] 简报表增加 parent_briefing_id 字段
- [ ] 3.2 后端 API
  - [ ] POST /briefings/{id}/track
  - [ ] DELETE /briefings/{id}/track
  - [ ] 定时任务检测跟踪列表
- [ ] 3.3 前端实现
  - [ ] 详情页"持续跟踪"按钮
  - [ ] 配置 Bottom Sheet
  - [ ] 卡片显示跟踪状态

## 4. Phase 4: 分享功能（待实施）
- [ ] 4.1 数据库设计
  - [ ] 创建 briefing_shares 表
- [ ] 4.2 后端 API
  - [ ] POST /briefings/{id}/share
  - [ ] GET /briefings/shared/{token}
- [ ] 4.3 前端实现
  - [ ] 详情页"分享"按钮
  - [ ] 分享配置面板
  - [ ] 复制链接功能

## 5. 测试与验证
- [ ] 5.1 Phase 1 功能测试
  - [ ] 卡片显示封面图（降级方案）
  - [ ] 点击卡片跳转全屏详情页
  - [ ] 详情页底部输入框功能
  - [ ] 快捷问题一键填充
  - [ ] 发送消息创建对话
- [ ] 5.2 视觉验证
  - [ ] 卡片间距和留白
  - [ ] 封面图渐变色彩
  - [ ] 详情页层次清晰
- [ ] 5.3 性能测试
  - [ ] 卡片加载速度
  - [ ] 详情页首屏渲染
  - [ ] 导航切换流畅度
