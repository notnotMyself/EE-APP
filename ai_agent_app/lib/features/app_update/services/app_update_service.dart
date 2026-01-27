import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../presentation/controllers/update_controller.dart';
import '../presentation/widgets/update_dialog.dart';

/// 应用更新服务
class AppUpdateService {
  /// 在应用启动时检查更新
  static Future<void> checkUpdateOnStartup(
    BuildContext context,
    WidgetRef ref, {
    bool silent = false, // 静默检查（无更新时不提示）
  }) async {
    final controller = ref.read(updateControllerProvider.notifier);

    try {
      // 🔍 调试：获取当前版本信息
      final repository = ref.read(updateRepositoryProvider);
      final currentVersionCode = await repository.getCurrentVersionCode();
      final currentVersionName = await repository.getCurrentVersionName();
      print('🔍 [UpdateCheck] Current version: $currentVersionName (code: $currentVersionCode)');

      // 检查更新
      print('🔍 [UpdateCheck] Checking for updates...');
      await controller.checkUpdate();

      final state = ref.read(updateControllerProvider);
      print('🔍 [UpdateCheck] Check status: ${state.checkStatus}');

      if (state.checkStatus == UpdateCheckStatus.hasUpdate) {
        final version = state.updateResponse?.latestVersion;
        print('🔍 [UpdateCheck] Has update! Latest: ${version?.versionName} (code: ${version?.versionCode})');
        if (version != null && context.mounted) {
          print('🔍 [UpdateCheck] Showing update dialog (force: ${version.forceUpdate})');
          // 显示更新对话框
          await showUpdateDialog(
            context,
            force: version.forceUpdate,
          );
        } else {
          print('⚠️  [UpdateCheck] Cannot show dialog: version=${version != null}, mounted=${context.mounted}');
        }
      } else if (!silent && state.checkStatus == UpdateCheckStatus.noUpdate) {
        print('🔍 [UpdateCheck] Already latest version');
        // 非静默模式下，无更新时也提示
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('已是最新版本')),
          );
        }
      } else if (state.checkStatus == UpdateCheckStatus.error) {
        print('❌ [UpdateCheck] Error: ${state.errorMessage}');
      }
    } catch (e, stack) {
      print('❌ [UpdateCheck] Exception: $e');
      print('Stack trace: $stack');
      if (!silent && context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('检查更新失败: $e')),
        );
      }
    }
  }

  /// 手动检查更新（从设置页面调用）
  static Future<void> checkUpdateManually(
    BuildContext context,
    WidgetRef ref,
  ) async {
    // 显示加载提示
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('正在检查更新...')),
      );
    }

    await checkUpdateOnStartup(context, ref, silent: false);
  }
}
