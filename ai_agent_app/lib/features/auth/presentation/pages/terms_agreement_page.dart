import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/error/error_handler.dart';
import '../../data/legal_repository.dart';
import '../../domain/models/legal_document.dart';
import '../controllers/auth_controller.dart';

/// 法律文档Repository Provider
final legalRepositoryProvider = Provider<LegalRepository>((ref) {
  return LegalRepository();
});

/// 法律文档加载Provider
final legalDocumentsProvider = FutureProvider<List<LegalDocument>>((ref) async {
  final repository = ref.read(legalRepositoryProvider);
  return await repository.getAllLegalDocuments();
});

/// 服务条款同意页面
///
/// 显示隐私政策和服务条款，要求用户同意后才能继续使用
class TermsAgreementPage extends ConsumerStatefulWidget {
  const TermsAgreementPage({super.key});

  @override
  ConsumerState<TermsAgreementPage> createState() => _TermsAgreementPageState();
}

class _TermsAgreementPageState extends ConsumerState<TermsAgreementPage> {
  bool _privacyPolicyAgreed = false;
  bool _termsOfServiceAgreed = false;
  bool _isSubmitting = false;

  /// 是否所有必需文档都已同意
  bool get _allAgreed => _privacyPolicyAgreed && _termsOfServiceAgreed;

  /// 处理同意按钮点击
  Future<void> _handleAgree() async {
    if (!_allAgreed) return;

    setState(() {
      _isSubmitting = true;
    });

    try {
      final documents = ref.read(legalDocumentsProvider).value;
      if (documents == null) {
        throw Exception('无法加载法律文档');
      }

      // Submit consent for each document
      final repository = ref.read(legalRepositoryProvider);
      for (final doc in documents) {
        await repository.createConsent(documentId: doc.id);
      }

      // 成功后导航到主页
      if (mounted) {
        context.go('/feed');
      }
    } catch (e) {
      if (mounted) {
        GlobalErrorHandler.showErrorSnackBar(context, e);
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final documentsAsync = ref.watch(legalDocumentsProvider);

    return Scaffold(
      backgroundColor: theme.colorScheme.surface,
      body: SafeArea(
        child: documentsAsync.when(
          data: (documents) => _buildContent(context, documents),
          loading: () => const Center(
            child: CircularProgressIndicator(),
          ),
          error: (error, stack) => _buildErrorView(context, error),
        ),
      ),
    );
  }

  /// 构建内容视图
  Widget _buildContent(BuildContext context, List<LegalDocument> documents) {
    final theme = Theme.of(context);

    // 分离隐私政策和服务条款
    final privacyPolicy = documents.firstWhere(
      (doc) => doc.type == 'privacy_policy',
      orElse: () => throw Exception('找不到隐私政策'),
    );
    final termsOfService = documents.firstWhere(
      (doc) => doc.type == 'terms_of_service',
      orElse: () => throw Exception('找不到服务条款'),
    );

    return Column(
      children: [
        // 顶部标题栏
        _buildHeader(context),

        // 内容区域
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 说明文字
                _buildDescription(theme),
                const SizedBox(height: 24),

                // 隐私政策
                _buildDocumentSection(
                  document: privacyPolicy,
                  isAgreed: _privacyPolicyAgreed,
                  onChanged: (value) {
                    setState(() {
                      _privacyPolicyAgreed = value ?? false;
                    });
                  },
                ),
                const SizedBox(height: 16),

                // 服务条款
                _buildDocumentSection(
                  document: termsOfService,
                  isAgreed: _termsOfServiceAgreed,
                  onChanged: (value) {
                    setState(() {
                      _termsOfServiceAgreed = value ?? false;
                    });
                  },
                ),
              ],
            ),
          ),
        ),

        // 底部按钮
        _buildBottomButton(theme),
      ],
    );
  }

  /// 构建顶部标题栏
  Widget _buildHeader(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(24.0),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        border: Border(
          bottom: BorderSide(
            color: theme.dividerColor,
            width: 1,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '欢迎使用 AI 数字员工平台',
            style: theme.textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.onSurface,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '请仔细阅读并同意以下条款',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.6),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建说明文字
  Widget _buildDescription(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer.withOpacity(0.3),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: theme.colorScheme.primary.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.info_outline,
            color: theme.colorScheme.primary,
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              '为了保护您的权益，请阅读并同意我们的隐私政策和服务条款。这将帮助您了解我们如何收集、使用和保护您的个人信息。',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.8),
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建单个文档区块
  Widget _buildDocumentSection({
    required LegalDocument document,
    required bool isAgreed,
    required ValueChanged<bool?> onChanged,
  }) {
    final theme = Theme.of(context);

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: isAgreed
              ? theme.colorScheme.primary.withOpacity(0.5)
              : theme.dividerColor,
          width: isAgreed ? 2 : 1,
        ),
      ),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        leading: Icon(
          _getDocumentIcon(document.type),
          color: theme.colorScheme.primary,
          size: 28,
        ),
        title: Text(
          document.title,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: theme.colorScheme.onSurface,
          ),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 4.0),
          child: Text(
            '版本 ${document.version} • ${_formatDate(document.effectiveDate)}',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.6),
            ),
          ),
        ),
        children: [
          const Divider(),
          const SizedBox(height: 8),
          // Markdown内容
          Container(
            constraints: const BoxConstraints(maxHeight: 300),
            decoration: BoxDecoration(
              color: theme.colorScheme.surface,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: theme.dividerColor,
                width: 1,
              ),
            ),
            child: Markdown(
              data: document.content,
              padding: const EdgeInsets.all(16),
              shrinkWrap: true,
              styleSheet: MarkdownStyleSheet(
                p: theme.textTheme.bodyMedium?.copyWith(
                  height: 1.6,
                  color: theme.colorScheme.onSurface.withOpacity(0.8),
                ),
                h1: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onSurface,
                ),
                h2: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onSurface,
                ),
                h3: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onSurface,
                ),
                listBullet: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.primary,
                ),
              ),
            ),
          ),
          const SizedBox(height: 12),
          // 同意复选框
          CheckboxListTile(
            value: isAgreed,
            onChanged: onChanged,
            controlAffinity: ListTileControlAffinity.leading,
            contentPadding: EdgeInsets.zero,
            title: Text(
              '我已阅读并同意《${document.title}》',
              style: theme.textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w500,
                color: theme.colorScheme.onSurface,
              ),
            ),
            activeColor: theme.colorScheme.primary,
          ),
        ],
      ),
    );
  }

  /// 构建底部按钮
  Widget _buildBottomButton(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(24.0),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        border: Border(
          top: BorderSide(
            color: theme.dividerColor,
            width: 1,
          ),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SizedBox(
        width: double.infinity,
        height: 50,
        child: ElevatedButton(
          onPressed: _allAgreed && !_isSubmitting ? _handleAgree : null,
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.primary,
            foregroundColor: theme.colorScheme.onPrimary,
            disabledBackgroundColor: theme.colorScheme.onSurface.withOpacity(0.12),
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          child: _isSubmitting
              ? SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      theme.colorScheme.onPrimary,
                    ),
                  ),
                )
              : Text(
                  '同意并继续',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.onPrimary,
                  ),
                ),
        ),
      ),
    );
  }

  /// 构建错误视图
  Widget _buildErrorView(BuildContext context, Object error) {
    final theme = Theme.of(context);

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: theme.colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              '加载法律文档失败',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.onSurface,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              GlobalErrorHandler.handleApiError(error),
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                ref.invalidate(legalDocumentsProvider);
              },
              icon: const Icon(Icons.refresh),
              label: const Text('重试'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 12,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 获取文档图标
  IconData _getDocumentIcon(String type) {
    switch (type) {
      case 'privacy_policy':
        return Icons.privacy_tip_outlined;
      case 'terms_of_service':
        return Icons.description_outlined;
      default:
        return Icons.article_outlined;
    }
  }

  /// 格式化日期
  String _formatDate(DateTime date) {
    return '${date.year}年${date.month}月${date.day}日生效';
  }
}
