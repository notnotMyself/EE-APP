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
      // 检查更新
      await controller.checkUpdate();

      final state = ref.read(updateControllerProvider);

      if (state.checkStatus == UpdateCheckStatus.hasUpdate) {
        final version = state.updateResponse?.latestVersion;
        if (version != null && context.mounted) {
          // 显示更新对话框
          await showUpdateDialog(
            context,
            force: version.forceUpdate,
          );
        }
      } else if (!silent && state.checkStatus == UpdateCheckStatus.noUpdate) {
        // 非静默模式下，无更新时也提示
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('已是最新版本')),
          );
        }
      }
    } catch (e) {
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
