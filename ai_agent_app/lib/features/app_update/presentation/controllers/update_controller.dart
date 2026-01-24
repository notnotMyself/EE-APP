import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/app_version.dart';
import '../../data/repositories/update_repository.dart';

/// 更新仓库 Provider
final updateRepositoryProvider = Provider<UpdateRepository>((ref) {
  return UpdateRepository();
});

/// 当前版本 Provider
final currentVersionProvider = FutureProvider<({int code, String name})>((ref) async {
  final repository = ref.read(updateRepositoryProvider);
  final code = await repository.getCurrentVersionCode();
  final name = await repository.getCurrentVersionName();
  return (code: code, name: name);
});

/// 更新检查状态
enum UpdateCheckStatus {
  idle,       // 空闲
  checking,   // 检查中
  hasUpdate,  // 有更新
  noUpdate,   // 无更新
  error,      // 错误
}

/// 下载状态
enum DownloadStatus {
  idle,        // 空闲
  downloading, // 下载中
  completed,   // 完成
  failed,      // 失败
  installing,  // 安装中
}

/// 更新控制器状态
class UpdateState {
  final UpdateCheckStatus checkStatus;
  final CheckUpdateResponse? updateResponse;
  final DownloadStatus downloadStatus;
  final DownloadProgress? downloadProgress;
  final String? downloadedFilePath;
  final String? errorMessage;
  final CancelToken? cancelToken;

  const UpdateState({
    this.checkStatus = UpdateCheckStatus.idle,
    this.updateResponse,
    this.downloadStatus = DownloadStatus.idle,
    this.downloadProgress,
    this.downloadedFilePath,
    this.errorMessage,
    this.cancelToken,
  });

  UpdateState copyWith({
    UpdateCheckStatus? checkStatus,
    CheckUpdateResponse? updateResponse,
    DownloadStatus? downloadStatus,
    DownloadProgress? downloadProgress,
    String? downloadedFilePath,
    String? errorMessage,
    CancelToken? cancelToken,
  }) {
    return UpdateState(
      checkStatus: checkStatus ?? this.checkStatus,
      updateResponse: updateResponse ?? this.updateResponse,
      downloadStatus: downloadStatus ?? this.downloadStatus,
      downloadProgress: downloadProgress ?? this.downloadProgress,
      downloadedFilePath: downloadedFilePath ?? this.downloadedFilePath,
      errorMessage: errorMessage ?? this.errorMessage,
      cancelToken: cancelToken ?? this.cancelToken,
    );
  }
}

/// 更新控制器
class UpdateController extends StateNotifier<UpdateState> {
  final UpdateRepository _repository;

  UpdateController(this._repository) : super(const UpdateState());

  /// 检查更新
  Future<void> checkUpdate() async {
    state = state.copyWith(
      checkStatus: UpdateCheckStatus.checking,
      errorMessage: null,
    );

    try {
      final response = await _repository.checkUpdate();

      if (response.hasUpdate) {
        state = state.copyWith(
          checkStatus: UpdateCheckStatus.hasUpdate,
          updateResponse: response,
        );
      } else {
        state = state.copyWith(
          checkStatus: UpdateCheckStatus.noUpdate,
          updateResponse: response,
        );
      }
    } catch (e) {
      state = state.copyWith(
        checkStatus: UpdateCheckStatus.error,
        errorMessage: e.toString(),
      );
    }
  }

  /// 下载并安装更新
  Future<void> downloadAndInstall({String? customUrl}) async {
    if (state.updateResponse?.latestVersion == null && customUrl == null) {
      return;
    }

    final url = customUrl ?? state.updateResponse!.latestVersion!.apkUrl;

    // 创建取消令牌
    final cancelToken = CancelToken();

    state = state.copyWith(
      downloadStatus: DownloadStatus.downloading,
      downloadProgress: const DownloadProgress(received: 0, total: 0),
      errorMessage: null,
      cancelToken: cancelToken,
    );

    try {
      // 下载 APK
      final filePath = await _repository.downloadApk(
        url,
        onProgress: (progress) {
          state = state.copyWith(downloadProgress: progress);
        },
        cancelToken: cancelToken,
      );

      state = state.copyWith(
        downloadStatus: DownloadStatus.completed,
        downloadedFilePath: filePath,
      );

      // 自动安装
      await install();
    } catch (e) {
      if (e is DioException && CancelToken.isCancel(e)) {
        state = state.copyWith(
          downloadStatus: DownloadStatus.idle,
          downloadProgress: null,
          errorMessage: '下载已取消',
        );
      } else {
        state = state.copyWith(
          downloadStatus: DownloadStatus.failed,
          errorMessage: e.toString(),
        );
      }
    }
  }

  /// 安装 APK
  Future<void> install() async {
    if (state.downloadedFilePath == null) {
      return;
    }

    state = state.copyWith(downloadStatus: DownloadStatus.installing);

    try {
      await _repository.installApk(state.downloadedFilePath!);
    } catch (e) {
      state = state.copyWith(
        downloadStatus: DownloadStatus.failed,
        errorMessage: e.toString(),
      );
    }
  }

  /// 取消下载
  void cancelDownload() {
    state.cancelToken?.cancel('用户取消下载');
    state = state.copyWith(
      downloadStatus: DownloadStatus.idle,
      downloadProgress: null,
      cancelToken: null,
    );
  }

  /// 重置状态
  void reset() {
    state = const UpdateState();
  }

  /// 使用备用下载源
  Future<void> downloadFromMirror(int sourceIndex) async {
    if (state.updateResponse?.latestVersion == null) {
      return;
    }

    final sources = state.updateResponse!.latestVersion!.downloadSources;
    if (sourceIndex >= sources.length) {
      return;
    }

    await downloadAndInstall(customUrl: sources[sourceIndex].url);
  }
}

/// 更新控制器 Provider
final updateControllerProvider =
    StateNotifierProvider<UpdateController, UpdateState>((ref) {
  final repository = ref.read(updateRepositoryProvider);
  return UpdateController(repository);
});
