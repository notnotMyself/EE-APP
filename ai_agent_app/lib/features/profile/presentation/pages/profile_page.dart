import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:go_router/go_router.dart';
import '../../../agents/presentation/theme/agent_profile_theme.dart';

/// OPPO Sans 字体家族名称
const String _oppoSansFamily = 'PingFang SC';

/// Profile page - shows user information, subscriptions, and settings
class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = Supabase.instance.client.auth.currentUser;

    return Scaffold(
      backgroundColor: AgentProfileTheme.backgroundColor,
      body: CustomScrollView(
        slivers: [
          // 自定义 AppBar
          SliverAppBar(
            backgroundColor: AgentProfileTheme.backgroundColor,
            elevation: 0,
            floating: true,
            pinned: true,
            expandedHeight: 130,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                padding: const EdgeInsets.fromLTRB(20, 56, 20, 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    Text(
                      '我的',
                      style: TextStyle(
                        fontFamily: _oppoSansFamily,
                        fontSize: 26,
                        fontWeight: FontWeight.w700,
                        color: AgentProfileTheme.titleColor,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '个人中心与设置',
                      style: TextStyle(
                        fontFamily: _oppoSansFamily,
                        fontSize: 13,
                        color: AgentProfileTheme.labelColor,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            // 移除了设置按钮
          ),

          // 内容区域
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  // User Profile Card
                  _buildUserProfileCard(context, user),
                  const SizedBox(height: 20),

                  // Menu Section
                  _buildMenuSection(context),
                  const SizedBox(height: 20),

                  // Logout Button
                  _buildLogoutButton(context),
                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUserProfileCard(BuildContext context, User? user) {
    final email = user?.email ?? '未登录';
    final displayName = _getDisplayName(user);
    final initial = displayName.isNotEmpty ? displayName[0].toUpperCase() : 'U';

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AgentProfileTheme.cardBackground,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white, width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          // Avatar
          Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: [
                  AgentProfileTheme.accentBlue,
                  AgentProfileTheme.accentBlue.withOpacity(0.7),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              boxShadow: [
                BoxShadow(
                  color: AgentProfileTheme.accentBlue.withOpacity(0.3),
                  blurRadius: 16,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Center(
              child: Text(
                initial,
                style: const TextStyle(
                  fontFamily: _oppoSansFamily,
                  fontSize: 28,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                ),
              ),
            ),
          ),
          const SizedBox(width: 20),

          // User Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  displayName,
                  style: TextStyle(
                    fontFamily: _oppoSansFamily,
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    color: AgentProfileTheme.titleColor,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  email,
                  style: TextStyle(
                    fontFamily: _oppoSansFamily,
                    fontSize: 14,
                    color: AgentProfileTheme.labelColor,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: const Color(0xFF10B981).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 6,
                        height: 6,
                        decoration: const BoxDecoration(
                          color: Color(0xFF10B981),
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        '已认证',
                        style: TextStyle(
                          fontFamily: _oppoSansFamily,
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: const Color(0xFF10B981),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Edit Button
          Container(
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.8),
              shape: BoxShape.circle,
            ),
            child: IconButton(
              icon: const Icon(
                Icons.edit_outlined,
                color: AgentProfileTheme.labelColor,
                size: 20,
              ),
              onPressed: () {
                // TODO: Edit profile
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsCard(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AgentProfileTheme.cardBackground,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white, width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: _buildStatItem(
              icon: Icons.smart_toy_outlined,
              value: '3',
              label: '已订阅',
              color: AgentProfileTheme.accentBlue,
            ),
          ),
          _buildVerticalDivider(),
          Expanded(
            child: _buildStatItem(
              icon: Icons.chat_bubble_outline_rounded,
              value: '28',
              label: '对话数',
              color: const Color(0xFF8B5CF6),
            ),
          ),
          _buildVerticalDivider(),
          Expanded(
            child: _buildStatItem(
              icon: Icons.description_outlined,
              value: '156',
              label: '简报数',
              color: const Color(0xFF10B981),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Column(
      children: [
        Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color, size: 22),
        ),
        const SizedBox(height: 10),
        Text(
          value,
          style: TextStyle(
            fontFamily: _oppoSansFamily,
            fontSize: 22,
            fontWeight: FontWeight.w700,
            color: AgentProfileTheme.titleColor,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: TextStyle(
            fontFamily: _oppoSansFamily,
            fontSize: 12,
            color: AgentProfileTheme.labelColor,
          ),
        ),
      ],
    );
  }

  Widget _buildVerticalDivider() {
    return Container(
      width: 1,
      height: 60,
      color: Colors.white,
    );
  }

  Widget _buildMenuSection(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AgentProfileTheme.cardBackground,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white, width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildMenuItem(
            context,
            icon: Icons.smart_toy_outlined,
            iconColor: AgentProfileTheme.accentBlue,
            title: '管理订阅',
            subtitle: '查看和管理已订阅的AI员工',
            onTap: () => context.go('/home'),
          ),
          _buildMenuDivider(),
          _buildMenuItem(
            context,
            icon: Icons.notifications_outlined,
            iconColor: const Color(0xFFF59E0B),
            title: '通知设置',
            subtitle: '配置消息推送偏好',
            onTap: () {
              // TODO: Navigate to notification settings
            },
          ),
          _buildMenuDivider(),
          _buildMenuItem(
            context,
            icon: Icons.security_outlined,
            iconColor: const Color(0xFF10B981),
            title: '账号安全',
            subtitle: '密码和安全设置',
            onTap: () {
              // TODO: Navigate to security settings
            },
          ),
          _buildMenuDivider(),
          _buildMenuItem(
            context,
            icon: Icons.help_outline_rounded,
            iconColor: const Color(0xFF8B5CF6),
            title: '帮助与反馈',
            subtitle: '常见问题和意见反馈',
            onTap: () {
              // TODO: Navigate to help
            },
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem(
    BuildContext context, {
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: iconColor, size: 22),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontFamily: _oppoSansFamily,
                        fontSize: 15,
                        fontWeight: FontWeight.w500,
                        color: AgentProfileTheme.titleColor,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontFamily: _oppoSansFamily,
                        fontSize: 12,
                        color: AgentProfileTheme.labelColor,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right_rounded,
                color: AgentProfileTheme.labelColor.withOpacity(0.5),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMenuDivider() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      height: 1,
      color: Colors.white,
    );
  }

  Widget _buildLogoutButton(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 56,
      decoration: BoxDecoration(
        color: AgentProfileTheme.cardBackground,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white, width: 1),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => _handleLogout(context),
          borderRadius: BorderRadius.circular(16),
          child: Center(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.logout_rounded,
                  color: const Color(0xFFEF4444),
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  '退出登录',
                  style: TextStyle(
                    fontFamily: _oppoSansFamily,
                    fontSize: 15,
                    fontWeight: FontWeight.w500,
                    color: const Color(0xFFEF4444),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  String _getDisplayName(User? user) {
    if (user == null) return '用户';

    // 优先使用 user_metadata 中的 username
    final username = user.userMetadata?['username'] as String?;
    if (username != null && username.isNotEmpty) {
      return username;
    }

    // 回退到 email 前缀
    final email = user.email ?? '';
    if (email.isEmpty || !email.contains('@')) {
      return '用户';
    }
    return email.split('@')[0];
  }

  /// 处理退出登录，显示确认对话框
  Future<void> _handleLogout(BuildContext context) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
        ),
        title: Text(
          '退出登录',
          style: TextStyle(
            fontFamily: _oppoSansFamily,
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: AgentProfileTheme.titleColor,
          ),
        ),
        content: Text(
          '确定要退出登录吗？',
          style: TextStyle(
            fontFamily: _oppoSansFamily,
            fontSize: 14,
            color: AgentProfileTheme.labelColor,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: Text(
              '取消',
              style: TextStyle(
                fontFamily: _oppoSansFamily,
                fontWeight: FontWeight.w500,
                color: AgentProfileTheme.labelColor,
              ),
            ),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(
              foregroundColor: const Color(0xFFEF4444),
            ),
            child: Text(
              '退出',
              style: TextStyle(
                fontFamily: _oppoSansFamily,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      await Supabase.instance.client.auth.signOut();
      if (context.mounted) {
        context.go('/login');
      }
    }
  }
}
