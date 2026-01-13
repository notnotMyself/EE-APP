import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:go_router/go_router.dart';

/// Profile page - shows user information, subscriptions, and settings
class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = Supabase.instance.client.auth.currentUser;

    return Scaffold(
      appBar: AppBar(
        title: const Text('我的'),
      ),
      body: ListView(
        children: [
          // User info section
          Container(
            padding: const EdgeInsets.all(24),
            color: Theme.of(context).primaryColor.withOpacity(0.1),
            child: Column(
              children: [
                CircleAvatar(
                  radius: 40,
                  backgroundColor: Theme.of(context).primaryColor,
                  child: Text(
                    user?.email?.substring(0, 1).toUpperCase() ?? 'U',
                    style: const TextStyle(
                      fontSize: 32,
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  user?.email ?? '未登录',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Subscriptions section
          _buildSectionHeader(context, '我的订阅'),
          ListTile(
            leading: const Icon(Icons.smart_toy),
            title: const Text('管理订阅'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.go('/agents'),
          ),
          const Divider(),

          // Usage stats section
          _buildSectionHeader(context, '使用统计'),
          ListTile(
            leading: const Icon(Icons.article),
            title: const Text('收到简报'),
            trailing: const Text('0'),
          ),
          ListTile(
            leading: const Icon(Icons.chat),
            title: const Text('对话次数'),
            trailing: const Text('0'),
          ),
          const Divider(),

          // Settings section
          _buildSectionHeader(context, '设置'),
          ListTile(
            leading: const Icon(Icons.notifications),
            title: const Text('通知设置'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              // TODO: Navigate to notification settings
            },
          ),
          ListTile(
            leading: const Icon(Icons.settings),
            title: const Text('偏好设置'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              // TODO: Navigate to preference settings
            },
          ),
          const Divider(),

          // Logout button
          Padding(
            padding: const EdgeInsets.all(16),
            child: OutlinedButton(
              onPressed: () async {
                await Supabase.instance.client.auth.signOut();
                if (context.mounted) {
                  context.go('/login');
                }
              },
              child: const Text('退出登录'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(BuildContext context, String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.grey.shade600,
        ),
      ),
    );
  }
}
