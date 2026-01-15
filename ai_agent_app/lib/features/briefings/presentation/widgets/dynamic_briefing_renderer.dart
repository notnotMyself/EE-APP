import 'package:flutter/material.dart';
import 'dynamic/widget_registry.dart';
import 'dynamic/metric_cards_widget.dart';
import 'dynamic/chart_widgets.dart';
import 'dynamic/list_widgets.dart';
import 'dynamic/table_widget.dart';
import 'dynamic/markdown_widget.dart';

/// 动态简报渲染器
///
/// 负责：
/// - 注册所有 A2UI 组件
/// - 解析 UI Schema
/// - 渲染动态 UI
class DynamicBriefingRenderer {
  static final DynamicBriefingRenderer _instance = DynamicBriefingRenderer._internal();
  factory DynamicBriefingRenderer() => _instance;
  DynamicBriefingRenderer._internal() {
    _registerComponents();
  }

  final WidgetRegistry _registry = WidgetRegistry();

  /// 注册所有组件
  void _registerComponents() {
    _registry.register('metric_cards', MetricCardsWidget.fromSchema);
    _registry.register('line_chart', LineChartWidget.fromSchema);
    _registry.register('bar_chart', BarChartWidget.fromSchema);
    _registry.register('alert_list', AlertListWidget.fromSchema);
    _registry.register('timeline', TimelineWidget.fromSchema);
    _registry.register('table', TableWidget.fromSchema);
    _registry.register('markdown', MarkdownWidget.fromSchema);
  }

  /// 从 UI Schema 渲染单个组件
  Widget renderComponent(Map<String, dynamic> schema) {
    return _registry.buildWidget(schema);
  }

  /// 从 UI Schema 列表渲染多个组件
  Widget renderComponents(List<Map<String, dynamic>> schemas) {
    if (schemas.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: schemas.map((schema) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: renderComponent(schema),
        );
      }).toList(),
    );
  }

  /// 从 JSON 字符串渲染组件
  Widget renderFromJson(String jsonString) {
    return _registry.buildFromJson(jsonString);
  }
}

/// 动态简报页面
///
/// 使用示例：
/// ```dart
/// DynamicBriefingPage(
///   title: '日报',
///   uiSchemas: briefing.uiSchema,
/// )
/// ```
class DynamicBriefingPage extends StatelessWidget {
  final String title;
  final List<Map<String, dynamic>> uiSchemas;
  final Widget? header;
  final Widget? footer;

  const DynamicBriefingPage({
    super.key,
    required this.title,
    required this.uiSchemas,
    this.header,
    this.footer,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final renderer = DynamicBriefingRenderer();

    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        elevation: 0,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (header != null) ...[
                header!,
                const SizedBox(height: 16),
              ],
              if (uiSchemas.isEmpty)
                Center(
                  child: Padding(
                    padding: const EdgeInsets.all(48),
                    child: Column(
                      children: [
                        Icon(
                          Icons.inbox_outlined,
                          size: 64,
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          '暂无内容',
                          style: theme.textTheme.titleMedium?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                )
              else
                renderer.renderComponents(uiSchemas),
              if (footer != null) ...[
                const SizedBox(height: 16),
                footer!,
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// 动态简报组件（可嵌入到其他页面）
///
/// 使用示例：
/// ```dart
/// DynamicBriefingWidget(
///   uiSchemas: briefing.uiSchema,
///   padding: EdgeInsets.all(16),
/// )
/// ```
class DynamicBriefingWidget extends StatelessWidget {
  final List<Map<String, dynamic>> uiSchemas;
  final EdgeInsets? padding;

  const DynamicBriefingWidget({
    super.key,
    required this.uiSchemas,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    final renderer = DynamicBriefingRenderer();

    return Padding(
      padding: padding ?? EdgeInsets.zero,
      child: renderer.renderComponents(uiSchemas),
    );
  }
}

/// 单个动态组件（用于预览或测试）
class DynamicComponentWidget extends StatelessWidget {
  final Map<String, dynamic> schema;

  const DynamicComponentWidget({
    super.key,
    required this.schema,
  });

  @override
  Widget build(BuildContext context) {
    final renderer = DynamicBriefingRenderer();
    return renderer.renderComponent(schema);
  }
}
