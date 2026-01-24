import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../controllers/update_controller.dart';

/// 显示更新对话框
Future<void> showUpdateDialog(
  BuildContext context, {
  required bool force,
}) {
  return showDialog(
    context: context,
    barrierDismissible: !force, // 强制更新时不允许关闭
    builder: (context) => UpdateDialog(forceUpdate: force),
  );
}

/// 更新对话框
class UpdateDialog extends ConsumerWidget {
  final bool forceUpdate;

  const UpdateDialog({
    super.key,
    this.forceUpdate = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(updateControllerProvider);
    final controller = ref.read(updateControllerProvider.notifier);
    final version = state.updateResponse?.latestVersion;

    if (version == null) {
      return const SizedBox.shrink();
    }

    return PopScope(
      canPop: !forceUpdate && state.downloadStatus != DownloadStatus.downloading,
      child: AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.system_update, color: Colors.blue),
            const SizedBox(width: 8),
            const Text('发现新版本'),
            if (forceUpdate)
              Container(
                margin: const EdgeInsets.only(left: 8),
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.red,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: const Text(
                  '强制',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                  ),
                ),
              ),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 版本信息
              Text(
                'v${version.versionName}',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                '大小: ${(version.apkSize / 1024 / 1024).toStringAsFixed(1)}MB',
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 16),

              // 更新说明
              const Text(
                '更新内容',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 8),
              Container(
                constraints: const BoxConstraints(maxHeight: 200),
                child: Markdown(
                  data: version.releaseNotes,
                  shrinkWrap: true,
                  padding: EdgeInsets.zero,
                  styleSheet: MarkdownStyleSheet(
                    p: const TextStyle(fontSize: 14),
                    h1: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    h2: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // 下载进度
              if (state.downloadStatus == DownloadStatus.downloading ||
                  state.downloadStatus == DownloadStatus.installing)
                Column(
                  children: [
                    LinearProgressIndicator(
                      value: state.downloadProgress?.percentage,
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          state.downloadStatus == DownloadStatus.installing
                              ? '正在安装...'
                              : '正在下载...',
                          style: const TextStyle(fontSize: 12),
                        ),
                        if (state.downloadProgress != null)
                          Text(
                            state.downloadProgress!.percentageText,
                            style: const TextStyle(fontSize: 12),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    if (state.downloadProgress != null)
                      Text(
                        state.downloadProgress!.progressText,
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.grey[600],
                        ),
                      ),
                  ],
                ),

              // 错误信息
              if (state.errorMessage != null)
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.red[50],
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline, color: Colors.red, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          state.errorMessage!,
                          style: const TextStyle(color: Colors.red, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ),
        actions: [
          // 取消按钮（非强制更新且未下载时显示）
          if (!forceUpdate && state.downloadStatus != DownloadStatus.downloading)
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('稍后更新'),
            ),

          // 取消下载按钮
          if (state.downloadStatus == DownloadStatus.downloading)
            TextButton(
              onPressed: () {
                controller.cancelDownload();
                if (!forceUpdate) {
                  Navigator.of(context).pop();
                }
              },
              child: const Text('取消'),
            ),

          // 更新/重试按钮
          if (state.downloadStatus != DownloadStatus.downloading &&
              state.downloadStatus != DownloadStatus.installing)
            FilledButton(
              onPressed: state.downloadStatus == DownloadStatus.failed
                  ? () => controller.downloadAndInstall()
                  : () => controller.downloadAndInstall(),
              child: Text(
                state.downloadStatus == DownloadStatus.failed
                    ? '重试'
                    : state.downloadStatus == DownloadStatus.completed
                        ? '立即安装'
                        : '立即更新',
              ),
            ),

          // 备用下载源（下载失败时显示）
          if (state.downloadStatus == DownloadStatus.failed &&
              version.downloadSources.isNotEmpty)
            PopupMenuButton<int>(
              icon: const Icon(Icons.more_horiz),
              tooltip: '选择其他下载源',
              onSelected: (index) => controller.downloadFromMirror(index),
              itemBuilder: (context) => version.downloadSources
                  .asMap()
                  .entries
                  .map(
                    (entry) => PopupMenuItem<int>(
                      value: entry.key,
                      child: Row(
                        children: [
                          Icon(
                            Icons.download,
                            size: 18,
                            color: entry.value.speed == 'fast'
                                ? Colors.green
                                : entry.value.speed == 'slow'
                                    ? Colors.orange
                                    : Colors.grey,
                          ),
                          const SizedBox(width: 8),
                          Text(entry.value.name),
                        ],
                      ),
                    ),
                  )
                  .toList(),
            ),
        ],
      ),
    );
  }
}
