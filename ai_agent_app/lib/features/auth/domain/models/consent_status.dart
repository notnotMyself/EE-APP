/// 用户同意状态模型
///
/// 记录用户对隐私政策和服务条款的同意状态
/// 匹配后端 /api/v1/legal/check-consent-status 接口返回格式
class ConsentStatus {
  /// 隐私政策是否已同意
  final bool privacyPolicyConsented;

  /// 服务条款是否已同意
  final bool termsOfServiceConsented;

  /// 所有必需文档是否都已同意
  final bool allConsented;

  ConsentStatus({
    required this.privacyPolicyConsented,
    required this.termsOfServiceConsented,
    required this.allConsented,
  });

  /// 是否需要同意（任何一个文档未同意则为true）
  bool get needsConsent => !allConsented;

  /// 从JSON创建ConsentStatus对象
  factory ConsentStatus.fromJson(Map<String, dynamic> json) {
    return ConsentStatus(
      privacyPolicyConsented: json['privacy_policy_consented'] as bool? ?? false,
      termsOfServiceConsented: json['terms_of_service_consented'] as bool? ?? false,
      allConsented: json['all_consented'] as bool? ?? false,
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'privacy_policy_consented': privacyPolicyConsented,
      'terms_of_service_consented': termsOfServiceConsented,
      'all_consented': allConsented,
    };
  }

  @override
  String toString() {
    return 'ConsentStatus(privacyPolicy: $privacyPolicyConsented, termsOfService: $termsOfServiceConsented, all: $allConsented)';
  }
}
