// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_version.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$DownloadSourceImpl _$$DownloadSourceImplFromJson(Map<String, dynamic> json) =>
    _$DownloadSourceImpl(
      name: json['name'] as String,
      url: json['url'] as String,
      speed: json['speed'] as String? ?? 'medium',
    );

Map<String, dynamic> _$$DownloadSourceImplToJson(
        _$DownloadSourceImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'url': instance.url,
      'speed': instance.speed,
    };

_$AppVersionInfoImpl _$$AppVersionInfoImplFromJson(Map<String, dynamic> json) =>
    _$AppVersionInfoImpl(
      versionCode: (json['version_code'] as num).toInt(),
      versionName: json['version_name'] as String,
      apkUrl: json['apk_url'] as String,
      apkSize: (json['apk_size'] as num).toInt(),
      apkMd5: json['apk_md5'] as String?,
      releaseNotes: json['release_notes'] as String,
      forceUpdate: json['force_update'] as bool? ?? false,
      downloadSources: (json['download_sources'] as List<dynamic>?)
              ?.map((e) => DownloadSource.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      publishedAt: json['published_at'] == null
          ? null
          : DateTime.parse(json['published_at'] as String),
    );

Map<String, dynamic> _$$AppVersionInfoImplToJson(
        _$AppVersionInfoImpl instance) =>
    <String, dynamic>{
      'version_code': instance.versionCode,
      'version_name': instance.versionName,
      'apk_url': instance.apkUrl,
      'apk_size': instance.apkSize,
      'apk_md5': instance.apkMd5,
      'release_notes': instance.releaseNotes,
      'force_update': instance.forceUpdate,
      'download_sources': instance.downloadSources,
      'published_at': instance.publishedAt?.toIso8601String(),
    };

_$CheckUpdateResponseImpl _$$CheckUpdateResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$CheckUpdateResponseImpl(
      hasUpdate: json['has_update'] as bool,
      latestVersion: json['latest_version'] == null
          ? null
          : AppVersionInfo.fromJson(
              json['latest_version'] as Map<String, dynamic>),
      message: json['message'] as String,
    );

Map<String, dynamic> _$$CheckUpdateResponseImplToJson(
        _$CheckUpdateResponseImpl instance) =>
    <String, dynamic>{
      'has_update': instance.hasUpdate,
      'latest_version': instance.latestVersion,
      'message': instance.message,
    };
