import 'package:flutter/material.dart';
import 'widget_registry.dart';

/// 指标卡片组件配置
class MetricCardsConfig extends ComponentConfig {
  final List<MetricCardData> metrics;
  final int columns;

  MetricCardsConfig({
    required Map<String, dynamic> data,
    required Map<String, dynamic> config,
    required this.metrics,
    required this.columns,
  }) : super(type: 'metric_cards', data: data, config: config);

  factory MetricCardsConfig.fromSchema(Map<String, dynamic> schema) {
    final data = schema['data'] as Map<String, dynamic>? ?? {};
    final config = schema['config'] as Map<String, dynamic>? ?? {};

    final metricsData = data['metrics'] as List? ?? [];
    final metrics = metricsData
        .map((m) => MetricCardData.fromJson(m as Map<String, dynamic>))
        .toList();

    final columns = config.getInt('columns') ?? 2;

    return MetricCardsConfig(
      data: data,
      config: config,
      metrics: metrics,
      columns: columns,
    );
  }
}

/// 单个指标卡片数据
class MetricCardData {
  final String label;
  final String value;
  final String? change;
  final String? trend; // 'up', 'down', 'neutral'
  final IconData? icon;

  MetricCardData({
    required this.label,
    required this.value,
    this.change,
    this.trend,
    this.icon,
  });

  factory MetricCardData.fromJson(Map<String, dynamic> json) {
    return MetricCardData(
      label: json.getString('label') ?? '',
      value: json.getString('value') ?? '',
      change: json.getString('change'),
      trend: json.getString('trend'),
      icon: _parseIcon(json.getString('icon')),
    );
  }

  static IconData? _parseIcon(String? iconName) {
    if (iconName == null) return null;

    final iconMap = {
      'trending_up': Icons.trending_up,
      'trending_down': Icons.trending_down,
      'attach_money': Icons.attach_money,
      'people': Icons.people,
      'shopping_cart': Icons.shopping_cart,
      'analytics': Icons.analytics,
      'speed': Icons.speed,
      'star': Icons.star,
    };

    return iconMap[iconName];
  }
}

/// 指标卡片组件
class MetricCardsWidget extends StatelessWidget {
  final MetricCardsConfig config;

  const MetricCardsWidget({
    super.key,
    required this.config,
  });

  /// 从 Schema 构建组件
  static Widget fromSchema(Map<String, dynamic> schema) {
    final config = MetricCardsConfig.fromSchema(schema);
    return MetricCardsWidget(config: config);
  }

  @override
  Widget build(BuildContext context) {
    if (config.metrics.isEmpty) {
      return const SizedBox.shrink();
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        // 计算列数（响应式）
        final columns = _calculateColumns(constraints.maxWidth);

        return Wrap(
          spacing: 12,
          runSpacing: 12,
          children: config.metrics.map((metric) {
            final width = (constraints.maxWidth - (columns - 1) * 12) / columns;
            return SizedBox(
              width: width,
              child: _buildMetricCard(context, metric),
            );
          }).toList(),
        );
      },
    );
  }

  int _calculateColumns(double width) {
    if (width < 600) return 1;
    if (width < 900) return 2;
    return config.columns.clamp(1, 4);
  }

  Widget _buildMetricCard(BuildContext context, MetricCardData metric) {
    final theme = Theme.of(context);
    final trendColor = _getTrendColor(metric.trend);
    final trendIcon = _getTrendIcon(metric.trend);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // 标签和图标
            Row(
              children: [
                Expanded(
                  child: Text(
                    metric.label,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (metric.icon != null)
                  Icon(
                    metric.icon,
                    size: 20,
                    color: theme.colorScheme.primary,
                  ),
              ],
            ),
            const SizedBox(height: 12),

            // 数值
            Text(
              metric.value,
              style: theme.textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.onSurface,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),

            // 变化趋势
            if (metric.change != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  if (trendIcon != null)
                    Icon(
                      trendIcon,
                      size: 16,
                      color: trendColor,
                    ),
                  const SizedBox(width: 4),
                  Text(
                    metric.change!,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: trendColor,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getTrendColor(String? trend) {
    switch (trend) {
      case 'up':
        return Colors.green.shade600;
      case 'down':
        return Colors.red.shade600;
      case 'neutral':
      default:
        return Colors.grey.shade600;
    }
  }

  IconData? _getTrendIcon(String? trend) {
    switch (trend) {
      case 'up':
        return Icons.arrow_upward;
      case 'down':
        return Icons.arrow_downward;
      case 'neutral':
        return Icons.remove;
      default:
        return null;
    }
  }
}
