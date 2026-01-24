/// 法律文档模型
///
/// 表示隐私政策或服务条款文档
class LegalDocument {
  /// 文档ID
  final String id;

  /// 文档类型: privacy_policy 或 terms_of_service
  final String type;

  /// 文档标题
  final String title;

  /// 文档内容 (Markdown格式)
  final String content;

  /// 文档版本号
  final String version;

  /// 生效日期
  final DateTime effectiveDate;

  /// 创建时间
  final DateTime createdAt;

  /// 是否为当前有效版本
  final bool isActive;

  LegalDocument({
    required this.id,
    required this.type,
    required this.title,
    required this.content,
    required this.version,
    required this.effectiveDate,
    required this.createdAt,
    required this.isActive,
  });

  /// 从JSON创建LegalDocument对象
  factory LegalDocument.fromJson(Map<String, dynamic> json) {
    return LegalDocument(
      id: json['id'] as String,
      type: json['document_type'] as String,  // Backend uses 'document_type'
      title: json['title'] as String,
      content: json['content'] as String,
      version: json['version'] as String,
      effectiveDate: DateTime.parse(json['effective_date'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'title': title,
      'content': content,
      'version': version,
      'effective_date': effectiveDate.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'is_active': isActive,
    };
  }

  /// 获取文档类型的显示名称
  String get typeDisplayName {
    switch (type) {
      case 'privacy_policy':
        return '隐私政策';
      case 'terms_of_service':
        return '服务条款';
      default:
        return type;
    }
  }

  @override
  String toString() {
    return 'LegalDocument(id: $id, type: $type, title: $title, version: $version)';
  }
}
