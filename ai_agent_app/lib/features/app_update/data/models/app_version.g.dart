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
      versionCode: (json['versionCode'] as num).toInt(),
      versionName: json['versionName'] as String,
      apkUrl: json['apkUrl'] as String,
      apkSize: (json['apkSize'] as num).toInt(),
      apkMd5: json['apkMd5'] as String?,
      releaseNotes: json['releaseNotes'] as String,
      forceUpdate: json['forceUpdate'] as bool? ?? false,
      downloadSources: (json['downloadSources'] as List<dynamic>?)
              ?.map((e) => DownloadSource.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      publishedAt: json['publishedAt'] == null
          ? null
          : DateTime.parse(json['publishedAt'] as String),
    );

Map<String, dynamic> _$$AppVersionInfoImplToJson(
        _$AppVersionInfoImpl instance) =>
    <String, dynamic>{
      'versionCode': instance.versionCode,
      'versionName': instance.versionName,
      'apkUrl': instance.apkUrl,
      'apkSize': instance.apkSize,
      'apkMd5': instance.apkMd5,
      'releaseNotes': instance.releaseNotes,
      'forceUpdate': instance.forceUpdate,
      'downloadSources': instance.downloadSources,
      'publishedAt': instance.publishedAt?.toIso8601String(),
    };

_$CheckUpdateResponseImpl _$$CheckUpdateResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$CheckUpdateResponseImpl(
      hasUpdate: json['hasUpdate'] as bool,
      latestVersion: json['latestVersion'] == null
          ? null
          : AppVersionInfo.fromJson(
              json['latestVersion'] as Map<String, dynamic>),
      message: json['message'] as String,
    );

Map<String, dynamic> _$$CheckUpdateResponseImplToJson(
        _$CheckUpdateResponseImpl instance) =>
    <String, dynamic>{
      'hasUpdate': instance.hasUpdate,
      'latestVersion': instance.latestVersion,
      'message': instance.message,
    };
