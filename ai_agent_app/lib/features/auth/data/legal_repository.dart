import 'package:dio/dio.dart';
import '../../../core/config/app_config.dart';
import '../../../core/network/authenticated_http_client.dart';
import '../domain/models/legal_document.dart';
import '../domain/models/consent_status.dart';

/// 法律文档Repository
/// 处理隐私政策、服务条款的获取和用户同意记录
class LegalRepository {
  final _dio = Dio();

  /// 获取法律文档
  ///
  /// [type] 文档类型: 'privacy_policy' 或 'terms_of_service'
  /// 返回法律文档对象
  Future<LegalDocument> getLegalDocument(String type) async {
    try {
      final response = await _dio.get(
        '${AppConfig.apiUrl}/legal/documents/$type',
      );

      // Backend uses FastAPI response_model, returns data directly
      return LegalDocument.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw Exception('法律文档不存在');
      }
      rethrow;
    } catch (e) {
      throw Exception('获取法律文档失败: $e');
    }
  }

  /// 获取所有法律文档
  ///
  /// 返回所有可用的法律文档列表（隐私政策和用户协议）
  Future<List<LegalDocument>> getAllLegalDocuments() async {
    try {
      // Backend doesn't have a single endpoint for all documents
      // Fetch privacy_policy and terms_of_service individually
      final results = await Future.wait([
        getLegalDocument('privacy_policy'),
        getLegalDocument('terms_of_service'),
      ]);

      return results;
    } catch (e) {
      throw Exception('获取法律文档列表失败: $e');
    }
  }

  /// 创建用户同意记录
  ///
  /// [documentId] 法律文档ID
  /// 需要用户已登录（使用JWT token验证）
  Future<void> createConsent({
    required String documentId,
  }) async {
    try {
      final authHeaders = await AuthenticatedHttpClient.getAuthHeaders();

      final response = await _dio.post(
        '${AppConfig.apiUrl}/legal/consent',
        data: {
          'document_id': documentId,
        },
        options: Options(headers: authHeaders),
      );

      // Backend returns ConsentResponse directly via response_model
      // Success if no exception is thrown
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('用户未登录，无法记录同意');
      } else if (e.response?.statusCode == 409) {
        // 409 Conflict: 用户已经同意过此文档
        // 这种情况可以静默处理，不抛出异常
        return;
      }
      rethrow;
    } catch (e) {
      throw Exception('记录用户同意失败: $e');
    }
  }

  /// 检查用户同意状态
  ///
  /// 返回用户对各法律文档的同意状态
  /// 需要用户已登录（使用JWT token验证）
  Future<ConsentStatus> checkConsentStatus() async {
    try {
      final authHeaders = await AuthenticatedHttpClient.getAuthHeaders();

      final response = await _dio.get(
        '${AppConfig.apiUrl}/legal/check-consent-status',
        options: Options(headers: authHeaders),
      );

      // Backend returns data directly: {privacy_policy_consented, terms_of_service_consented, all_consented}
      return ConsentStatus.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('用户未登录，无法检查同意状态');
      }
      rethrow;
    } catch (e) {
      throw Exception('检查同意状态失败: $e');
    }
  }
}
