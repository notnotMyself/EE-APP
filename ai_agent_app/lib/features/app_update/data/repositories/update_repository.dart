import 'package:dio/dio.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:open_file/open_file.dart';
import 'dart:io';
import '../../../../core/config/app_config.dart';
import '../models/app_version.dart';

/// 应用更新仓库
class UpdateRepository {
  final Dio _dio;

  UpdateRepository({Dio? dio}) : _dio = dio ?? Dio();

  /// 获取当前版本号
  Future<int> getCurrentVersionCode() async {
    final packageInfo = await PackageInfo.fromPlatform();
    return int.tryParse(packageInfo.buildNumber) ?? 1;
  }

  /// 获取当前版本名称
  Future<String> getCurrentVersionName() async {
    final packageInfo = await PackageInfo.fromPlatform();
    return packageInfo.version;
  }

  /// 检查更新
  Future<CheckUpdateResponse> checkUpdate() async {
    try {
      final currentVersion = await getCurrentVersionCode();

      final response = await _dio.get(
        '${AppConfig.apiUrl}/app/version/latest',
        queryParameters: {
          'current_version': currentVersion,
          'region': 'cn', // 可以根据地区动态设置
        },
      );

      return CheckUpdateResponse.fromJson(response.data);
    } catch (e) {
      throw Exception('检查更新失败: $e');
    }
  }

  /// 下载 APK
  Future<String> downloadApk(
    String url, {
    required Function(DownloadProgress progress) onProgress,
    CancelToken? cancelToken,
  }) async {
    try {
      // 获取下载目录
      final dir = await getTemporaryDirectory();
      final savePath = '${dir.path}/app-update.apk';

      // 删除旧文件
      final file = File(savePath);
      if (await file.exists()) {
        await file.delete();
      }

      // 下载文件
      await _dio.download(
        url,
        savePath,
        onReceiveProgress: (received, total) {
          onProgress(DownloadProgress(
            received: received,
            total: total,
          ));
        },
        cancelToken: cancelToken,
        options: Options(
          receiveTimeout: const Duration(minutes: 10),
          sendTimeout: const Duration(minutes: 10),
        ),
      );

      return savePath;
    } catch (e) {
      throw Exception('下载失败: $e');
    }
  }

  /// 安装 APK
  Future<void> installApk(String filePath) async {
    try {
      final result = await OpenFile.open(filePath);

      if (result.type != ResultType.done) {
        throw Exception('打开安装器失败: ${result.message}');
      }
    } catch (e) {
      throw Exception('安装失败: $e');
    }
  }

  /// 获取版本列表
  Future<List<AppVersionInfo>> getVersionList({
    int limit = 10,
    int offset = 0,
  }) async {
    try {
      final response = await _dio.get(
        '${AppConfig.apiUrl}/app/version/list',
        queryParameters: {
          'limit': limit,
          'offset': offset,
        },
      );

      return (response.data as List)
          .map((item) => AppVersionInfo.fromJson(item))
          .toList();
    } catch (e) {
      throw Exception('获取版本列表失败: $e');
    }
  }

  /// 获取指定版本
  Future<AppVersionInfo> getVersion(int versionCode) async {
    try {
      final response = await _dio.get(
        '${AppConfig.apiUrl}/app/version/$versionCode',
      );

      return AppVersionInfo.fromJson(response.data);
    } catch (e) {
      throw Exception('获取版本信息失败: $e');
    }
  }
}
