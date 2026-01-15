import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'widget_registry.dart';

/// ========== 折线图组件 ==========

/// 折线图配置
class LineChartConfig extends ComponentConfig {
  final String title;
  final List<LineChartSeriesData> series;
  final List<String> xLabels;
  final String? xAxisLabel;
  final String? yAxisLabel;
  final bool showGrid;
  final bool showLegend;

  LineChartConfig({
    required Map<String, dynamic> data,
    required Map<String, dynamic> config,
    required this.title,
    required this.series,
    required this.xLabels,
    this.xAxisLabel,
    this.yAxisLabel,
    required this.showGrid,
    required this.showLegend,
  }) : super(type: 'line_chart', data: data, config: config);

  factory LineChartConfig.fromSchema(Map<String, dynamic> schema) {
    final data = schema['data'] as Map<String, dynamic>? ?? {};
    final config = schema['config'] as Map<String, dynamic>? ?? {};

    final seriesData = data.getList<Map<String, dynamic>>('series') ?? [];
    final series = seriesData
        .map((s) => LineChartSeriesData.fromJson(s))
        .toList();

    final xLabels = data.getList<String>('x_labels') ?? [];

    return LineChartConfig(
      data: data,
      config: config,
      title: data.getString('title') ?? '',
      series: series,
      xLabels: xLabels,
      xAxisLabel: data.getString('x_axis_label'),
      yAxisLabel: data.getString('y_axis_label'),
      showGrid: config.getBool('show_grid') ?? true,
      showLegend: config.getBool('show_legend') ?? true,
    );
  }
}

class LineChartSeriesData {
  final String name;
  final List<double> values;
  final Color color;

  LineChartSeriesData({
    required this.name,
    required this.values,
    required this.color,
  });

  factory LineChartSeriesData.fromJson(Map<String, dynamic> json) {
    final valuesData = json['values'] as List? ?? [];
    final values = valuesData.map((v) {
      if (v is num) return v.toDouble();
      if (v is String) return double.tryParse(v) ?? 0.0;
      return 0.0;
    }).toList();

    return LineChartSeriesData(
      name: json.getString('name') ?? '',
      values: values,
      color: _parseColor(json.getString('color')) ?? Colors.blue,
    );
  }

  static Color? _parseColor(String? colorStr) {
    if (colorStr == null) return null;
    final colorMap = {
      'blue': Colors.blue,
      'red': Colors.red,
      'green': Colors.green,
      'orange': Colors.orange,
      'purple': Colors.purple,
      'teal': Colors.teal,
    };
    return colorMap[colorStr.toLowerCase()];
  }
}

class LineChartWidget extends StatelessWidget {
  final LineChartConfig config;

  const LineChartWidget({
    super.key,
    required this.config,
  });

  static Widget fromSchema(Map<String, dynamic> schema) {
    final config = LineChartConfig.fromSchema(schema);
    return LineChartWidget(config: config);
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
            // 标题
            if (config.title.isNotEmpty) ...[
              Text(
                config.title,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
            ],

            // 图表
            SizedBox(
              height: 250,
              child: LineChart(
                _buildChartData(theme),
              ),
            ),

            // 图例
            if (config.showLegend && config.series.isNotEmpty) ...[
              const SizedBox(height: 16),
              _buildLegend(theme),
            ],
          ],
        ),
      ),
    );
  }

  LineChartData _buildChartData(ThemeData theme) {
    final maxValue = config.series
        .expand((s) => s.values)
        .fold<double>(0, (max, v) => v > max ? v : max);

    return LineChartData(
      gridData: FlGridData(
        show: config.showGrid,
        drawVerticalLine: true,
        horizontalInterval: maxValue / 5,
      ),
      titlesData: FlTitlesData(
        show: true,
        rightTitles: const AxisTitles(
          sideTitles: SideTitles(showTitles: false),
        ),
        topTitles: const AxisTitles(
          sideTitles: SideTitles(showTitles: false),
        ),
        bottomTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            reservedSize: 30,
            interval: 1,
            getTitlesWidget: (value, meta) {
              final index = value.toInt();
              if (index < 0 || index >= config.xLabels.length) {
                return const SizedBox.shrink();
              }
              return Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  config.xLabels[index],
                  style: theme.textTheme.bodySmall,
                ),
              );
            },
          ),
        ),
        leftTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            reservedSize: 40,
            getTitlesWidget: (value, meta) {
              return Text(
                value.toStringAsFixed(0),
                style: theme.textTheme.bodySmall,
              );
            },
          ),
        ),
      ),
      borderData: FlBorderData(
        show: true,
        border: Border.all(color: theme.dividerColor),
      ),
      lineBarsData: config.series.asMap().entries.map((entry) {
        final series = entry.value;
        return LineChartBarData(
          spots: series.values.asMap().entries.map((e) {
            return FlSpot(e.key.toDouble(), e.value);
          }).toList(),
          isCurved: true,
          color: series.color,
          barWidth: 3,
          isStrokeCapRound: true,
          dotData: const FlDotData(show: true),
          belowBarData: BarAreaData(
            show: true,
            color: series.color.withOpacity(0.1),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildLegend(ThemeData theme) {
    return Wrap(
      spacing: 16,
      runSpacing: 8,
      children: config.series.map((series) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: series.color,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 6),
            Text(
              series.name,
              style: theme.textTheme.bodySmall,
            ),
          ],
        );
      }).toList(),
    );
  }
}

/// ========== 柱状图组件 ==========

class BarChartConfig extends ComponentConfig {
  final String title;
  final List<BarChartSeriesData> series;
  final List<String> xLabels;
  final bool showGrid;
  final bool showLegend;

  BarChartConfig({
    required Map<String, dynamic> data,
    required Map<String, dynamic> config,
    required this.title,
    required this.series,
    required this.xLabels,
    required this.showGrid,
    required this.showLegend,
  }) : super(type: 'bar_chart', data: data, config: config);

  factory BarChartConfig.fromSchema(Map<String, dynamic> schema) {
    final data = schema['data'] as Map<String, dynamic>? ?? {};
    final config = schema['config'] as Map<String, dynamic>? ?? {};

    final seriesData = data.getList<Map<String, dynamic>>('series') ?? [];
    final series = seriesData
        .map((s) => BarChartSeriesData.fromJson(s))
        .toList();

    return BarChartConfig(
      data: data,
      config: config,
      title: data.getString('title') ?? '',
      series: series,
      xLabels: data.getList<String>('x_labels') ?? [],
      showGrid: config.getBool('show_grid') ?? true,
      showLegend: config.getBool('show_legend') ?? true,
    );
  }
}

class BarChartSeriesData {
  final String name;
  final List<double> values;
  final Color color;

  BarChartSeriesData({
    required this.name,
    required this.values,
    required this.color,
  });

  factory BarChartSeriesData.fromJson(Map<String, dynamic> json) {
    final valuesData = json['values'] as List? ?? [];
    final values = valuesData.map((v) {
      if (v is num) return v.toDouble();
      if (v is String) return double.tryParse(v) ?? 0.0;
      return 0.0;
    }).toList();

    return BarChartSeriesData(
      name: json.getString('name') ?? '',
      values: values,
      color: LineChartSeriesData._parseColor(json.getString('color')) ??
          Colors.blue,
    );
  }
}

class BarChartWidget extends StatelessWidget {
  final BarChartConfig config;

  const BarChartWidget({
    super.key,
    required this.config,
  });

  static Widget fromSchema(Map<String, dynamic> schema) {
    final config = BarChartConfig.fromSchema(schema);
    return BarChartWidget(config: config);
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
            SizedBox(
              height: 250,
              child: BarChart(
                _buildChartData(theme),
              ),
            ),
            if (config.showLegend && config.series.isNotEmpty) ...[
              const SizedBox(height: 16),
              _buildLegend(theme),
            ],
          ],
        ),
      ),
    );
  }

  BarChartData _buildChartData(ThemeData theme) {
    final maxValue = config.series
        .expand((s) => s.values)
        .fold<double>(0, (max, v) => v > max ? v : max);

    return BarChartData(
      alignment: BarChartAlignment.spaceAround,
      maxY: maxValue * 1.2,
      barTouchData: BarTouchData(enabled: true),
      titlesData: FlTitlesData(
        show: true,
        rightTitles: const AxisTitles(
          sideTitles: SideTitles(showTitles: false),
        ),
        topTitles: const AxisTitles(
          sideTitles: SideTitles(showTitles: false),
        ),
        bottomTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            reservedSize: 30,
            getTitlesWidget: (value, meta) {
              final index = value.toInt();
              if (index < 0 || index >= config.xLabels.length) {
                return const SizedBox.shrink();
              }
              return Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  config.xLabels[index],
                  style: theme.textTheme.bodySmall,
                ),
              );
            },
          ),
        ),
        leftTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            reservedSize: 40,
            getTitlesWidget: (value, meta) {
              return Text(
                value.toStringAsFixed(0),
                style: theme.textTheme.bodySmall,
              );
            },
          ),
        ),
      ),
      gridData: FlGridData(
        show: config.showGrid,
        drawVerticalLine: false,
      ),
      borderData: FlBorderData(
        show: true,
        border: Border.all(color: theme.dividerColor),
      ),
      barGroups: _buildBarGroups(),
    );
  }

  List<BarChartGroupData> _buildBarGroups() {
    final groupCount = config.xLabels.length;
    final seriesCount = config.series.length;

    return List.generate(groupCount, (groupIndex) {
      return BarChartGroupData(
        x: groupIndex,
        barRods: List.generate(seriesCount, (seriesIndex) {
          final series = config.series[seriesIndex];
          final value = groupIndex < series.values.length
              ? series.values[groupIndex]
              : 0.0;

          return BarChartRodData(
            toY: value,
            color: series.color,
            width: 16,
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(4),
              topRight: Radius.circular(4),
            ),
          );
        }),
      );
    });
  }

  Widget _buildLegend(ThemeData theme) {
    return Wrap(
      spacing: 16,
      runSpacing: 8,
      children: config.series.map((series) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: series.color,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(width: 6),
            Text(
              series.name,
              style: theme.textTheme.bodySmall,
            ),
          ],
        );
      }).toList(),
    );
  }
}
