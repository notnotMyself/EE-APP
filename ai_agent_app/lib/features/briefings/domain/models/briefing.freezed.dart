// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'briefing.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

BriefingAction _$BriefingActionFromJson(Map<String, dynamic> json) {
  return _BriefingAction.fromJson(json);
}

/// @nodoc
mixin _$BriefingAction {
  String get label => throw _privateConstructorUsedError;
  String get action => throw _privateConstructorUsedError;
  Map<String, dynamic>? get data => throw _privateConstructorUsedError;
  String? get prompt => throw _privateConstructorUsedError;

  /// Serializes this BriefingAction to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of BriefingAction
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $BriefingActionCopyWith<BriefingAction> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BriefingActionCopyWith<$Res> {
  factory $BriefingActionCopyWith(
          BriefingAction value, $Res Function(BriefingAction) then) =
      _$BriefingActionCopyWithImpl<$Res, BriefingAction>;
  @useResult
  $Res call(
      {String label,
      String action,
      Map<String, dynamic>? data,
      String? prompt});
}

/// @nodoc
class _$BriefingActionCopyWithImpl<$Res, $Val extends BriefingAction>
    implements $BriefingActionCopyWith<$Res> {
  _$BriefingActionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of BriefingAction
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? label = null,
    Object? action = null,
    Object? data = freezed,
    Object? prompt = freezed,
  }) {
    return _then(_value.copyWith(
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      action: null == action
          ? _value.action
          : action // ignore: cast_nullable_to_non_nullable
              as String,
      data: freezed == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      prompt: freezed == prompt
          ? _value.prompt
          : prompt // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$BriefingActionImplCopyWith<$Res>
    implements $BriefingActionCopyWith<$Res> {
  factory _$$BriefingActionImplCopyWith(_$BriefingActionImpl value,
          $Res Function(_$BriefingActionImpl) then) =
      __$$BriefingActionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String label,
      String action,
      Map<String, dynamic>? data,
      String? prompt});
}

/// @nodoc
class __$$BriefingActionImplCopyWithImpl<$Res>
    extends _$BriefingActionCopyWithImpl<$Res, _$BriefingActionImpl>
    implements _$$BriefingActionImplCopyWith<$Res> {
  __$$BriefingActionImplCopyWithImpl(
      _$BriefingActionImpl _value, $Res Function(_$BriefingActionImpl) _then)
      : super(_value, _then);

  /// Create a copy of BriefingAction
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? label = null,
    Object? action = null,
    Object? data = freezed,
    Object? prompt = freezed,
  }) {
    return _then(_$BriefingActionImpl(
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      action: null == action
          ? _value.action
          : action // ignore: cast_nullable_to_non_nullable
              as String,
      data: freezed == data
          ? _value._data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      prompt: freezed == prompt
          ? _value.prompt
          : prompt // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$BriefingActionImpl implements _BriefingAction {
  const _$BriefingActionImpl(
      {required this.label,
      required this.action,
      final Map<String, dynamic>? data,
      this.prompt})
      : _data = data;

  factory _$BriefingActionImpl.fromJson(Map<String, dynamic> json) =>
      _$$BriefingActionImplFromJson(json);

  @override
  final String label;
  @override
  final String action;
  final Map<String, dynamic>? _data;
  @override
  Map<String, dynamic>? get data {
    final value = _data;
    if (value == null) return null;
    if (_data is EqualUnmodifiableMapView) return _data;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final String? prompt;

  @override
  String toString() {
    return 'BriefingAction(label: $label, action: $action, data: $data, prompt: $prompt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$BriefingActionImpl &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.action, action) || other.action == action) &&
            const DeepCollectionEquality().equals(other._data, _data) &&
            (identical(other.prompt, prompt) || other.prompt == prompt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, label, action,
      const DeepCollectionEquality().hash(_data), prompt);

  /// Create a copy of BriefingAction
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$BriefingActionImplCopyWith<_$BriefingActionImpl> get copyWith =>
      __$$BriefingActionImplCopyWithImpl<_$BriefingActionImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$BriefingActionImplToJson(
      this,
    );
  }
}

abstract class _BriefingAction implements BriefingAction {
  const factory _BriefingAction(
      {required final String label,
      required final String action,
      final Map<String, dynamic>? data,
      final String? prompt}) = _$BriefingActionImpl;

  factory _BriefingAction.fromJson(Map<String, dynamic> json) =
      _$BriefingActionImpl.fromJson;

  @override
  String get label;
  @override
  String get action;
  @override
  Map<String, dynamic>? get data;
  @override
  String? get prompt;

  /// Create a copy of BriefingAction
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$BriefingActionImplCopyWith<_$BriefingActionImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

BriefingNewsItem _$BriefingNewsItemFromJson(Map<String, dynamic> json) {
  return _BriefingNewsItem.fromJson(json);
}

/// @nodoc
mixin _$BriefingNewsItem {
  int get index => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  @JsonKey(name: 'full_title')
  String? get fullTitle => throw _privateConstructorUsedError;
  String? get source => throw _privateConstructorUsedError;
  String? get category => throw _privateConstructorUsedError;
  String? get tag => throw _privateConstructorUsedError;
  String? get url => throw _privateConstructorUsedError;

  /// Serializes this BriefingNewsItem to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of BriefingNewsItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $BriefingNewsItemCopyWith<BriefingNewsItem> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BriefingNewsItemCopyWith<$Res> {
  factory $BriefingNewsItemCopyWith(
          BriefingNewsItem value, $Res Function(BriefingNewsItem) then) =
      _$BriefingNewsItemCopyWithImpl<$Res, BriefingNewsItem>;
  @useResult
  $Res call(
      {int index,
      String title,
      @JsonKey(name: 'full_title') String? fullTitle,
      String? source,
      String? category,
      String? tag,
      String? url});
}

/// @nodoc
class _$BriefingNewsItemCopyWithImpl<$Res, $Val extends BriefingNewsItem>
    implements $BriefingNewsItemCopyWith<$Res> {
  _$BriefingNewsItemCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of BriefingNewsItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? index = null,
    Object? title = null,
    Object? fullTitle = freezed,
    Object? source = freezed,
    Object? category = freezed,
    Object? tag = freezed,
    Object? url = freezed,
  }) {
    return _then(_value.copyWith(
      index: null == index
          ? _value.index
          : index // ignore: cast_nullable_to_non_nullable
              as int,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      fullTitle: freezed == fullTitle
          ? _value.fullTitle
          : fullTitle // ignore: cast_nullable_to_non_nullable
              as String?,
      source: freezed == source
          ? _value.source
          : source // ignore: cast_nullable_to_non_nullable
              as String?,
      category: freezed == category
          ? _value.category
          : category // ignore: cast_nullable_to_non_nullable
              as String?,
      tag: freezed == tag
          ? _value.tag
          : tag // ignore: cast_nullable_to_non_nullable
              as String?,
      url: freezed == url
          ? _value.url
          : url // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$BriefingNewsItemImplCopyWith<$Res>
    implements $BriefingNewsItemCopyWith<$Res> {
  factory _$$BriefingNewsItemImplCopyWith(_$BriefingNewsItemImpl value,
          $Res Function(_$BriefingNewsItemImpl) then) =
      __$$BriefingNewsItemImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int index,
      String title,
      @JsonKey(name: 'full_title') String? fullTitle,
      String? source,
      String? category,
      String? tag,
      String? url});
}

/// @nodoc
class __$$BriefingNewsItemImplCopyWithImpl<$Res>
    extends _$BriefingNewsItemCopyWithImpl<$Res, _$BriefingNewsItemImpl>
    implements _$$BriefingNewsItemImplCopyWith<$Res> {
  __$$BriefingNewsItemImplCopyWithImpl(_$BriefingNewsItemImpl _value,
      $Res Function(_$BriefingNewsItemImpl) _then)
      : super(_value, _then);

  /// Create a copy of BriefingNewsItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? index = null,
    Object? title = null,
    Object? fullTitle = freezed,
    Object? source = freezed,
    Object? category = freezed,
    Object? tag = freezed,
    Object? url = freezed,
  }) {
    return _then(_$BriefingNewsItemImpl(
      index: null == index
          ? _value.index
          : index // ignore: cast_nullable_to_non_nullable
              as int,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      fullTitle: freezed == fullTitle
          ? _value.fullTitle
          : fullTitle // ignore: cast_nullable_to_non_nullable
              as String?,
      source: freezed == source
          ? _value.source
          : source // ignore: cast_nullable_to_non_nullable
              as String?,
      category: freezed == category
          ? _value.category
          : category // ignore: cast_nullable_to_non_nullable
              as String?,
      tag: freezed == tag
          ? _value.tag
          : tag // ignore: cast_nullable_to_non_nullable
              as String?,
      url: freezed == url
          ? _value.url
          : url // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$BriefingNewsItemImpl implements _BriefingNewsItem {
  const _$BriefingNewsItemImpl(
      {required this.index,
      required this.title,
      @JsonKey(name: 'full_title') this.fullTitle,
      this.source,
      this.category,
      this.tag,
      this.url});

  factory _$BriefingNewsItemImpl.fromJson(Map<String, dynamic> json) =>
      _$$BriefingNewsItemImplFromJson(json);

  @override
  final int index;
  @override
  final String title;
  @override
  @JsonKey(name: 'full_title')
  final String? fullTitle;
  @override
  final String? source;
  @override
  final String? category;
  @override
  final String? tag;
  @override
  final String? url;

  @override
  String toString() {
    return 'BriefingNewsItem(index: $index, title: $title, fullTitle: $fullTitle, source: $source, category: $category, tag: $tag, url: $url)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$BriefingNewsItemImpl &&
            (identical(other.index, index) || other.index == index) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.fullTitle, fullTitle) ||
                other.fullTitle == fullTitle) &&
            (identical(other.source, source) || other.source == source) &&
            (identical(other.category, category) ||
                other.category == category) &&
            (identical(other.tag, tag) || other.tag == tag) &&
            (identical(other.url, url) || other.url == url));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, index, title, fullTitle, source, category, tag, url);

  /// Create a copy of BriefingNewsItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$BriefingNewsItemImplCopyWith<_$BriefingNewsItemImpl> get copyWith =>
      __$$BriefingNewsItemImplCopyWithImpl<_$BriefingNewsItemImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$BriefingNewsItemImplToJson(
      this,
    );
  }
}

abstract class _BriefingNewsItem implements BriefingNewsItem {
  const factory _BriefingNewsItem(
      {required final int index,
      required final String title,
      @JsonKey(name: 'full_title') final String? fullTitle,
      final String? source,
      final String? category,
      final String? tag,
      final String? url}) = _$BriefingNewsItemImpl;

  factory _BriefingNewsItem.fromJson(Map<String, dynamic> json) =
      _$BriefingNewsItemImpl.fromJson;

  @override
  int get index;
  @override
  String get title;
  @override
  @JsonKey(name: 'full_title')
  String? get fullTitle;
  @override
  String? get source;
  @override
  String? get category;
  @override
  String? get tag;
  @override
  String? get url;

  /// Create a copy of BriefingNewsItem
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$BriefingNewsItemImplCopyWith<_$BriefingNewsItemImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Briefing _$BriefingFromJson(Map<String, dynamic> json) {
  return _Briefing.fromJson(json);
}

/// @nodoc
mixin _$Briefing {
  String get id => throw _privateConstructorUsedError;
  @JsonKey(name: 'agent_id')
  String get agentId => throw _privateConstructorUsedError;
  @JsonKey(name: 'user_id')
  String get userId => throw _privateConstructorUsedError;
  @JsonKey(name: 'briefing_type')
  BriefingType get briefingType => throw _privateConstructorUsedError;
  BriefingPriority get priority => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String get summary => throw _privateConstructorUsedError;
  String? get impact => throw _privateConstructorUsedError;
  List<BriefingAction> get actions => throw _privateConstructorUsedError;
  @JsonKey(name: 'report_artifact_id')
  String? get reportArtifactId => throw _privateConstructorUsedError;
  @JsonKey(name: 'conversation_id')
  String? get conversationId => throw _privateConstructorUsedError;
  @JsonKey(name: 'context_data')
  Map<String, dynamic>? get contextData => throw _privateConstructorUsedError;
  BriefingStatus get status => throw _privateConstructorUsedError;
  @JsonKey(name: 'importance_score')
  double? get importanceScore => throw _privateConstructorUsedError;
  @JsonKey(name: 'read_at')
  DateTime? get readAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'actioned_at')
  DateTime? get actionedAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  DateTime get createdAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'expires_at')
  DateTime? get expiresAt => throw _privateConstructorUsedError; // 关联的Agent信息
  @JsonKey(name: 'agent_name')
  String? get agentName => throw _privateConstructorUsedError;
  @JsonKey(name: 'agent_avatar_url')
  String? get agentAvatarUrl => throw _privateConstructorUsedError;
  @JsonKey(name: 'agent_role')
  String? get agentRole =>
      throw _privateConstructorUsedError; // 结构化新闻列表（用于AI资讯类简报）
  @JsonKey(name: 'summary_structured')
  List<BriefingNewsItem> get summaryStructured =>
      throw _privateConstructorUsedError; // 封面样式提示（废弃字段，保留兼容性）
  @JsonKey(name: 'cover_style')
  @Deprecated('Use ui_schema instead')
  String? get coverStyle =>
      throw _privateConstructorUsedError; // A2UI 动态 UI Schema（新增）
  @JsonKey(name: 'ui_schema')
  Map<String, dynamic>? get uiSchema => throw _privateConstructorUsedError;
  @JsonKey(name: 'ui_schema_version')
  String? get uiSchemaVersion => throw _privateConstructorUsedError;

  /// Serializes this Briefing to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Briefing
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $BriefingCopyWith<Briefing> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BriefingCopyWith<$Res> {
  factory $BriefingCopyWith(Briefing value, $Res Function(Briefing) then) =
      _$BriefingCopyWithImpl<$Res, Briefing>;
  @useResult
  $Res call(
      {String id,
      @JsonKey(name: 'agent_id') String agentId,
      @JsonKey(name: 'user_id') String userId,
      @JsonKey(name: 'briefing_type') BriefingType briefingType,
      BriefingPriority priority,
      String title,
      String summary,
      String? impact,
      List<BriefingAction> actions,
      @JsonKey(name: 'report_artifact_id') String? reportArtifactId,
      @JsonKey(name: 'conversation_id') String? conversationId,
      @JsonKey(name: 'context_data') Map<String, dynamic>? contextData,
      BriefingStatus status,
      @JsonKey(name: 'importance_score') double? importanceScore,
      @JsonKey(name: 'read_at') DateTime? readAt,
      @JsonKey(name: 'actioned_at') DateTime? actionedAt,
      @JsonKey(name: 'created_at') DateTime createdAt,
      @JsonKey(name: 'expires_at') DateTime? expiresAt,
      @JsonKey(name: 'agent_name') String? agentName,
      @JsonKey(name: 'agent_avatar_url') String? agentAvatarUrl,
      @JsonKey(name: 'agent_role') String? agentRole,
      @JsonKey(name: 'summary_structured')
      List<BriefingNewsItem> summaryStructured,
      @JsonKey(name: 'cover_style')
      @Deprecated('Use ui_schema instead')
      String? coverStyle,
      @JsonKey(name: 'ui_schema') Map<String, dynamic>? uiSchema,
      @JsonKey(name: 'ui_schema_version') String? uiSchemaVersion});
}

/// @nodoc
class _$BriefingCopyWithImpl<$Res, $Val extends Briefing>
    implements $BriefingCopyWith<$Res> {
  _$BriefingCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Briefing
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? agentId = null,
    Object? userId = null,
    Object? briefingType = null,
    Object? priority = null,
    Object? title = null,
    Object? summary = null,
    Object? impact = freezed,
    Object? actions = null,
    Object? reportArtifactId = freezed,
    Object? conversationId = freezed,
    Object? contextData = freezed,
    Object? status = null,
    Object? importanceScore = freezed,
    Object? readAt = freezed,
    Object? actionedAt = freezed,
    Object? createdAt = null,
    Object? expiresAt = freezed,
    Object? agentName = freezed,
    Object? agentAvatarUrl = freezed,
    Object? agentRole = freezed,
    Object? summaryStructured = null,
    Object? coverStyle = freezed,
    Object? uiSchema = freezed,
    Object? uiSchemaVersion = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      agentId: null == agentId
          ? _value.agentId
          : agentId // ignore: cast_nullable_to_non_nullable
              as String,
      userId: null == userId
          ? _value.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String,
      briefingType: null == briefingType
          ? _value.briefingType
          : briefingType // ignore: cast_nullable_to_non_nullable
              as BriefingType,
      priority: null == priority
          ? _value.priority
          : priority // ignore: cast_nullable_to_non_nullable
              as BriefingPriority,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      summary: null == summary
          ? _value.summary
          : summary // ignore: cast_nullable_to_non_nullable
              as String,
      impact: freezed == impact
          ? _value.impact
          : impact // ignore: cast_nullable_to_non_nullable
              as String?,
      actions: null == actions
          ? _value.actions
          : actions // ignore: cast_nullable_to_non_nullable
              as List<BriefingAction>,
      reportArtifactId: freezed == reportArtifactId
          ? _value.reportArtifactId
          : reportArtifactId // ignore: cast_nullable_to_non_nullable
              as String?,
      conversationId: freezed == conversationId
          ? _value.conversationId
          : conversationId // ignore: cast_nullable_to_non_nullable
              as String?,
      contextData: freezed == contextData
          ? _value.contextData
          : contextData // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as BriefingStatus,
      importanceScore: freezed == importanceScore
          ? _value.importanceScore
          : importanceScore // ignore: cast_nullable_to_non_nullable
              as double?,
      readAt: freezed == readAt
          ? _value.readAt
          : readAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      actionedAt: freezed == actionedAt
          ? _value.actionedAt
          : actionedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      expiresAt: freezed == expiresAt
          ? _value.expiresAt
          : expiresAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      agentName: freezed == agentName
          ? _value.agentName
          : agentName // ignore: cast_nullable_to_non_nullable
              as String?,
      agentAvatarUrl: freezed == agentAvatarUrl
          ? _value.agentAvatarUrl
          : agentAvatarUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      agentRole: freezed == agentRole
          ? _value.agentRole
          : agentRole // ignore: cast_nullable_to_non_nullable
              as String?,
      summaryStructured: null == summaryStructured
          ? _value.summaryStructured
          : summaryStructured // ignore: cast_nullable_to_non_nullable
              as List<BriefingNewsItem>,
      coverStyle: freezed == coverStyle
          ? _value.coverStyle
          : coverStyle // ignore: cast_nullable_to_non_nullable
              as String?,
      uiSchema: freezed == uiSchema
          ? _value.uiSchema
          : uiSchema // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      uiSchemaVersion: freezed == uiSchemaVersion
          ? _value.uiSchemaVersion
          : uiSchemaVersion // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$BriefingImplCopyWith<$Res>
    implements $BriefingCopyWith<$Res> {
  factory _$$BriefingImplCopyWith(
          _$BriefingImpl value, $Res Function(_$BriefingImpl) then) =
      __$$BriefingImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      @JsonKey(name: 'agent_id') String agentId,
      @JsonKey(name: 'user_id') String userId,
      @JsonKey(name: 'briefing_type') BriefingType briefingType,
      BriefingPriority priority,
      String title,
      String summary,
      String? impact,
      List<BriefingAction> actions,
      @JsonKey(name: 'report_artifact_id') String? reportArtifactId,
      @JsonKey(name: 'conversation_id') String? conversationId,
      @JsonKey(name: 'context_data') Map<String, dynamic>? contextData,
      BriefingStatus status,
      @JsonKey(name: 'importance_score') double? importanceScore,
      @JsonKey(name: 'read_at') DateTime? readAt,
      @JsonKey(name: 'actioned_at') DateTime? actionedAt,
      @JsonKey(name: 'created_at') DateTime createdAt,
      @JsonKey(name: 'expires_at') DateTime? expiresAt,
      @JsonKey(name: 'agent_name') String? agentName,
      @JsonKey(name: 'agent_avatar_url') String? agentAvatarUrl,
      @JsonKey(name: 'agent_role') String? agentRole,
      @JsonKey(name: 'summary_structured')
      List<BriefingNewsItem> summaryStructured,
      @JsonKey(name: 'cover_style')
      @Deprecated('Use ui_schema instead')
      String? coverStyle,
      @JsonKey(name: 'ui_schema') Map<String, dynamic>? uiSchema,
      @JsonKey(name: 'ui_schema_version') String? uiSchemaVersion});
}

/// @nodoc
class __$$BriefingImplCopyWithImpl<$Res>
    extends _$BriefingCopyWithImpl<$Res, _$BriefingImpl>
    implements _$$BriefingImplCopyWith<$Res> {
  __$$BriefingImplCopyWithImpl(
      _$BriefingImpl _value, $Res Function(_$BriefingImpl) _then)
      : super(_value, _then);

  /// Create a copy of Briefing
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? agentId = null,
    Object? userId = null,
    Object? briefingType = null,
    Object? priority = null,
    Object? title = null,
    Object? summary = null,
    Object? impact = freezed,
    Object? actions = null,
    Object? reportArtifactId = freezed,
    Object? conversationId = freezed,
    Object? contextData = freezed,
    Object? status = null,
    Object? importanceScore = freezed,
    Object? readAt = freezed,
    Object? actionedAt = freezed,
    Object? createdAt = null,
    Object? expiresAt = freezed,
    Object? agentName = freezed,
    Object? agentAvatarUrl = freezed,
    Object? agentRole = freezed,
    Object? summaryStructured = null,
    Object? coverStyle = freezed,
    Object? uiSchema = freezed,
    Object? uiSchemaVersion = freezed,
  }) {
    return _then(_$BriefingImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      agentId: null == agentId
          ? _value.agentId
          : agentId // ignore: cast_nullable_to_non_nullable
              as String,
      userId: null == userId
          ? _value.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String,
      briefingType: null == briefingType
          ? _value.briefingType
          : briefingType // ignore: cast_nullable_to_non_nullable
              as BriefingType,
      priority: null == priority
          ? _value.priority
          : priority // ignore: cast_nullable_to_non_nullable
              as BriefingPriority,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      summary: null == summary
          ? _value.summary
          : summary // ignore: cast_nullable_to_non_nullable
              as String,
      impact: freezed == impact
          ? _value.impact
          : impact // ignore: cast_nullable_to_non_nullable
              as String?,
      actions: null == actions
          ? _value._actions
          : actions // ignore: cast_nullable_to_non_nullable
              as List<BriefingAction>,
      reportArtifactId: freezed == reportArtifactId
          ? _value.reportArtifactId
          : reportArtifactId // ignore: cast_nullable_to_non_nullable
              as String?,
      conversationId: freezed == conversationId
          ? _value.conversationId
          : conversationId // ignore: cast_nullable_to_non_nullable
              as String?,
      contextData: freezed == contextData
          ? _value._contextData
          : contextData // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as BriefingStatus,
      importanceScore: freezed == importanceScore
          ? _value.importanceScore
          : importanceScore // ignore: cast_nullable_to_non_nullable
              as double?,
      readAt: freezed == readAt
          ? _value.readAt
          : readAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      actionedAt: freezed == actionedAt
          ? _value.actionedAt
          : actionedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      expiresAt: freezed == expiresAt
          ? _value.expiresAt
          : expiresAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      agentName: freezed == agentName
          ? _value.agentName
          : agentName // ignore: cast_nullable_to_non_nullable
              as String?,
      agentAvatarUrl: freezed == agentAvatarUrl
          ? _value.agentAvatarUrl
          : agentAvatarUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      agentRole: freezed == agentRole
          ? _value.agentRole
          : agentRole // ignore: cast_nullable_to_non_nullable
              as String?,
      summaryStructured: null == summaryStructured
          ? _value._summaryStructured
          : summaryStructured // ignore: cast_nullable_to_non_nullable
              as List<BriefingNewsItem>,
      coverStyle: freezed == coverStyle
          ? _value.coverStyle
          : coverStyle // ignore: cast_nullable_to_non_nullable
              as String?,
      uiSchema: freezed == uiSchema
          ? _value._uiSchema
          : uiSchema // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      uiSchemaVersion: freezed == uiSchemaVersion
          ? _value.uiSchemaVersion
          : uiSchemaVersion // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$BriefingImpl implements _Briefing {
  const _$BriefingImpl(
      {required this.id,
      @JsonKey(name: 'agent_id') required this.agentId,
      @JsonKey(name: 'user_id') required this.userId,
      @JsonKey(name: 'briefing_type') required this.briefingType,
      required this.priority,
      required this.title,
      required this.summary,
      this.impact,
      final List<BriefingAction> actions = const [],
      @JsonKey(name: 'report_artifact_id') this.reportArtifactId,
      @JsonKey(name: 'conversation_id') this.conversationId,
      @JsonKey(name: 'context_data') final Map<String, dynamic>? contextData,
      required this.status,
      @JsonKey(name: 'importance_score') this.importanceScore,
      @JsonKey(name: 'read_at') this.readAt,
      @JsonKey(name: 'actioned_at') this.actionedAt,
      @JsonKey(name: 'created_at') required this.createdAt,
      @JsonKey(name: 'expires_at') this.expiresAt,
      @JsonKey(name: 'agent_name') this.agentName,
      @JsonKey(name: 'agent_avatar_url') this.agentAvatarUrl,
      @JsonKey(name: 'agent_role') this.agentRole,
      @JsonKey(name: 'summary_structured')
      final List<BriefingNewsItem> summaryStructured = const [],
      @JsonKey(name: 'cover_style')
      @Deprecated('Use ui_schema instead')
      this.coverStyle,
      @JsonKey(name: 'ui_schema') final Map<String, dynamic>? uiSchema,
      @JsonKey(name: 'ui_schema_version') this.uiSchemaVersion})
      : _actions = actions,
        _contextData = contextData,
        _summaryStructured = summaryStructured,
        _uiSchema = uiSchema;

  factory _$BriefingImpl.fromJson(Map<String, dynamic> json) =>
      _$$BriefingImplFromJson(json);

  @override
  final String id;
  @override
  @JsonKey(name: 'agent_id')
  final String agentId;
  @override
  @JsonKey(name: 'user_id')
  final String userId;
  @override
  @JsonKey(name: 'briefing_type')
  final BriefingType briefingType;
  @override
  final BriefingPriority priority;
  @override
  final String title;
  @override
  final String summary;
  @override
  final String? impact;
  final List<BriefingAction> _actions;
  @override
  @JsonKey()
  List<BriefingAction> get actions {
    if (_actions is EqualUnmodifiableListView) return _actions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_actions);
  }

  @override
  @JsonKey(name: 'report_artifact_id')
  final String? reportArtifactId;
  @override
  @JsonKey(name: 'conversation_id')
  final String? conversationId;
  final Map<String, dynamic>? _contextData;
  @override
  @JsonKey(name: 'context_data')
  Map<String, dynamic>? get contextData {
    final value = _contextData;
    if (value == null) return null;
    if (_contextData is EqualUnmodifiableMapView) return _contextData;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final BriefingStatus status;
  @override
  @JsonKey(name: 'importance_score')
  final double? importanceScore;
  @override
  @JsonKey(name: 'read_at')
  final DateTime? readAt;
  @override
  @JsonKey(name: 'actioned_at')
  final DateTime? actionedAt;
  @override
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @override
  @JsonKey(name: 'expires_at')
  final DateTime? expiresAt;
// 关联的Agent信息
  @override
  @JsonKey(name: 'agent_name')
  final String? agentName;
  @override
  @JsonKey(name: 'agent_avatar_url')
  final String? agentAvatarUrl;
  @override
  @JsonKey(name: 'agent_role')
  final String? agentRole;
// 结构化新闻列表（用于AI资讯类简报）
  final List<BriefingNewsItem> _summaryStructured;
// 结构化新闻列表（用于AI资讯类简报）
  @override
  @JsonKey(name: 'summary_structured')
  List<BriefingNewsItem> get summaryStructured {
    if (_summaryStructured is EqualUnmodifiableListView)
      return _summaryStructured;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_summaryStructured);
  }

// 封面样式提示（废弃字段，保留兼容性）
  @override
  @JsonKey(name: 'cover_style')
  @Deprecated('Use ui_schema instead')
  final String? coverStyle;
// A2UI 动态 UI Schema（新增）
  final Map<String, dynamic>? _uiSchema;
// A2UI 动态 UI Schema（新增）
  @override
  @JsonKey(name: 'ui_schema')
  Map<String, dynamic>? get uiSchema {
    final value = _uiSchema;
    if (value == null) return null;
    if (_uiSchema is EqualUnmodifiableMapView) return _uiSchema;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  @JsonKey(name: 'ui_schema_version')
  final String? uiSchemaVersion;

  @override
  String toString() {
    return 'Briefing(id: $id, agentId: $agentId, userId: $userId, briefingType: $briefingType, priority: $priority, title: $title, summary: $summary, impact: $impact, actions: $actions, reportArtifactId: $reportArtifactId, conversationId: $conversationId, contextData: $contextData, status: $status, importanceScore: $importanceScore, readAt: $readAt, actionedAt: $actionedAt, createdAt: $createdAt, expiresAt: $expiresAt, agentName: $agentName, agentAvatarUrl: $agentAvatarUrl, agentRole: $agentRole, summaryStructured: $summaryStructured, coverStyle: $coverStyle, uiSchema: $uiSchema, uiSchemaVersion: $uiSchemaVersion)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$BriefingImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.agentId, agentId) || other.agentId == agentId) &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.briefingType, briefingType) ||
                other.briefingType == briefingType) &&
            (identical(other.priority, priority) ||
                other.priority == priority) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.summary, summary) || other.summary == summary) &&
            (identical(other.impact, impact) || other.impact == impact) &&
            const DeepCollectionEquality().equals(other._actions, _actions) &&
            (identical(other.reportArtifactId, reportArtifactId) ||
                other.reportArtifactId == reportArtifactId) &&
            (identical(other.conversationId, conversationId) ||
                other.conversationId == conversationId) &&
            const DeepCollectionEquality()
                .equals(other._contextData, _contextData) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.importanceScore, importanceScore) ||
                other.importanceScore == importanceScore) &&
            (identical(other.readAt, readAt) || other.readAt == readAt) &&
            (identical(other.actionedAt, actionedAt) ||
                other.actionedAt == actionedAt) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.expiresAt, expiresAt) ||
                other.expiresAt == expiresAt) &&
            (identical(other.agentName, agentName) ||
                other.agentName == agentName) &&
            (identical(other.agentAvatarUrl, agentAvatarUrl) ||
                other.agentAvatarUrl == agentAvatarUrl) &&
            (identical(other.agentRole, agentRole) ||
                other.agentRole == agentRole) &&
            const DeepCollectionEquality()
                .equals(other._summaryStructured, _summaryStructured) &&
            (identical(other.coverStyle, coverStyle) ||
                other.coverStyle == coverStyle) &&
            const DeepCollectionEquality().equals(other._uiSchema, _uiSchema) &&
            (identical(other.uiSchemaVersion, uiSchemaVersion) ||
                other.uiSchemaVersion == uiSchemaVersion));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        id,
        agentId,
        userId,
        briefingType,
        priority,
        title,
        summary,
        impact,
        const DeepCollectionEquality().hash(_actions),
        reportArtifactId,
        conversationId,
        const DeepCollectionEquality().hash(_contextData),
        status,
        importanceScore,
        readAt,
        actionedAt,
        createdAt,
        expiresAt,
        agentName,
        agentAvatarUrl,
        agentRole,
        const DeepCollectionEquality().hash(_summaryStructured),
        coverStyle,
        const DeepCollectionEquality().hash(_uiSchema),
        uiSchemaVersion
      ]);

  /// Create a copy of Briefing
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$BriefingImplCopyWith<_$BriefingImpl> get copyWith =>
      __$$BriefingImplCopyWithImpl<_$BriefingImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$BriefingImplToJson(
      this,
    );
  }
}

abstract class _Briefing implements Briefing {
  const factory _Briefing(
      {required final String id,
      @JsonKey(name: 'agent_id') required final String agentId,
      @JsonKey(name: 'user_id') required final String userId,
      @JsonKey(name: 'briefing_type') required final BriefingType briefingType,
      required final BriefingPriority priority,
      required final String title,
      required final String summary,
      final String? impact,
      final List<BriefingAction> actions,
      @JsonKey(name: 'report_artifact_id') final String? reportArtifactId,
      @JsonKey(name: 'conversation_id') final String? conversationId,
      @JsonKey(name: 'context_data') final Map<String, dynamic>? contextData,
      required final BriefingStatus status,
      @JsonKey(name: 'importance_score') final double? importanceScore,
      @JsonKey(name: 'read_at') final DateTime? readAt,
      @JsonKey(name: 'actioned_at') final DateTime? actionedAt,
      @JsonKey(name: 'created_at') required final DateTime createdAt,
      @JsonKey(name: 'expires_at') final DateTime? expiresAt,
      @JsonKey(name: 'agent_name') final String? agentName,
      @JsonKey(name: 'agent_avatar_url') final String? agentAvatarUrl,
      @JsonKey(name: 'agent_role') final String? agentRole,
      @JsonKey(name: 'summary_structured')
      final List<BriefingNewsItem> summaryStructured,
      @JsonKey(name: 'cover_style')
      @Deprecated('Use ui_schema instead')
      final String? coverStyle,
      @JsonKey(name: 'ui_schema') final Map<String, dynamic>? uiSchema,
      @JsonKey(name: 'ui_schema_version')
      final String? uiSchemaVersion}) = _$BriefingImpl;

  factory _Briefing.fromJson(Map<String, dynamic> json) =
      _$BriefingImpl.fromJson;

  @override
  String get id;
  @override
  @JsonKey(name: 'agent_id')
  String get agentId;
  @override
  @JsonKey(name: 'user_id')
  String get userId;
  @override
  @JsonKey(name: 'briefing_type')
  BriefingType get briefingType;
  @override
  BriefingPriority get priority;
  @override
  String get title;
  @override
  String get summary;
  @override
  String? get impact;
  @override
  List<BriefingAction> get actions;
  @override
  @JsonKey(name: 'report_artifact_id')
  String? get reportArtifactId;
  @override
  @JsonKey(name: 'conversation_id')
  String? get conversationId;
  @override
  @JsonKey(name: 'context_data')
  Map<String, dynamic>? get contextData;
  @override
  BriefingStatus get status;
  @override
  @JsonKey(name: 'importance_score')
  double? get importanceScore;
  @override
  @JsonKey(name: 'read_at')
  DateTime? get readAt;
  @override
  @JsonKey(name: 'actioned_at')
  DateTime? get actionedAt;
  @override
  @JsonKey(name: 'created_at')
  DateTime get createdAt;
  @override
  @JsonKey(name: 'expires_at')
  DateTime? get expiresAt; // 关联的Agent信息
  @override
  @JsonKey(name: 'agent_name')
  String? get agentName;
  @override
  @JsonKey(name: 'agent_avatar_url')
  String? get agentAvatarUrl;
  @override
  @JsonKey(name: 'agent_role')
  String? get agentRole; // 结构化新闻列表（用于AI资讯类简报）
  @override
  @JsonKey(name: 'summary_structured')
  List<BriefingNewsItem> get summaryStructured; // 封面样式提示（废弃字段，保留兼容性）
  @override
  @JsonKey(name: 'cover_style')
  @Deprecated('Use ui_schema instead')
  String? get coverStyle; // A2UI 动态 UI Schema（新增）
  @override
  @JsonKey(name: 'ui_schema')
  Map<String, dynamic>? get uiSchema;
  @override
  @JsonKey(name: 'ui_schema_version')
  String? get uiSchemaVersion;

  /// Create a copy of Briefing
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$BriefingImplCopyWith<_$BriefingImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

BriefingListResponse _$BriefingListResponseFromJson(Map<String, dynamic> json) {
  return _BriefingListResponse.fromJson(json);
}

/// @nodoc
mixin _$BriefingListResponse {
  List<Briefing> get items => throw _privateConstructorUsedError;
  int get total => throw _privateConstructorUsedError;
  @JsonKey(name: 'unread_count')
  int get unreadCount => throw _privateConstructorUsedError;

  /// Serializes this BriefingListResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of BriefingListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $BriefingListResponseCopyWith<BriefingListResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BriefingListResponseCopyWith<$Res> {
  factory $BriefingListResponseCopyWith(BriefingListResponse value,
          $Res Function(BriefingListResponse) then) =
      _$BriefingListResponseCopyWithImpl<$Res, BriefingListResponse>;
  @useResult
  $Res call(
      {List<Briefing> items,
      int total,
      @JsonKey(name: 'unread_count') int unreadCount});
}

/// @nodoc
class _$BriefingListResponseCopyWithImpl<$Res,
        $Val extends BriefingListResponse>
    implements $BriefingListResponseCopyWith<$Res> {
  _$BriefingListResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of BriefingListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? items = null,
    Object? total = null,
    Object? unreadCount = null,
  }) {
    return _then(_value.copyWith(
      items: null == items
          ? _value.items
          : items // ignore: cast_nullable_to_non_nullable
              as List<Briefing>,
      total: null == total
          ? _value.total
          : total // ignore: cast_nullable_to_non_nullable
              as int,
      unreadCount: null == unreadCount
          ? _value.unreadCount
          : unreadCount // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$BriefingListResponseImplCopyWith<$Res>
    implements $BriefingListResponseCopyWith<$Res> {
  factory _$$BriefingListResponseImplCopyWith(_$BriefingListResponseImpl value,
          $Res Function(_$BriefingListResponseImpl) then) =
      __$$BriefingListResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<Briefing> items,
      int total,
      @JsonKey(name: 'unread_count') int unreadCount});
}

/// @nodoc
class __$$BriefingListResponseImplCopyWithImpl<$Res>
    extends _$BriefingListResponseCopyWithImpl<$Res, _$BriefingListResponseImpl>
    implements _$$BriefingListResponseImplCopyWith<$Res> {
  __$$BriefingListResponseImplCopyWithImpl(_$BriefingListResponseImpl _value,
      $Res Function(_$BriefingListResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of BriefingListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? items = null,
    Object? total = null,
    Object? unreadCount = null,
  }) {
    return _then(_$BriefingListResponseImpl(
      items: null == items
          ? _value._items
          : items // ignore: cast_nullable_to_non_nullable
              as List<Briefing>,
      total: null == total
          ? _value.total
          : total // ignore: cast_nullable_to_non_nullable
              as int,
      unreadCount: null == unreadCount
          ? _value.unreadCount
          : unreadCount // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$BriefingListResponseImpl implements _BriefingListResponse {
  const _$BriefingListResponseImpl(
      {required final List<Briefing> items,
      required this.total,
      @JsonKey(name: 'unread_count') required this.unreadCount})
      : _items = items;

  factory _$BriefingListResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$BriefingListResponseImplFromJson(json);

  final List<Briefing> _items;
  @override
  List<Briefing> get items {
    if (_items is EqualUnmodifiableListView) return _items;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_items);
  }

  @override
  final int total;
  @override
  @JsonKey(name: 'unread_count')
  final int unreadCount;

  @override
  String toString() {
    return 'BriefingListResponse(items: $items, total: $total, unreadCount: $unreadCount)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$BriefingListResponseImpl &&
            const DeepCollectionEquality().equals(other._items, _items) &&
            (identical(other.total, total) || other.total == total) &&
            (identical(other.unreadCount, unreadCount) ||
                other.unreadCount == unreadCount));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType,
      const DeepCollectionEquality().hash(_items), total, unreadCount);

  /// Create a copy of BriefingListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$BriefingListResponseImplCopyWith<_$BriefingListResponseImpl>
      get copyWith =>
          __$$BriefingListResponseImplCopyWithImpl<_$BriefingListResponseImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$BriefingListResponseImplToJson(
      this,
    );
  }
}

abstract class _BriefingListResponse implements BriefingListResponse {
  const factory _BriefingListResponse(
          {required final List<Briefing> items,
          required final int total,
          @JsonKey(name: 'unread_count') required final int unreadCount}) =
      _$BriefingListResponseImpl;

  factory _BriefingListResponse.fromJson(Map<String, dynamic> json) =
      _$BriefingListResponseImpl.fromJson;

  @override
  List<Briefing> get items;
  @override
  int get total;
  @override
  @JsonKey(name: 'unread_count')
  int get unreadCount;

  /// Create a copy of BriefingListResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$BriefingListResponseImplCopyWith<_$BriefingListResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}

BriefingUnreadCount _$BriefingUnreadCountFromJson(Map<String, dynamic> json) {
  return _BriefingUnreadCount.fromJson(json);
}

/// @nodoc
mixin _$BriefingUnreadCount {
  int get count => throw _privateConstructorUsedError;
  @JsonKey(name: 'by_priority')
  Map<String, int> get byPriority => throw _privateConstructorUsedError;

  /// Serializes this BriefingUnreadCount to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of BriefingUnreadCount
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $BriefingUnreadCountCopyWith<BriefingUnreadCount> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BriefingUnreadCountCopyWith<$Res> {
  factory $BriefingUnreadCountCopyWith(
          BriefingUnreadCount value, $Res Function(BriefingUnreadCount) then) =
      _$BriefingUnreadCountCopyWithImpl<$Res, BriefingUnreadCount>;
  @useResult
  $Res call(
      {int count, @JsonKey(name: 'by_priority') Map<String, int> byPriority});
}

/// @nodoc
class _$BriefingUnreadCountCopyWithImpl<$Res, $Val extends BriefingUnreadCount>
    implements $BriefingUnreadCountCopyWith<$Res> {
  _$BriefingUnreadCountCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of BriefingUnreadCount
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? count = null,
    Object? byPriority = null,
  }) {
    return _then(_value.copyWith(
      count: null == count
          ? _value.count
          : count // ignore: cast_nullable_to_non_nullable
              as int,
      byPriority: null == byPriority
          ? _value.byPriority
          : byPriority // ignore: cast_nullable_to_non_nullable
              as Map<String, int>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$BriefingUnreadCountImplCopyWith<$Res>
    implements $BriefingUnreadCountCopyWith<$Res> {
  factory _$$BriefingUnreadCountImplCopyWith(_$BriefingUnreadCountImpl value,
          $Res Function(_$BriefingUnreadCountImpl) then) =
      __$$BriefingUnreadCountImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int count, @JsonKey(name: 'by_priority') Map<String, int> byPriority});
}

/// @nodoc
class __$$BriefingUnreadCountImplCopyWithImpl<$Res>
    extends _$BriefingUnreadCountCopyWithImpl<$Res, _$BriefingUnreadCountImpl>
    implements _$$BriefingUnreadCountImplCopyWith<$Res> {
  __$$BriefingUnreadCountImplCopyWithImpl(_$BriefingUnreadCountImpl _value,
      $Res Function(_$BriefingUnreadCountImpl) _then)
      : super(_value, _then);

  /// Create a copy of BriefingUnreadCount
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? count = null,
    Object? byPriority = null,
  }) {
    return _then(_$BriefingUnreadCountImpl(
      count: null == count
          ? _value.count
          : count // ignore: cast_nullable_to_non_nullable
              as int,
      byPriority: null == byPriority
          ? _value._byPriority
          : byPriority // ignore: cast_nullable_to_non_nullable
              as Map<String, int>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$BriefingUnreadCountImpl implements _BriefingUnreadCount {
  const _$BriefingUnreadCountImpl(
      {required this.count,
      @JsonKey(name: 'by_priority')
      final Map<String, int> byPriority = const {}})
      : _byPriority = byPriority;

  factory _$BriefingUnreadCountImpl.fromJson(Map<String, dynamic> json) =>
      _$$BriefingUnreadCountImplFromJson(json);

  @override
  final int count;
  final Map<String, int> _byPriority;
  @override
  @JsonKey(name: 'by_priority')
  Map<String, int> get byPriority {
    if (_byPriority is EqualUnmodifiableMapView) return _byPriority;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_byPriority);
  }

  @override
  String toString() {
    return 'BriefingUnreadCount(count: $count, byPriority: $byPriority)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$BriefingUnreadCountImpl &&
            (identical(other.count, count) || other.count == count) &&
            const DeepCollectionEquality()
                .equals(other._byPriority, _byPriority));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, count, const DeepCollectionEquality().hash(_byPriority));

  /// Create a copy of BriefingUnreadCount
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$BriefingUnreadCountImplCopyWith<_$BriefingUnreadCountImpl> get copyWith =>
      __$$BriefingUnreadCountImplCopyWithImpl<_$BriefingUnreadCountImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$BriefingUnreadCountImplToJson(
      this,
    );
  }
}

abstract class _BriefingUnreadCount implements BriefingUnreadCount {
  const factory _BriefingUnreadCount(
          {required final int count,
          @JsonKey(name: 'by_priority') final Map<String, int> byPriority}) =
      _$BriefingUnreadCountImpl;

  factory _BriefingUnreadCount.fromJson(Map<String, dynamic> json) =
      _$BriefingUnreadCountImpl.fromJson;

  @override
  int get count;
  @override
  @JsonKey(name: 'by_priority')
  Map<String, int> get byPriority;

  /// Create a copy of BriefingUnreadCount
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$BriefingUnreadCountImplCopyWith<_$BriefingUnreadCountImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

StartConversationResponse _$StartConversationResponseFromJson(
    Map<String, dynamic> json) {
  return _StartConversationResponse.fromJson(json);
}

/// @nodoc
mixin _$StartConversationResponse {
  @JsonKey(name: 'conversation_id')
  String get conversationId => throw _privateConstructorUsedError;
  @JsonKey(name: 'briefing_id')
  String get briefingId => throw _privateConstructorUsedError;

  /// Serializes this StartConversationResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of StartConversationResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $StartConversationResponseCopyWith<StartConversationResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $StartConversationResponseCopyWith<$Res> {
  factory $StartConversationResponseCopyWith(StartConversationResponse value,
          $Res Function(StartConversationResponse) then) =
      _$StartConversationResponseCopyWithImpl<$Res, StartConversationResponse>;
  @useResult
  $Res call(
      {@JsonKey(name: 'conversation_id') String conversationId,
      @JsonKey(name: 'briefing_id') String briefingId});
}

/// @nodoc
class _$StartConversationResponseCopyWithImpl<$Res,
        $Val extends StartConversationResponse>
    implements $StartConversationResponseCopyWith<$Res> {
  _$StartConversationResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of StartConversationResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? conversationId = null,
    Object? briefingId = null,
  }) {
    return _then(_value.copyWith(
      conversationId: null == conversationId
          ? _value.conversationId
          : conversationId // ignore: cast_nullable_to_non_nullable
              as String,
      briefingId: null == briefingId
          ? _value.briefingId
          : briefingId // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$StartConversationResponseImplCopyWith<$Res>
    implements $StartConversationResponseCopyWith<$Res> {
  factory _$$StartConversationResponseImplCopyWith(
          _$StartConversationResponseImpl value,
          $Res Function(_$StartConversationResponseImpl) then) =
      __$$StartConversationResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'conversation_id') String conversationId,
      @JsonKey(name: 'briefing_id') String briefingId});
}

/// @nodoc
class __$$StartConversationResponseImplCopyWithImpl<$Res>
    extends _$StartConversationResponseCopyWithImpl<$Res,
        _$StartConversationResponseImpl>
    implements _$$StartConversationResponseImplCopyWith<$Res> {
  __$$StartConversationResponseImplCopyWithImpl(
      _$StartConversationResponseImpl _value,
      $Res Function(_$StartConversationResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of StartConversationResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? conversationId = null,
    Object? briefingId = null,
  }) {
    return _then(_$StartConversationResponseImpl(
      conversationId: null == conversationId
          ? _value.conversationId
          : conversationId // ignore: cast_nullable_to_non_nullable
              as String,
      briefingId: null == briefingId
          ? _value.briefingId
          : briefingId // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$StartConversationResponseImpl implements _StartConversationResponse {
  const _$StartConversationResponseImpl(
      {@JsonKey(name: 'conversation_id') required this.conversationId,
      @JsonKey(name: 'briefing_id') required this.briefingId});

  factory _$StartConversationResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$StartConversationResponseImplFromJson(json);

  @override
  @JsonKey(name: 'conversation_id')
  final String conversationId;
  @override
  @JsonKey(name: 'briefing_id')
  final String briefingId;

  @override
  String toString() {
    return 'StartConversationResponse(conversationId: $conversationId, briefingId: $briefingId)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$StartConversationResponseImpl &&
            (identical(other.conversationId, conversationId) ||
                other.conversationId == conversationId) &&
            (identical(other.briefingId, briefingId) ||
                other.briefingId == briefingId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, conversationId, briefingId);

  /// Create a copy of StartConversationResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$StartConversationResponseImplCopyWith<_$StartConversationResponseImpl>
      get copyWith => __$$StartConversationResponseImplCopyWithImpl<
          _$StartConversationResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$StartConversationResponseImplToJson(
      this,
    );
  }
}

abstract class _StartConversationResponse implements StartConversationResponse {
  const factory _StartConversationResponse(
      {@JsonKey(name: 'conversation_id') required final String conversationId,
      @JsonKey(name: 'briefing_id')
      required final String briefingId}) = _$StartConversationResponseImpl;

  factory _StartConversationResponse.fromJson(Map<String, dynamic> json) =
      _$StartConversationResponseImpl.fromJson;

  @override
  @JsonKey(name: 'conversation_id')
  String get conversationId;
  @override
  @JsonKey(name: 'briefing_id')
  String get briefingId;

  /// Create a copy of StartConversationResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$StartConversationResponseImplCopyWith<_$StartConversationResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}
