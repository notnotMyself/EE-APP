import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'widget_registry.dart';

/// Markdown 组件配置
class MarkdownConfig extends ComponentConfig {
  final String content;
  final bool selectable;

  MarkdownConfig({
    required Map<String, dynamic> data,
    required Map<String, dynamic> config,
    required this.content,
    required this.selectable,
  }) : super(type: 'markdown', data: data, config: config);

  factory MarkdownConfig.fromSchema(Map<String, dynamic> schema) {
    final data = schema['data'] as Map<String, dynamic>? ?? {};
    final config = schema['config'] as Map<String, dynamic>? ?? {};

    return MarkdownConfig(
      data: data,
      config: config,
      content: data.getString('content') ?? '',
      selectable: config.getBool('selectable') ?? true,
    );
  }
}

class MarkdownWidget extends StatelessWidget {
  final MarkdownConfig config;

  const MarkdownWidget({
    super.key,
    required this.config,
  });

  static Widget fromSchema(Map<String, dynamic> schema) {
    final config = MarkdownConfig.fromSchema(schema);
    return MarkdownWidget(config: config);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (config.content.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: config.selectable
            ? MarkdownBody(
                data: config.content,
                selectable: true,
                styleSheet: _buildMarkdownStyleSheet(theme),
              )
            : MarkdownBody(
                data: config.content,
                styleSheet: _buildMarkdownStyleSheet(theme),
              ),
      ),
    );
  }

  MarkdownStyleSheet _buildMarkdownStyleSheet(ThemeData theme) {
    return MarkdownStyleSheet(
      h1: theme.textTheme.headlineLarge?.copyWith(
        fontWeight: FontWeight.bold,
        color: theme.colorScheme.onSurface,
      ),
      h2: theme.textTheme.headlineMedium?.copyWith(
        fontWeight: FontWeight.bold,
        color: theme.colorScheme.onSurface,
      ),
      h3: theme.textTheme.titleLarge?.copyWith(
        fontWeight: FontWeight.bold,
        color: theme.colorScheme.onSurface,
      ),
      h4: theme.textTheme.titleMedium?.copyWith(
        fontWeight: FontWeight.w600,
        color: theme.colorScheme.onSurface,
      ),
      p: theme.textTheme.bodyMedium?.copyWith(
        color: theme.colorScheme.onSurface,
        height: 1.5,
      ),
      code: theme.textTheme.bodyMedium?.copyWith(
        fontFamily: 'monospace',
        backgroundColor: theme.colorScheme.surfaceContainerHighest,
        color: theme.colorScheme.primary,
      ),
      codeblockDecoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: theme.dividerColor),
      ),
      blockquote: theme.textTheme.bodyMedium?.copyWith(
        color: theme.colorScheme.onSurfaceVariant,
        fontStyle: FontStyle.italic,
      ),
      blockquoteDecoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.5),
        borderRadius: BorderRadius.circular(4),
        border: Border(
          left: BorderSide(
            color: theme.colorScheme.primary,
            width: 4,
          ),
        ),
      ),
      listBullet: theme.textTheme.bodyMedium?.copyWith(
        color: theme.colorScheme.primary,
      ),
      tableHead: theme.textTheme.titleSmall?.copyWith(
        fontWeight: FontWeight.bold,
        color: theme.colorScheme.onSurface,
      ),
      tableBody: theme.textTheme.bodyMedium?.copyWith(
        color: theme.colorScheme.onSurface,
      ),
      tableBorder: TableBorder.all(
        color: theme.dividerColor,
        width: 1,
      ),
      a: theme.textTheme.bodyMedium?.copyWith(
        color: theme.colorScheme.primary,
        decoration: TextDecoration.underline,
      ),
      strong: theme.textTheme.bodyMedium?.copyWith(
        fontWeight: FontWeight.bold,
        color: theme.colorScheme.onSurface,
      ),
      em: theme.textTheme.bodyMedium?.copyWith(
        fontStyle: FontStyle.italic,
        color: theme.colorScheme.onSurface,
      ),
    );
  }
}
