// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'app_version.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

DownloadSource _$DownloadSourceFromJson(Map<String, dynamic> json) {
  return _DownloadSource.fromJson(json);
}

/// @nodoc
mixin _$DownloadSource {
  String get name => throw _privateConstructorUsedError;
  String get url => throw _privateConstructorUsedError;
  String get speed => throw _privateConstructorUsedError;

  /// Serializes this DownloadSource to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DownloadSource
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DownloadSourceCopyWith<DownloadSource> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DownloadSourceCopyWith<$Res> {
  factory $DownloadSourceCopyWith(
          DownloadSource value, $Res Function(DownloadSource) then) =
      _$DownloadSourceCopyWithImpl<$Res, DownloadSource>;
  @useResult
  $Res call({String name, String url, String speed});
}

/// @nodoc
class _$DownloadSourceCopyWithImpl<$Res, $Val extends DownloadSource>
    implements $DownloadSourceCopyWith<$Res> {
  _$DownloadSourceCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DownloadSource
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? url = null,
    Object? speed = null,
  }) {
    return _then(_value.copyWith(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      url: null == url
          ? _value.url
          : url // ignore: cast_nullable_to_non_nullable
              as String,
      speed: null == speed
          ? _value.speed
          : speed // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DownloadSourceImplCopyWith<$Res>
    implements $DownloadSourceCopyWith<$Res> {
  factory _$$DownloadSourceImplCopyWith(_$DownloadSourceImpl value,
          $Res Function(_$DownloadSourceImpl) then) =
      __$$DownloadSourceImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String name, String url, String speed});
}

/// @nodoc
class __$$DownloadSourceImplCopyWithImpl<$Res>
    extends _$DownloadSourceCopyWithImpl<$Res, _$DownloadSourceImpl>
    implements _$$DownloadSourceImplCopyWith<$Res> {
  __$$DownloadSourceImplCopyWithImpl(
      _$DownloadSourceImpl _value, $Res Function(_$DownloadSourceImpl) _then)
      : super(_value, _then);

  /// Create a copy of DownloadSource
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? url = null,
    Object? speed = null,
  }) {
    return _then(_$DownloadSourceImpl(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      url: null == url
          ? _value.url
          : url // ignore: cast_nullable_to_non_nullable
              as String,
      speed: null == speed
          ? _value.speed
          : speed // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DownloadSourceImpl implements _DownloadSource {
  const _$DownloadSourceImpl(
      {required this.name, required this.url, this.speed = 'medium'});

  factory _$DownloadSourceImpl.fromJson(Map<String, dynamic> json) =>
      _$$DownloadSourceImplFromJson(json);

  @override
  final String name;
  @override
  final String url;
  @override
  @JsonKey()
  final String speed;

  @override
  String toString() {
    return 'DownloadSource(name: $name, url: $url, speed: $speed)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DownloadSourceImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.url, url) || other.url == url) &&
            (identical(other.speed, speed) || other.speed == speed));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, name, url, speed);

  /// Create a copy of DownloadSource
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DownloadSourceImplCopyWith<_$DownloadSourceImpl> get copyWith =>
      __$$DownloadSourceImplCopyWithImpl<_$DownloadSourceImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DownloadSourceImplToJson(
      this,
    );
  }
}

abstract class _DownloadSource implements DownloadSource {
  const factory _DownloadSource(
      {required final String name,
      required final String url,
      final String speed}) = _$DownloadSourceImpl;

  factory _DownloadSource.fromJson(Map<String, dynamic> json) =
      _$DownloadSourceImpl.fromJson;

  @override
  String get name;
  @override
  String get url;
  @override
  String get speed;

  /// Create a copy of DownloadSource
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DownloadSourceImplCopyWith<_$DownloadSourceImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

AppVersionInfo _$AppVersionInfoFromJson(Map<String, dynamic> json) {
  return _AppVersionInfo.fromJson(json);
}

/// @nodoc
mixin _$AppVersionInfo {
  @JsonKey(name: 'version_code')
  int get versionCode => throw _privateConstructorUsedError;
  @JsonKey(name: 'version_name')
  String get versionName => throw _privateConstructorUsedError;
  @JsonKey(name: 'apk_url')
  String get apkUrl => throw _privateConstructorUsedError;
  @JsonKey(name: 'apk_size')
  int get apkSize => throw _privateConstructorUsedError;
  @JsonKey(name: 'apk_md5')
  String? get apkMd5 => throw _privateConstructorUsedError;
  @JsonKey(name: 'release_notes')
  String get releaseNotes => throw _privateConstructorUsedError;
  @JsonKey(name: 'force_update')
  bool get forceUpdate => throw _privateConstructorUsedError;
  @JsonKey(name: 'download_sources')
  List<DownloadSource> get downloadSources =>
      throw _privateConstructorUsedError;
  @JsonKey(name: 'published_at')
  DateTime? get publishedAt => throw _privateConstructorUsedError;

  /// Serializes this AppVersionInfo to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AppVersionInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AppVersionInfoCopyWith<AppVersionInfo> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AppVersionInfoCopyWith<$Res> {
  factory $AppVersionInfoCopyWith(
          AppVersionInfo value, $Res Function(AppVersionInfo) then) =
      _$AppVersionInfoCopyWithImpl<$Res, AppVersionInfo>;
  @useResult
  $Res call(
      {@JsonKey(name: 'version_code') int versionCode,
      @JsonKey(name: 'version_name') String versionName,
      @JsonKey(name: 'apk_url') String apkUrl,
      @JsonKey(name: 'apk_size') int apkSize,
      @JsonKey(name: 'apk_md5') String? apkMd5,
      @JsonKey(name: 'release_notes') String releaseNotes,
      @JsonKey(name: 'force_update') bool forceUpdate,
      @JsonKey(name: 'download_sources') List<DownloadSource> downloadSources,
      @JsonKey(name: 'published_at') DateTime? publishedAt});
}

/// @nodoc
class _$AppVersionInfoCopyWithImpl<$Res, $Val extends AppVersionInfo>
    implements $AppVersionInfoCopyWith<$Res> {
  _$AppVersionInfoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AppVersionInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? versionCode = null,
    Object? versionName = null,
    Object? apkUrl = null,
    Object? apkSize = null,
    Object? apkMd5 = freezed,
    Object? releaseNotes = null,
    Object? forceUpdate = null,
    Object? downloadSources = null,
    Object? publishedAt = freezed,
  }) {
    return _then(_value.copyWith(
      versionCode: null == versionCode
          ? _value.versionCode
          : versionCode // ignore: cast_nullable_to_non_nullable
              as int,
      versionName: null == versionName
          ? _value.versionName
          : versionName // ignore: cast_nullable_to_non_nullable
              as String,
      apkUrl: null == apkUrl
          ? _value.apkUrl
          : apkUrl // ignore: cast_nullable_to_non_nullable
              as String,
      apkSize: null == apkSize
          ? _value.apkSize
          : apkSize // ignore: cast_nullable_to_non_nullable
              as int,
      apkMd5: freezed == apkMd5
          ? _value.apkMd5
          : apkMd5 // ignore: cast_nullable_to_non_nullable
              as String?,
      releaseNotes: null == releaseNotes
          ? _value.releaseNotes
          : releaseNotes // ignore: cast_nullable_to_non_nullable
              as String,
      forceUpdate: null == forceUpdate
          ? _value.forceUpdate
          : forceUpdate // ignore: cast_nullable_to_non_nullable
              as bool,
      downloadSources: null == downloadSources
          ? _value.downloadSources
          : downloadSources // ignore: cast_nullable_to_non_nullable
              as List<DownloadSource>,
      publishedAt: freezed == publishedAt
          ? _value.publishedAt
          : publishedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AppVersionInfoImplCopyWith<$Res>
    implements $AppVersionInfoCopyWith<$Res> {
  factory _$$AppVersionInfoImplCopyWith(_$AppVersionInfoImpl value,
          $Res Function(_$AppVersionInfoImpl) then) =
      __$$AppVersionInfoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'version_code') int versionCode,
      @JsonKey(name: 'version_name') String versionName,
      @JsonKey(name: 'apk_url') String apkUrl,
      @JsonKey(name: 'apk_size') int apkSize,
      @JsonKey(name: 'apk_md5') String? apkMd5,
      @JsonKey(name: 'release_notes') String releaseNotes,
      @JsonKey(name: 'force_update') bool forceUpdate,
      @JsonKey(name: 'download_sources') List<DownloadSource> downloadSources,
      @JsonKey(name: 'published_at') DateTime? publishedAt});
}

/// @nodoc
class __$$AppVersionInfoImplCopyWithImpl<$Res>
    extends _$AppVersionInfoCopyWithImpl<$Res, _$AppVersionInfoImpl>
    implements _$$AppVersionInfoImplCopyWith<$Res> {
  __$$AppVersionInfoImplCopyWithImpl(
      _$AppVersionInfoImpl _value, $Res Function(_$AppVersionInfoImpl) _then)
      : super(_value, _then);

  /// Create a copy of AppVersionInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? versionCode = null,
    Object? versionName = null,
    Object? apkUrl = null,
    Object? apkSize = null,
    Object? apkMd5 = freezed,
    Object? releaseNotes = null,
    Object? forceUpdate = null,
    Object? downloadSources = null,
    Object? publishedAt = freezed,
  }) {
    return _then(_$AppVersionInfoImpl(
      versionCode: null == versionCode
          ? _value.versionCode
          : versionCode // ignore: cast_nullable_to_non_nullable
              as int,
      versionName: null == versionName
          ? _value.versionName
          : versionName // ignore: cast_nullable_to_non_nullable
              as String,
      apkUrl: null == apkUrl
          ? _value.apkUrl
          : apkUrl // ignore: cast_nullable_to_non_nullable
              as String,
      apkSize: null == apkSize
          ? _value.apkSize
          : apkSize // ignore: cast_nullable_to_non_nullable
              as int,
      apkMd5: freezed == apkMd5
          ? _value.apkMd5
          : apkMd5 // ignore: cast_nullable_to_non_nullable
              as String?,
      releaseNotes: null == releaseNotes
          ? _value.releaseNotes
          : releaseNotes // ignore: cast_nullable_to_non_nullable
              as String,
      forceUpdate: null == forceUpdate
          ? _value.forceUpdate
          : forceUpdate // ignore: cast_nullable_to_non_nullable
              as bool,
      downloadSources: null == downloadSources
          ? _value._downloadSources
          : downloadSources // ignore: cast_nullable_to_non_nullable
              as List<DownloadSource>,
      publishedAt: freezed == publishedAt
          ? _value.publishedAt
          : publishedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AppVersionInfoImpl implements _AppVersionInfo {
  const _$AppVersionInfoImpl(
      {@JsonKey(name: 'version_code') required this.versionCode,
      @JsonKey(name: 'version_name') required this.versionName,
      @JsonKey(name: 'apk_url') required this.apkUrl,
      @JsonKey(name: 'apk_size') required this.apkSize,
      @JsonKey(name: 'apk_md5') this.apkMd5,
      @JsonKey(name: 'release_notes') required this.releaseNotes,
      @JsonKey(name: 'force_update') this.forceUpdate = false,
      @JsonKey(name: 'download_sources')
      final List<DownloadSource> downloadSources = const [],
      @JsonKey(name: 'published_at') this.publishedAt})
      : _downloadSources = downloadSources;

  factory _$AppVersionInfoImpl.fromJson(Map<String, dynamic> json) =>
      _$$AppVersionInfoImplFromJson(json);

  @override
  @JsonKey(name: 'version_code')
  final int versionCode;
  @override
  @JsonKey(name: 'version_name')
  final String versionName;
  @override
  @JsonKey(name: 'apk_url')
  final String apkUrl;
  @override
  @JsonKey(name: 'apk_size')
  final int apkSize;
  @override
  @JsonKey(name: 'apk_md5')
  final String? apkMd5;
  @override
  @JsonKey(name: 'release_notes')
  final String releaseNotes;
  @override
  @JsonKey(name: 'force_update')
  final bool forceUpdate;
  final List<DownloadSource> _downloadSources;
  @override
  @JsonKey(name: 'download_sources')
  List<DownloadSource> get downloadSources {
    if (_downloadSources is EqualUnmodifiableListView) return _downloadSources;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_downloadSources);
  }

  @override
  @JsonKey(name: 'published_at')
  final DateTime? publishedAt;

  @override
  String toString() {
    return 'AppVersionInfo(versionCode: $versionCode, versionName: $versionName, apkUrl: $apkUrl, apkSize: $apkSize, apkMd5: $apkMd5, releaseNotes: $releaseNotes, forceUpdate: $forceUpdate, downloadSources: $downloadSources, publishedAt: $publishedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AppVersionInfoImpl &&
            (identical(other.versionCode, versionCode) ||
                other.versionCode == versionCode) &&
            (identical(other.versionName, versionName) ||
                other.versionName == versionName) &&
            (identical(other.apkUrl, apkUrl) || other.apkUrl == apkUrl) &&
            (identical(other.apkSize, apkSize) || other.apkSize == apkSize) &&
            (identical(other.apkMd5, apkMd5) || other.apkMd5 == apkMd5) &&
            (identical(other.releaseNotes, releaseNotes) ||
                other.releaseNotes == releaseNotes) &&
            (identical(other.forceUpdate, forceUpdate) ||
                other.forceUpdate == forceUpdate) &&
            const DeepCollectionEquality()
                .equals(other._downloadSources, _downloadSources) &&
            (identical(other.publishedAt, publishedAt) ||
                other.publishedAt == publishedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      versionCode,
      versionName,
      apkUrl,
      apkSize,
      apkMd5,
      releaseNotes,
      forceUpdate,
      const DeepCollectionEquality().hash(_downloadSources),
      publishedAt);

  /// Create a copy of AppVersionInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AppVersionInfoImplCopyWith<_$AppVersionInfoImpl> get copyWith =>
      __$$AppVersionInfoImplCopyWithImpl<_$AppVersionInfoImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AppVersionInfoImplToJson(
      this,
    );
  }
}

abstract class _AppVersionInfo implements AppVersionInfo {
  const factory _AppVersionInfo(
          {@JsonKey(name: 'version_code') required final int versionCode,
          @JsonKey(name: 'version_name') required final String versionName,
          @JsonKey(name: 'apk_url') required final String apkUrl,
          @JsonKey(name: 'apk_size') required final int apkSize,
          @JsonKey(name: 'apk_md5') final String? apkMd5,
          @JsonKey(name: 'release_notes') required final String releaseNotes,
          @JsonKey(name: 'force_update') final bool forceUpdate,
          @JsonKey(name: 'download_sources')
          final List<DownloadSource> downloadSources,
          @JsonKey(name: 'published_at') final DateTime? publishedAt}) =
      _$AppVersionInfoImpl;

  factory _AppVersionInfo.fromJson(Map<String, dynamic> json) =
      _$AppVersionInfoImpl.fromJson;

  @override
  @JsonKey(name: 'version_code')
  int get versionCode;
  @override
  @JsonKey(name: 'version_name')
  String get versionName;
  @override
  @JsonKey(name: 'apk_url')
  String get apkUrl;
  @override
  @JsonKey(name: 'apk_size')
  int get apkSize;
  @override
  @JsonKey(name: 'apk_md5')
  String? get apkMd5;
  @override
  @JsonKey(name: 'release_notes')
  String get releaseNotes;
  @override
  @JsonKey(name: 'force_update')
  bool get forceUpdate;
  @override
  @JsonKey(name: 'download_sources')
  List<DownloadSource> get downloadSources;
  @override
  @JsonKey(name: 'published_at')
  DateTime? get publishedAt;

  /// Create a copy of AppVersionInfo
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AppVersionInfoImplCopyWith<_$AppVersionInfoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CheckUpdateResponse _$CheckUpdateResponseFromJson(Map<String, dynamic> json) {
  return _CheckUpdateResponse.fromJson(json);
}

/// @nodoc
mixin _$CheckUpdateResponse {
  @JsonKey(name: 'has_update')
  bool get hasUpdate => throw _privateConstructorUsedError;
  @JsonKey(name: 'latest_version')
  AppVersionInfo? get latestVersion => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;

  /// Serializes this CheckUpdateResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CheckUpdateResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CheckUpdateResponseCopyWith<CheckUpdateResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CheckUpdateResponseCopyWith<$Res> {
  factory $CheckUpdateResponseCopyWith(
          CheckUpdateResponse value, $Res Function(CheckUpdateResponse) then) =
      _$CheckUpdateResponseCopyWithImpl<$Res, CheckUpdateResponse>;
  @useResult
  $Res call(
      {@JsonKey(name: 'has_update') bool hasUpdate,
      @JsonKey(name: 'latest_version') AppVersionInfo? latestVersion,
      String message});

  $AppVersionInfoCopyWith<$Res>? get latestVersion;
}

/// @nodoc
class _$CheckUpdateResponseCopyWithImpl<$Res, $Val extends CheckUpdateResponse>
    implements $CheckUpdateResponseCopyWith<$Res> {
  _$CheckUpdateResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CheckUpdateResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? hasUpdate = null,
    Object? latestVersion = freezed,
    Object? message = null,
  }) {
    return _then(_value.copyWith(
      hasUpdate: null == hasUpdate
          ? _value.hasUpdate
          : hasUpdate // ignore: cast_nullable_to_non_nullable
              as bool,
      latestVersion: freezed == latestVersion
          ? _value.latestVersion
          : latestVersion // ignore: cast_nullable_to_non_nullable
              as AppVersionInfo?,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }

  /// Create a copy of CheckUpdateResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $AppVersionInfoCopyWith<$Res>? get latestVersion {
    if (_value.latestVersion == null) {
      return null;
    }

    return $AppVersionInfoCopyWith<$Res>(_value.latestVersion!, (value) {
      return _then(_value.copyWith(latestVersion: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$CheckUpdateResponseImplCopyWith<$Res>
    implements $CheckUpdateResponseCopyWith<$Res> {
  factory _$$CheckUpdateResponseImplCopyWith(_$CheckUpdateResponseImpl value,
          $Res Function(_$CheckUpdateResponseImpl) then) =
      __$$CheckUpdateResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'has_update') bool hasUpdate,
      @JsonKey(name: 'latest_version') AppVersionInfo? latestVersion,
      String message});

  @override
  $AppVersionInfoCopyWith<$Res>? get latestVersion;
}

/// @nodoc
class __$$CheckUpdateResponseImplCopyWithImpl<$Res>
    extends _$CheckUpdateResponseCopyWithImpl<$Res, _$CheckUpdateResponseImpl>
    implements _$$CheckUpdateResponseImplCopyWith<$Res> {
  __$$CheckUpdateResponseImplCopyWithImpl(_$CheckUpdateResponseImpl _value,
      $Res Function(_$CheckUpdateResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of CheckUpdateResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? hasUpdate = null,
    Object? latestVersion = freezed,
    Object? message = null,
  }) {
    return _then(_$CheckUpdateResponseImpl(
      hasUpdate: null == hasUpdate
          ? _value.hasUpdate
          : hasUpdate // ignore: cast_nullable_to_non_nullable
              as bool,
      latestVersion: freezed == latestVersion
          ? _value.latestVersion
          : latestVersion // ignore: cast_nullable_to_non_nullable
              as AppVersionInfo?,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CheckUpdateResponseImpl implements _CheckUpdateResponse {
  const _$CheckUpdateResponseImpl(
      {@JsonKey(name: 'has_update') required this.hasUpdate,
      @JsonKey(name: 'latest_version') this.latestVersion,
      required this.message});

  factory _$CheckUpdateResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$CheckUpdateResponseImplFromJson(json);

  @override
  @JsonKey(name: 'has_update')
  final bool hasUpdate;
  @override
  @JsonKey(name: 'latest_version')
  final AppVersionInfo? latestVersion;
  @override
  final String message;

  @override
  String toString() {
    return 'CheckUpdateResponse(hasUpdate: $hasUpdate, latestVersion: $latestVersion, message: $message)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CheckUpdateResponseImpl &&
            (identical(other.hasUpdate, hasUpdate) ||
                other.hasUpdate == hasUpdate) &&
            (identical(other.latestVersion, latestVersion) ||
                other.latestVersion == latestVersion) &&
            (identical(other.message, message) || other.message == message));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, hasUpdate, latestVersion, message);

  /// Create a copy of CheckUpdateResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CheckUpdateResponseImplCopyWith<_$CheckUpdateResponseImpl> get copyWith =>
      __$$CheckUpdateResponseImplCopyWithImpl<_$CheckUpdateResponseImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CheckUpdateResponseImplToJson(
      this,
    );
  }
}

abstract class _CheckUpdateResponse implements CheckUpdateResponse {
  const factory _CheckUpdateResponse(
      {@JsonKey(name: 'has_update') required final bool hasUpdate,
      @JsonKey(name: 'latest_version') final AppVersionInfo? latestVersion,
      required final String message}) = _$CheckUpdateResponseImpl;

  factory _CheckUpdateResponse.fromJson(Map<String, dynamic> json) =
      _$CheckUpdateResponseImpl.fromJson;

  @override
  @JsonKey(name: 'has_update')
  bool get hasUpdate;
  @override
  @JsonKey(name: 'latest_version')
  AppVersionInfo? get latestVersion;
  @override
  String get message;

  /// Create a copy of CheckUpdateResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CheckUpdateResponseImplCopyWith<_$CheckUpdateResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$DownloadProgress {
  int get received => throw _privateConstructorUsedError;
  int get total => throw _privateConstructorUsedError;

  /// Create a copy of DownloadProgress
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DownloadProgressCopyWith<DownloadProgress> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DownloadProgressCopyWith<$Res> {
  factory $DownloadProgressCopyWith(
          DownloadProgress value, $Res Function(DownloadProgress) then) =
      _$DownloadProgressCopyWithImpl<$Res, DownloadProgress>;
  @useResult
  $Res call({int received, int total});
}

/// @nodoc
class _$DownloadProgressCopyWithImpl<$Res, $Val extends DownloadProgress>
    implements $DownloadProgressCopyWith<$Res> {
  _$DownloadProgressCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DownloadProgress
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? received = null,
    Object? total = null,
  }) {
    return _then(_value.copyWith(
      received: null == received
          ? _value.received
          : received // ignore: cast_nullable_to_non_nullable
              as int,
      total: null == total
          ? _value.total
          : total // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DownloadProgressImplCopyWith<$Res>
    implements $DownloadProgressCopyWith<$Res> {
  factory _$$DownloadProgressImplCopyWith(_$DownloadProgressImpl value,
          $Res Function(_$DownloadProgressImpl) then) =
      __$$DownloadProgressImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({int received, int total});
}

/// @nodoc
class __$$DownloadProgressImplCopyWithImpl<$Res>
    extends _$DownloadProgressCopyWithImpl<$Res, _$DownloadProgressImpl>
    implements _$$DownloadProgressImplCopyWith<$Res> {
  __$$DownloadProgressImplCopyWithImpl(_$DownloadProgressImpl _value,
      $Res Function(_$DownloadProgressImpl) _then)
      : super(_value, _then);

  /// Create a copy of DownloadProgress
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? received = null,
    Object? total = null,
  }) {
    return _then(_$DownloadProgressImpl(
      received: null == received
          ? _value.received
          : received // ignore: cast_nullable_to_non_nullable
              as int,
      total: null == total
          ? _value.total
          : total // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc

class _$DownloadProgressImpl extends _DownloadProgress {
  const _$DownloadProgressImpl({required this.received, required this.total})
      : super._();

  @override
  final int received;
  @override
  final int total;

  @override
  String toString() {
    return 'DownloadProgress(received: $received, total: $total)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DownloadProgressImpl &&
            (identical(other.received, received) ||
                other.received == received) &&
            (identical(other.total, total) || other.total == total));
  }

  @override
  int get hashCode => Object.hash(runtimeType, received, total);

  /// Create a copy of DownloadProgress
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DownloadProgressImplCopyWith<_$DownloadProgressImpl> get copyWith =>
      __$$DownloadProgressImplCopyWithImpl<_$DownloadProgressImpl>(
          this, _$identity);
}

abstract class _DownloadProgress extends DownloadProgress {
  const factory _DownloadProgress(
      {required final int received,
      required final int total}) = _$DownloadProgressImpl;
  const _DownloadProgress._() : super._();

  @override
  int get received;
  @override
  int get total;

  /// Create a copy of DownloadProgress
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DownloadProgressImplCopyWith<_$DownloadProgressImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
