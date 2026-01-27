import 'package:freezed_annotation/freezed_annotation.dart';

part 'app_version.freezed.dart';
part 'app_version.g.dart';

/// 下载源
@freezed
class DownloadSource with _$DownloadSource {
  const factory DownloadSource({
    required String name,
    required String url,
    @Default('medium') String speed,
  }) = _DownloadSource;

  factory DownloadSource.fromJson(Map<String, dynamic> json) =>
      _$DownloadSourceFromJson(json);
}

/// 应用版本信息
@freezed
class AppVersionInfo with _$AppVersionInfo {
  const factory AppVersionInfo({
    @JsonKey(name: 'version_code') required int versionCode,
    @JsonKey(name: 'version_name') required String versionName,
    @JsonKey(name: 'apk_url') required String apkUrl,
    @JsonKey(name: 'apk_size') required int apkSize,
    @JsonKey(name: 'apk_md5') String? apkMd5,
    @JsonKey(name: 'release_notes') required String releaseNotes,
    @JsonKey(name: 'force_update') @Default(false) bool forceUpdate,
    @JsonKey(name: 'download_sources') @Default([]) List<DownloadSource> downloadSources,
    @JsonKey(name: 'published_at') DateTime? publishedAt,
  }) = _AppVersionInfo;

  factory AppVersionInfo.fromJson(Map<String, dynamic> json) =>
      _$AppVersionInfoFromJson(json);
}

/// 检查更新响应
@freezed
class CheckUpdateResponse with _$CheckUpdateResponse {
  const factory CheckUpdateResponse({
    @JsonKey(name: 'has_update') required bool hasUpdate,
    @JsonKey(name: 'latest_version') AppVersionInfo? latestVersion,
    required String message,
  }) = _CheckUpdateResponse;

  factory CheckUpdateResponse.fromJson(Map<String, dynamic> json) =>
      _$CheckUpdateResponseFromJson(json);
}

/// 下载进度
@freezed
class DownloadProgress with _$DownloadProgress {
  const factory DownloadProgress({
    required int received,
    required int total,
  }) = _DownloadProgress;

  const DownloadProgress._();

  /// 获取下载百分比 (0.0 ~ 1.0)
  double get percentage => total > 0 ? received / total : 0.0;

  /// 获取下载百分比文本 (0% ~ 100%)
  String get percentageText => '${(percentage * 100).toStringAsFixed(0)}%';

  /// 获取已下载大小（MB）
  double get receivedMB => received / 1024 / 1024;

  /// 获取总大小（MB）
  double get totalMB => total / 1024 / 1024;

  /// 获取下载进度文本
  String get progressText =>
      '${receivedMB.toStringAsFixed(1)}MB / ${totalMB.toStringAsFixed(1)}MB';
}
