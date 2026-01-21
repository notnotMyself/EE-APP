import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../domain/models/agent.dart';
import '../../../conversations/presentation/pages/conversation_page.dart';
import '../theme/agent_profile_theme.dart';
import '../widgets/agent_avatar.dart';
import '../widgets/agent_chat_input.dart';
import '../widgets/quick_action_button.dart';

/// AI员工详情页面
/// 
/// 基于 Figma 设计稿实现，展示AI员工信息和快捷对话入口
class AgentProfilePage extends ConsumerStatefulWidget {
  final Agent agent;

  const AgentProfilePage({
    super.key,
    required this.agent,
  });

  @override
  ConsumerState<AgentProfilePage> createState() => _AgentProfilePageState();
}

class _AgentProfilePageState extends ConsumerState<AgentProfilePage> {
  
  /// 获取问候语
  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 6) return '夜深了';
    if (hour < 9) return '早上好';
    if (hour < 12) return '上午好';
    if (hour < 14) return '中午好';
    if (hour < 18) return '下午好';
    if (hour < 22) return '晚上好';
    return '夜深了';
  }

  /// 开始对话
  void _startConversation(String? initialMessage) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ConversationPage(
          agent: widget.agent,
          initialMessage: initialMessage,
        ),
      ),
    );
  }

  /// 处理快捷功能点击
  void _onQuickActionTap(QuickAction action) {
    _startConversation(action.initialMessage);
  }

  /// 处理输入框提交
  void _onInputSubmit(String message) {
    _startConversation(message);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AgentProfileTheme.backgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            // 顶部导航栏
            _buildAppBar(),
            
            // 内容区域
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(
                  horizontal: AgentProfileTheme.horizontalPadding,
                ),
                child: Column(
                  children: [
                    const SizedBox(height: 16),
                    
                    // 问候区域
                    _buildGreetingSection(),
                    
                    const SizedBox(height: 40),
                    
                    // AI员工信息区域
                    _buildAgentInfoSection(),
                    
                    const SizedBox(height: 59),
                    
                    // 输入框和快捷功能区域
                    _buildInteractionSection(),
                    
                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 构建顶部导航栏
  Widget _buildAppBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: 8,
        vertical: 8,
      ),
      child: Row(
        children: [
          IconButton(
            onPressed: () => Navigator.of(context).pop(),
            icon: const Icon(
              Icons.arrow_back_ios_new,
              color: AgentProfileTheme.titleColor,
            ),
          ),
          const Spacer(),
          IconButton(
            onPressed: () {
              // TODO: 更多操作菜单
            },
            icon: const Icon(
              Icons.more_horiz,
              color: AgentProfileTheme.titleColor,
            ),
          ),
        ],
      ),
    );
  }

  /// 构建问候区域
  Widget _buildGreetingSection() {
    // TODO: 从用户状态获取真实用户名
    const userName = 'User';
    
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _getGreeting(),
              style: AgentProfileTheme.greetingStyle,
            ),
            const SizedBox(height: 6),
            Text(
              userName,
              style: AgentProfileTheme.userNameStyle,
            ),
          ],
        ),
        // 通知图标
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.68),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.notifications_outlined,
            color: AgentProfileTheme.titleColor,
          ),
        ),
      ],
    );
  }

  /// 构建AI员工信息区域
  Widget _buildAgentInfoSection() {
    return Column(
      children: [
        // 头像
        AgentAvatar(
          avatarUrl: widget.agent.avatarUrl,
          fallbackText: widget.agent.name,
        ),
        
        const SizedBox(height: 14),
        
        // 名称
        Text(
          widget.agent.name,
          style: AgentProfileTheme.agentNameStyle,
        ),
        
        // 描述
        SizedBox(
          width: 209,
          child: Text(
            widget.agent.description,
            textAlign: TextAlign.center,
            style: AgentProfileTheme.agentDescriptionStyle,
          ),
        ),
      ],
    );
  }

  /// 构建交互区域（输入框 + 快捷功能）
  Widget _buildInteractionSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 输入框
        AgentChatInput(
          hintText: '简单描述下方案背景与目标',
          onSubmit: _onInputSubmit,
        ),
        
        const SizedBox(height: 19),
        
        // 快捷功能按钮
        QuickActionRow(
          actions: QuickActions.defaults,
          onActionTap: _onQuickActionTap,
        ),
      ],
    );
  }
}

