import 'package:flutter/material.dart';
import 'package:timeline_tile/timeline_tile.dart';
import 'widget_registry.dart';

/// ========== 警报列表组件 ==========

class AlertListConfig extends ComponentConfig {
  final String title;
  final List<AlertItem> alerts;
  final bool showIcon;

  AlertListConfig({
    required Map<String, dynamic> data,
    required Map<String, dynamic> config,
    required this.title,
    required this.alerts,
    required this.showIcon,
  }) : super(type: 'alert_list', data: data, config: config);

  factory AlertListConfig.fromSchema(Map<String, dynamic> schema) {
    final data = schema['data'] as Map<String, dynamic>? ?? {};
    final config = schema['config'] as Map<String, dynamic>? ?? {};

    final alertsData = data.getList<Map<String, dynamic>>('alerts') ?? [];
    final alerts = alertsData.map((a) => AlertItem.fromJson(a)).toList();

    return AlertListConfig(
      data: data,
      config: config,
      title: data.getString('title') ?? '',
      alerts: alerts,
      showIcon: config.getBool('show_icon') ?? true,
    );
  }
}

class AlertItem {
  final String title;
  final String? description;
  final String severity; // 'critical', 'warning', 'info'
  final DateTime? timestamp;

  AlertItem({
    required this.title,
    this.description,
    required this.severity,
    this.timestamp,
  });

  factory AlertItem.fromJson(Map<String, dynamic> json) {
    return AlertItem(
      title: json.getString('title') ?? '',
      description: json.getString('description'),
      severity: json.getString('severity') ?? 'info',
      timestamp: _parseTimestamp(json['timestamp']),
    );
  }

  static DateTime? _parseTimestamp(dynamic value) {
    if (value == null) return null;
    if (value is DateTime) return value;
    if (value is String) {
      try {
        return DateTime.parse(value);
      } catch (e) {
        return null;
      }
    }
    return null;
  }
}

class AlertListWidget extends StatelessWidget {
  final AlertListConfig config;

  const AlertListWidget({
    super.key,
    required this.config,
  });

  static Widget fromSchema(Map<String, dynamic> schema) {
    final config = AlertListConfig.fromSchema(schema);
    return AlertListWidget(config: config);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (config.title.isNotEmpty) ...[
              Text(
                config.title,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
            ],
            if (config.alerts.isEmpty)
              Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Text(
                    '暂无警报',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              )
            else
              ...config.alerts.map((alert) => _buildAlertItem(context, alert)),
          ],
        ),
      ),
    );
  }

  Widget _buildAlertItem(BuildContext context, AlertItem alert) {
    final theme = Theme.of(context);
    final severityConfig = _getSeverityConfig(alert.severity);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: severityConfig.backgroundColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: severityConfig.borderColor,
          width: 1,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (config.showIcon) ...[
            Icon(
              severityConfig.icon,
              color: severityConfig.iconColor,
              size: 20,
            ),
            const SizedBox(width: 12),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  alert.title,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: severityConfig.textColor,
                  ),
                ),
                if (alert.description != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    alert.description!,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: severityConfig.textColor.withOpacity(0.8),
                    ),
                  ),
                ],
                if (alert.timestamp != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    _formatTimestamp(alert.timestamp!),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: severityConfig.textColor.withOpacity(0.6),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  _SeverityConfig _getSeverityConfig(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return _SeverityConfig(
          icon: Icons.error,
          iconColor: Colors.red.shade700,
          backgroundColor: Colors.red.shade50,
          borderColor: Colors.red.shade200,
          textColor: Colors.red.shade900,
        );
      case 'warning':
        return _SeverityConfig(
          icon: Icons.warning,
          iconColor: Colors.orange.shade700,
          backgroundColor: Colors.orange.shade50,
          borderColor: Colors.orange.shade200,
          textColor: Colors.orange.shade900,
        );
      case 'info':
      default:
        return _SeverityConfig(
          icon: Icons.info,
          iconColor: Colors.blue.shade700,
          backgroundColor: Colors.blue.shade50,
          borderColor: Colors.blue.shade200,
          textColor: Colors.blue.shade900,
        );
    }
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final diff = now.difference(timestamp);

    if (diff.inMinutes < 1) return '刚刚';
    if (diff.inMinutes < 60) return '${diff.inMinutes}分钟前';
    if (diff.inHours < 24) return '${diff.inHours}小时前';
    if (diff.inDays < 7) return '${diff.inDays}天前';

    return '${timestamp.year}-${timestamp.month.toString().padLeft(2, '0')}-${timestamp.day.toString().padLeft(2, '0')}';
  }
}

class _SeverityConfig {
  final IconData icon;
  final Color iconColor;
  final Color backgroundColor;
  final Color borderColor;
  final Color textColor;

  _SeverityConfig({
    required this.icon,
    required this.iconColor,
    required this.backgroundColor,
    required this.borderColor,
    required this.textColor,
  });
}

/// ========== 时间线组件 ==========

class TimelineConfig extends ComponentConfig {
  final String title;
  final List<TimelineEvent> events;
  final bool showTime;

  TimelineConfig({
    required Map<String, dynamic> data,
    required Map<String, dynamic> config,
    required this.title,
    required this.events,
    required this.showTime,
  }) : super(type: 'timeline', data: data, config: config);

  factory TimelineConfig.fromSchema(Map<String, dynamic> schema) {
    final data = schema['data'] as Map<String, dynamic>? ?? {};
    final config = schema['config'] as Map<String, dynamic>? ?? {};

    final eventsData = data.getList<Map<String, dynamic>>('events') ?? [];
    final events = eventsData.map((e) => TimelineEvent.fromJson(e)).toList();

    return TimelineConfig(
      data: data,
      config: config,
      title: data.getString('title') ?? '',
      events: events,
      showTime: config.getBool('show_time') ?? true,
    );
  }
}

class TimelineEvent {
  final String title;
  final String? description;
  final DateTime timestamp;
  final String? status; // 'completed', 'in_progress', 'pending'
  final IconData? icon;

  TimelineEvent({
    required this.title,
    this.description,
    required this.timestamp,
    this.status,
    this.icon,
  });

  factory TimelineEvent.fromJson(Map<String, dynamic> json) {
    return TimelineEvent(
      title: json.getString('title') ?? '',
      description: json.getString('description'),
      timestamp: AlertItem._parseTimestamp(json['timestamp']) ?? DateTime.now(),
      status: json.getString('status'),
      icon: _parseIcon(json.getString('icon')),
    );
  }

  static IconData? _parseIcon(String? iconName) {
    if (iconName == null) return null;
    final iconMap = {
      'check_circle': Icons.check_circle,
      'radio_button_checked': Icons.radio_button_checked,
      'circle': Icons.circle,
      'event': Icons.event,
      'schedule': Icons.schedule,
      'done': Icons.done,
    };
    return iconMap[iconName];
  }
}

class TimelineWidget extends StatelessWidget {
  final TimelineConfig config;

  const TimelineWidget({
    super.key,
    required this.config,
  });

  static Widget fromSchema(Map<String, dynamic> schema) {
    final config = TimelineConfig.fromSchema(schema);
    return TimelineWidget(config: config);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (config.title.isNotEmpty) ...[
              Text(
                config.title,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
            ],
            if (config.events.isEmpty)
              Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Text(
                    '暂无事件',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              )
            else
              ...config.events.asMap().entries.map((entry) {
                final index = entry.key;
                final event = entry.value;
                final isFirst = index == 0;
                final isLast = index == config.events.length - 1;
                return _buildTimelineItem(
                  context,
                  event,
                  isFirst: isFirst,
                  isLast: isLast,
                );
              }),
          ],
        ),
      ),
    );
  }

  Widget _buildTimelineItem(
    BuildContext context,
    TimelineEvent event, {
    required bool isFirst,
    required bool isLast,
  }) {
    final theme = Theme.of(context);
    final statusConfig = _getStatusConfig(event.status);

    return TimelineTile(
      isFirst: isFirst,
      isLast: isLast,
      alignment: TimelineAlign.start,
      indicatorStyle: IndicatorStyle(
        width: 32,
        height: 32,
        indicator: Container(
          decoration: BoxDecoration(
            color: statusConfig.color,
            shape: BoxShape.circle,
          ),
          child: Icon(
            event.icon ?? statusConfig.icon,
            color: Colors.white,
            size: 16,
          ),
        ),
      ),
      beforeLineStyle: LineStyle(
        color: theme.dividerColor,
        thickness: 2,
      ),
      endChild: Padding(
        padding: const EdgeInsets.only(left: 16, bottom: 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              event.title,
              style: theme.textTheme.bodyLarge?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            if (event.description != null) ...[
              const SizedBox(height: 4),
              Text(
                event.description!,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
            if (config.showTime) ...[
              const SizedBox(height: 4),
              Text(
                _formatTimestamp(event.timestamp),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  _StatusConfig _getStatusConfig(String? status) {
    switch (status?.toLowerCase()) {
      case 'completed':
        return _StatusConfig(
          icon: Icons.check_circle,
          color: Colors.green.shade500,
        );
      case 'in_progress':
        return _StatusConfig(
          icon: Icons.radio_button_checked,
          color: Colors.blue.shade500,
        );
      case 'pending':
      default:
        return _StatusConfig(
          icon: Icons.circle,
          color: Colors.grey.shade400,
        );
    }
  }

  String _formatTimestamp(DateTime timestamp) {
    return '${timestamp.year}-${timestamp.month.toString().padLeft(2, '0')}-${timestamp.day.toString().padLeft(2, '0')} '
        '${timestamp.hour.toString().padLeft(2, '0')}:${timestamp.minute.toString().padLeft(2, '0')}';
  }
}

class _StatusConfig {
  final IconData icon;
  final Color color;

  _StatusConfig({
    required this.icon,
    required this.color,
  });
}
