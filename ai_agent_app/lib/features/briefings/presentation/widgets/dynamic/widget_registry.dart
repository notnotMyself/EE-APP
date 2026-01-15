import 'package:flutter/material.dart';
import 'dart:convert';

/// A2UI 组件注册表
///
/// 负责将 JSON UI Schema 映射到对应的 Flutter Widget
class WidgetRegistry {
  static final WidgetRegistry _instance = WidgetRegistry._internal();
  factory WidgetRegistry() => _instance;
  WidgetRegistry._internal();

  /// 组件构建器映射表
  final Map<String, WidgetBuilder> _builders = {};

  /// 注册组件构建器
  void register(String type, WidgetBuilder builder) {
    _builders[type] = builder;
  }

  /// 根据 UI Schema 构建 Widget
  Widget buildWidget(Map<String, dynamic> schema) {
    try {
      final type = schema['type'] as String?;
      if (type == null || type.isEmpty) {
        return _buildErrorWidget('Missing component type');
      }

      final builder = _builders[type];
      if (builder == null) {
        return _buildErrorWidget('Unknown component type: $type');
      }

      return builder(schema);
    } catch (e, stackTrace) {
      debugPrint('Error building widget from schema: $e\n$stackTrace');
      return _buildErrorWidget('Failed to build component: $e');
    }
  }

  /// 从 JSON 字符串构建 Widget
  Widget buildFromJson(String jsonString) {
    try {
      final schema = jsonDecode(jsonString) as Map<String, dynamic>;
      return buildWidget(schema);
    } catch (e) {
      return _buildErrorWidget('Invalid JSON: $e');
    }
  }

  /// 构建错误提示 Widget
  Widget _buildErrorWidget(String message) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        border: Border.all(color: Colors.red.shade200),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, color: Colors.red.shade700),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              message,
              style: TextStyle(color: Colors.red.shade700),
            ),
          ),
        ],
      ),
    );
  }

  /// 清空所有注册的构建器
  void clear() {
    _builders.clear();
  }
}

/// Widget 构建器类型定义
typedef WidgetBuilder = Widget Function(Map<String, dynamic> schema);

/// 组件配置基类
abstract class ComponentConfig {
  final String type;
  final Map<String, dynamic> data;
  final Map<String, dynamic> config;

  ComponentConfig({
    required this.type,
    required this.data,
    required this.config,
  });

  /// 从 Schema 创建配置
  factory ComponentConfig.fromSchema(Map<String, dynamic> schema) {
    throw UnimplementedError('Subclass must implement fromSchema');
  }
}

/// 安全获取配置值的辅助方法
extension SchemaHelpers on Map<String, dynamic> {
  /// 安全获取字符串
  String? getString(String key) {
    final value = this[key];
    return value is String ? value : null;
  }

  /// 安全获取整数
  int? getInt(String key) {
    final value = this[key];
    if (value is int) return value;
    if (value is String) return int.tryParse(value);
    return null;
  }

  /// 安全获取双精度浮点数
  double? getDouble(String key) {
    final value = this[key];
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }

  /// 安全获取布尔值
  bool? getBool(String key) {
    final value = this[key];
    if (value is bool) return value;
    if (value is String) {
      return value.toLowerCase() == 'true';
    }
    return null;
  }

  /// 安全获取列表
  List<T>? getList<T>(String key) {
    final value = this[key];
    if (value is List) {
      try {
        return value.cast<T>();
      } catch (e) {
        debugPrint('Failed to cast list to $T: $e');
        return null;
      }
    }
    return null;
  }

  /// 安全获取映射
  Map<String, dynamic>? getMap(String key) {
    final value = this[key];
    return value is Map<String, dynamic> ? value : null;
  }

  /// 获取嵌套值
  dynamic getNested(List<String> keys) {
    dynamic current = this;
    for (final key in keys) {
      if (current is Map) {
        current = current[key];
      } else {
        return null;
      }
    }
    return current;
  }
}
