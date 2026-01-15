import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../../../core/services/notification_service.dart';

/// 通知设置模型
class NotificationSettings {
  final bool enabled;
  final List<String> priorities; // ['P0', 'P1']
  final double minImportance; // 0.0 - 1.0
  final String quietHoursStart; // "HH:mm"
  final String quietHoursEnd; // "HH:mm"

  NotificationSettings({
    required this.enabled,
    required this.priorities,
    required this.minImportance,
    required this.quietHoursStart,
    required this.quietHoursEnd,
  });

  factory NotificationSettings.fromJson(Map<String, dynamic> json) {
    return NotificationSettings(
      enabled: json['enabled'] as bool? ?? true,
      priorities: (json['priorities'] as List?)?.cast<String>() ?? ['P0', 'P1'],
      minImportance: (json['min_importance'] as num?)?.toDouble() ?? 0.7,
      quietHoursStart: json['quiet_hours_start'] as String? ?? '22:00',
      quietHoursEnd: json['quiet_hours_end'] as String? ?? '08:00',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'enabled': enabled,
      'priorities': priorities,
      'min_importance': minImportance,
      'quiet_hours_start': quietHoursStart,
      'quiet_hours_end': quietHoursEnd,
    };
  }

  NotificationSettings copyWith({
    bool? enabled,
    List<String>? priorities,
    double? minImportance,
    String? quietHoursStart,
    String? quietHoursEnd,
  }) {
    return NotificationSettings(
      enabled: enabled ?? this.enabled,
      priorities: priorities ?? this.priorities,
      minImportance: minImportance ?? this.minImportance,
      quietHoursStart: quietHoursStart ?? this.quietHoursStart,
      quietHoursEnd: quietHoursEnd ?? this.quietHoursEnd,
    );
  }
}

/// 通知设置状态提供者
final notificationSettingsProvider =
    StateNotifierProvider<NotificationSettingsNotifier, AsyncValue<NotificationSettings>>((ref) {
  return NotificationSettingsNotifier();
});

class NotificationSettingsNotifier extends StateNotifier<AsyncValue<NotificationSettings>> {
  NotificationSettingsNotifier() : super(const AsyncValue.loading()) {
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    try {
      final userId = Supabase.instance.client.auth.currentUser?.id;
      if (userId == null) {
        state = AsyncValue.data(NotificationSettings(
          enabled: true,
          priorities: ['P0', 'P1'],
          minImportance: 0.7,
          quietHoursStart: '22:00',
          quietHoursEnd: '08:00',
        ));
        return;
      }

      final response = await Supabase.instance.client
          .from('user_notification_settings')
          .select()
          .eq('user_id', userId)
          .maybeSingle();

      if (response == null) {
        // 创建默认设置
        final defaultSettings = NotificationSettings(
          enabled: true,
          priorities: ['P0', 'P1'],
          minImportance: 0.7,
          quietHoursStart: '22:00',
          quietHoursEnd: '08:00',
        );
        await _saveSettings(defaultSettings);
        state = AsyncValue.data(defaultSettings);
      } else {
        state = AsyncValue.data(NotificationSettings.fromJson(response));
      }
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<void> updateSettings(NotificationSettings settings) async {
    state = const AsyncValue.loading();
    try {
      await _saveSettings(settings);
      state = AsyncValue.data(settings);
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<void> _saveSettings(NotificationSettings settings) async {
    final userId = Supabase.instance.client.auth.currentUser?.id;
    if (userId == null) return;

    await Supabase.instance.client.from('user_notification_settings').upsert({
      'user_id': userId,
      ...settings.toJson(),
    });
  }
}

/// 通知设置页面
class NotificationSettingsPage extends ConsumerWidget {
  const NotificationSettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final settingsAsync = ref.watch(notificationSettingsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('通知设置'),
        elevation: 0,
      ),
      body: settingsAsync.when(
        data: (settings) => _buildSettingsContent(context, ref, settings),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 48, color: theme.colorScheme.error),
              const SizedBox(height: 16),
              Text('加载设置失败: $error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  ref.invalidate(notificationSettingsProvider);
                },
                child: const Text('重试'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSettingsContent(
    BuildContext context,
    WidgetRef ref,
    NotificationSettings settings,
  ) {
    final theme = Theme.of(context);
    final notifier = ref.read(notificationSettingsProvider.notifier);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // 总开关
        Card(
          child: SwitchListTile(
            title: const Text('推送通知'),
            subtitle: const Text('接收 AI 员工的简报推送'),
            value: settings.enabled,
            onChanged: (value) {
              notifier.updateSettings(settings.copyWith(enabled: value));
            },
          ),
        ),

        const SizedBox(height: 24),

        // 优先级过滤
        Text(
          '优先级过滤',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          '选择需要推送的简报优先级',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 12),

        Card(
          child: Column(
            children: [
              CheckboxListTile(
                title: const Text('P0 - 紧急'),
                subtitle: const Text('需要立即处理的事项'),
                value: settings.priorities.contains('P0'),
                onChanged: (value) {
                  final priorities = List<String>.from(settings.priorities);
                  if (value == true) {
                    priorities.add('P0');
                  } else {
                    priorities.remove('P0');
                  }
                  notifier.updateSettings(settings.copyWith(priorities: priorities));
                },
              ),
              const Divider(height: 1),
              CheckboxListTile(
                title: const Text('P1 - 重要'),
                subtitle: const Text('需要及时关注的事项'),
                value: settings.priorities.contains('P1'),
                onChanged: (value) {
                  final priorities = List<String>.from(settings.priorities);
                  if (value == true) {
                    priorities.add('P1');
                  } else {
                    priorities.remove('P1');
                  }
                  notifier.updateSettings(settings.copyWith(priorities: priorities));
                },
              ),
              const Divider(height: 1),
              CheckboxListTile(
                title: const Text('P2 - 一般'),
                subtitle: const Text('常规信息推送'),
                value: settings.priorities.contains('P2'),
                onChanged: (value) {
                  final priorities = List<String>.from(settings.priorities);
                  if (value == true) {
                    priorities.add('P2');
                  } else {
                    priorities.remove('P2');
                  }
                  notifier.updateSettings(settings.copyWith(priorities: priorities));
                },
              ),
            ],
          ),
        ),

        const SizedBox(height: 24),

        // 重要性阈值
        Text(
          '重要性阈值',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          '只推送重要性评分 ≥ ${settings.minImportance.toStringAsFixed(1)} 的简报',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 12),

        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Slider(
                  value: settings.minImportance,
                  min: 0.0,
                  max: 1.0,
                  divisions: 10,
                  label: settings.minImportance.toStringAsFixed(1),
                  onChanged: (value) {
                    notifier.updateSettings(settings.copyWith(minImportance: value));
                  },
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('0.0', style: theme.textTheme.bodySmall),
                    Text('1.0', style: theme.textTheme.bodySmall),
                  ],
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 24),

        // 免打扰时间
        Text(
          '免打扰时间',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          '在此时间段内不接收推送通知',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 12),

        Card(
          child: Column(
            children: [
              ListTile(
                title: const Text('开始时间'),
                trailing: Text(
                  settings.quietHoursStart,
                  style: theme.textTheme.titleMedium,
                ),
                onTap: () async {
                  final time = await _pickTime(context, settings.quietHoursStart);
                  if (time != null) {
                    notifier.updateSettings(settings.copyWith(quietHoursStart: time));
                  }
                },
              ),
              const Divider(height: 1),
              ListTile(
                title: const Text('结束时间'),
                trailing: Text(
                  settings.quietHoursEnd,
                  style: theme.textTheme.titleMedium,
                ),
                onTap: () async {
                  final time = await _pickTime(context, settings.quietHoursEnd);
                  if (time != null) {
                    notifier.updateSettings(settings.copyWith(quietHoursEnd: time));
                  }
                },
              ),
            ],
          ),
        ),

        const SizedBox(height: 24),

        // 测试推送
        Card(
          child: ListTile(
            leading: const Icon(Icons.notifications_active),
            title: const Text('测试推送'),
            subtitle: const Text('发送一条测试通知'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => _testNotification(context),
          ),
        ),

        const SizedBox(height: 24),

        // 设备信息
        Card(
          child: ListTile(
            leading: const Icon(Icons.devices),
            title: const Text('已注册设备'),
            subtitle: FutureBuilder<String?>(
              future: NotificationService().getRegistrationId(),
              builder: (context, snapshot) {
                if (snapshot.hasData && snapshot.data != null) {
                  return Text(
                    'Registration ID: ${snapshot.data!.substring(0, 16)}...',
                    style: theme.textTheme.bodySmall,
                  );
                }
                return const Text('正在获取设备信息...');
              },
            ),
          ),
        ),
      ],
    );
  }

  Future<String?> _pickTime(BuildContext context, String currentTime) async {
    final parts = currentTime.split(':');
    final initialTime = TimeOfDay(
      hour: int.parse(parts[0]),
      minute: int.parse(parts[1]),
    );

    final picked = await showTimePicker(
      context: context,
      initialTime: initialTime,
    );

    if (picked != null) {
      return '${picked.hour.toString().padLeft(2, '0')}:${picked.minute.toString().padLeft(2, '0')}';
    }

    return null;
  }

  Future<void> _testNotification(BuildContext context) async {
    final messenger = ScaffoldMessenger.of(context);

    try {
      // 调用后端测试接口
      final response = await Supabase.instance.client.functions.invoke(
        'api/v1/notifications/test',
      );

      if (response.status == 200) {
        messenger.showSnackBar(
          const SnackBar(content: Text('测试通知已发送，请检查通知栏')),
        );
      } else {
        throw Exception('发送失败: ${response.data}');
      }
    } catch (e) {
      messenger.showSnackBar(
        SnackBar(content: Text('发送测试通知失败: $e')),
      );
    }
  }
}
