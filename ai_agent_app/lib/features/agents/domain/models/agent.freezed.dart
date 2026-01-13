// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'agent.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

Agent _$AgentFromJson(Map<String, dynamic> json) {
  return _Agent.fromJson(json);
}

/// @nodoc
mixin _$Agent {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  String get role => throw _privateConstructorUsedError;
  @JsonKey(name: 'avatar_url')
  String? get avatarUrl => throw _privateConstructorUsedError;
  @JsonKey(name: 'data_sources')
  Map<String, dynamic>? get dataSources => throw _privateConstructorUsedError;
  @JsonKey(name: 'trigger_conditions')
  Map<String, dynamic>? get triggerConditions =>
      throw _privateConstructorUsedError;
  @JsonKey(name: 'is_active')
  bool get isActive => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  DateTime? get createdAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_by')
  String? get createdBy => throw _privateConstructorUsedError;

  /// Serializes this Agent to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Agent
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AgentCopyWith<Agent> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AgentCopyWith<$Res> {
  factory $AgentCopyWith(Agent value, $Res Function(Agent) then) =
      _$AgentCopyWithImpl<$Res, Agent>;
  @useResult
  $Res call(
      {String id,
      String name,
      String description,
      String role,
      @JsonKey(name: 'avatar_url') String? avatarUrl,
      @JsonKey(name: 'data_sources') Map<String, dynamic>? dataSources,
      @JsonKey(name: 'trigger_conditions')
      Map<String, dynamic>? triggerConditions,
      @JsonKey(name: 'is_active') bool isActive,
      @JsonKey(name: 'created_at') DateTime? createdAt,
      @JsonKey(name: 'created_by') String? createdBy});
}

/// @nodoc
class _$AgentCopyWithImpl<$Res, $Val extends Agent>
    implements $AgentCopyWith<$Res> {
  _$AgentCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Agent
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? description = null,
    Object? role = null,
    Object? avatarUrl = freezed,
    Object? dataSources = freezed,
    Object? triggerConditions = freezed,
    Object? isActive = null,
    Object? createdAt = freezed,
    Object? createdBy = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      role: null == role
          ? _value.role
          : role // ignore: cast_nullable_to_non_nullable
              as String,
      avatarUrl: freezed == avatarUrl
          ? _value.avatarUrl
          : avatarUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      dataSources: freezed == dataSources
          ? _value.dataSources
          : dataSources // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      triggerConditions: freezed == triggerConditions
          ? _value.triggerConditions
          : triggerConditions // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdBy: freezed == createdBy
          ? _value.createdBy
          : createdBy // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AgentImplCopyWith<$Res> implements $AgentCopyWith<$Res> {
  factory _$$AgentImplCopyWith(
          _$AgentImpl value, $Res Function(_$AgentImpl) then) =
      __$$AgentImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String description,
      String role,
      @JsonKey(name: 'avatar_url') String? avatarUrl,
      @JsonKey(name: 'data_sources') Map<String, dynamic>? dataSources,
      @JsonKey(name: 'trigger_conditions')
      Map<String, dynamic>? triggerConditions,
      @JsonKey(name: 'is_active') bool isActive,
      @JsonKey(name: 'created_at') DateTime? createdAt,
      @JsonKey(name: 'created_by') String? createdBy});
}

/// @nodoc
class __$$AgentImplCopyWithImpl<$Res>
    extends _$AgentCopyWithImpl<$Res, _$AgentImpl>
    implements _$$AgentImplCopyWith<$Res> {
  __$$AgentImplCopyWithImpl(
      _$AgentImpl _value, $Res Function(_$AgentImpl) _then)
      : super(_value, _then);

  /// Create a copy of Agent
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? description = null,
    Object? role = null,
    Object? avatarUrl = freezed,
    Object? dataSources = freezed,
    Object? triggerConditions = freezed,
    Object? isActive = null,
    Object? createdAt = freezed,
    Object? createdBy = freezed,
  }) {
    return _then(_$AgentImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      role: null == role
          ? _value.role
          : role // ignore: cast_nullable_to_non_nullable
              as String,
      avatarUrl: freezed == avatarUrl
          ? _value.avatarUrl
          : avatarUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      dataSources: freezed == dataSources
          ? _value._dataSources
          : dataSources // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      triggerConditions: freezed == triggerConditions
          ? _value._triggerConditions
          : triggerConditions // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdBy: freezed == createdBy
          ? _value.createdBy
          : createdBy // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AgentImpl implements _Agent {
  const _$AgentImpl(
      {required this.id,
      required this.name,
      required this.description,
      required this.role,
      @JsonKey(name: 'avatar_url') this.avatarUrl,
      @JsonKey(name: 'data_sources') final Map<String, dynamic>? dataSources,
      @JsonKey(name: 'trigger_conditions')
      final Map<String, dynamic>? triggerConditions,
      @JsonKey(name: 'is_active') this.isActive = true,
      @JsonKey(name: 'created_at') this.createdAt,
      @JsonKey(name: 'created_by') this.createdBy})
      : _dataSources = dataSources,
        _triggerConditions = triggerConditions;

  factory _$AgentImpl.fromJson(Map<String, dynamic> json) =>
      _$$AgentImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String description;
  @override
  final String role;
  @override
  @JsonKey(name: 'avatar_url')
  final String? avatarUrl;
  final Map<String, dynamic>? _dataSources;
  @override
  @JsonKey(name: 'data_sources')
  Map<String, dynamic>? get dataSources {
    final value = _dataSources;
    if (value == null) return null;
    if (_dataSources is EqualUnmodifiableMapView) return _dataSources;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final Map<String, dynamic>? _triggerConditions;
  @override
  @JsonKey(name: 'trigger_conditions')
  Map<String, dynamic>? get triggerConditions {
    final value = _triggerConditions;
    if (value == null) return null;
    if (_triggerConditions is EqualUnmodifiableMapView)
      return _triggerConditions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  @JsonKey(name: 'is_active')
  final bool isActive;
  @override
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;
  @override
  @JsonKey(name: 'created_by')
  final String? createdBy;

  @override
  String toString() {
    return 'Agent(id: $id, name: $name, description: $description, role: $role, avatarUrl: $avatarUrl, dataSources: $dataSources, triggerConditions: $triggerConditions, isActive: $isActive, createdAt: $createdAt, createdBy: $createdBy)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AgentImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.role, role) || other.role == role) &&
            (identical(other.avatarUrl, avatarUrl) ||
                other.avatarUrl == avatarUrl) &&
            const DeepCollectionEquality()
                .equals(other._dataSources, _dataSources) &&
            const DeepCollectionEquality()
                .equals(other._triggerConditions, _triggerConditions) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.createdBy, createdBy) ||
                other.createdBy == createdBy));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      name,
      description,
      role,
      avatarUrl,
      const DeepCollectionEquality().hash(_dataSources),
      const DeepCollectionEquality().hash(_triggerConditions),
      isActive,
      createdAt,
      createdBy);

  /// Create a copy of Agent
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AgentImplCopyWith<_$AgentImpl> get copyWith =>
      __$$AgentImplCopyWithImpl<_$AgentImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AgentImplToJson(
      this,
    );
  }
}

abstract class _Agent implements Agent {
  const factory _Agent(
      {required final String id,
      required final String name,
      required final String description,
      required final String role,
      @JsonKey(name: 'avatar_url') final String? avatarUrl,
      @JsonKey(name: 'data_sources') final Map<String, dynamic>? dataSources,
      @JsonKey(name: 'trigger_conditions')
      final Map<String, dynamic>? triggerConditions,
      @JsonKey(name: 'is_active') final bool isActive,
      @JsonKey(name: 'created_at') final DateTime? createdAt,
      @JsonKey(name: 'created_by') final String? createdBy}) = _$AgentImpl;

  factory _Agent.fromJson(Map<String, dynamic> json) = _$AgentImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String get description;
  @override
  String get role;
  @override
  @JsonKey(name: 'avatar_url')
  String? get avatarUrl;
  @override
  @JsonKey(name: 'data_sources')
  Map<String, dynamic>? get dataSources;
  @override
  @JsonKey(name: 'trigger_conditions')
  Map<String, dynamic>? get triggerConditions;
  @override
  @JsonKey(name: 'is_active')
  bool get isActive;
  @override
  @JsonKey(name: 'created_at')
  DateTime? get createdAt;
  @override
  @JsonKey(name: 'created_by')
  String? get createdBy;

  /// Create a copy of Agent
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AgentImplCopyWith<_$AgentImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

UserAgentSubscription _$UserAgentSubscriptionFromJson(
    Map<String, dynamic> json) {
  return _UserAgentSubscription.fromJson(json);
}

/// @nodoc
mixin _$UserAgentSubscription {
  @JsonKey(name: 'user_id')
  String get userId => throw _privateConstructorUsedError;
  @JsonKey(name: 'agent_id')
  String get agentId => throw _privateConstructorUsedError;
  @JsonKey(name: 'subscribed_at')
  DateTime get subscribedAt => throw _privateConstructorUsedError;
  Map<String, dynamic>? get config => throw _privateConstructorUsedError;
  Agent? get agent => throw _privateConstructorUsedError;

  /// Serializes this UserAgentSubscription to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UserAgentSubscription
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UserAgentSubscriptionCopyWith<UserAgentSubscription> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UserAgentSubscriptionCopyWith<$Res> {
  factory $UserAgentSubscriptionCopyWith(UserAgentSubscription value,
          $Res Function(UserAgentSubscription) then) =
      _$UserAgentSubscriptionCopyWithImpl<$Res, UserAgentSubscription>;
  @useResult
  $Res call(
      {@JsonKey(name: 'user_id') String userId,
      @JsonKey(name: 'agent_id') String agentId,
      @JsonKey(name: 'subscribed_at') DateTime subscribedAt,
      Map<String, dynamic>? config,
      Agent? agent});

  $AgentCopyWith<$Res>? get agent;
}

/// @nodoc
class _$UserAgentSubscriptionCopyWithImpl<$Res,
        $Val extends UserAgentSubscription>
    implements $UserAgentSubscriptionCopyWith<$Res> {
  _$UserAgentSubscriptionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UserAgentSubscription
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? userId = null,
    Object? agentId = null,
    Object? subscribedAt = null,
    Object? config = freezed,
    Object? agent = freezed,
  }) {
    return _then(_value.copyWith(
      userId: null == userId
          ? _value.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String,
      agentId: null == agentId
          ? _value.agentId
          : agentId // ignore: cast_nullable_to_non_nullable
              as String,
      subscribedAt: null == subscribedAt
          ? _value.subscribedAt
          : subscribedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      config: freezed == config
          ? _value.config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      agent: freezed == agent
          ? _value.agent
          : agent // ignore: cast_nullable_to_non_nullable
              as Agent?,
    ) as $Val);
  }

  /// Create a copy of UserAgentSubscription
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $AgentCopyWith<$Res>? get agent {
    if (_value.agent == null) {
      return null;
    }

    return $AgentCopyWith<$Res>(_value.agent!, (value) {
      return _then(_value.copyWith(agent: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$UserAgentSubscriptionImplCopyWith<$Res>
    implements $UserAgentSubscriptionCopyWith<$Res> {
  factory _$$UserAgentSubscriptionImplCopyWith(
          _$UserAgentSubscriptionImpl value,
          $Res Function(_$UserAgentSubscriptionImpl) then) =
      __$$UserAgentSubscriptionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'user_id') String userId,
      @JsonKey(name: 'agent_id') String agentId,
      @JsonKey(name: 'subscribed_at') DateTime subscribedAt,
      Map<String, dynamic>? config,
      Agent? agent});

  @override
  $AgentCopyWith<$Res>? get agent;
}

/// @nodoc
class __$$UserAgentSubscriptionImplCopyWithImpl<$Res>
    extends _$UserAgentSubscriptionCopyWithImpl<$Res,
        _$UserAgentSubscriptionImpl>
    implements _$$UserAgentSubscriptionImplCopyWith<$Res> {
  __$$UserAgentSubscriptionImplCopyWithImpl(_$UserAgentSubscriptionImpl _value,
      $Res Function(_$UserAgentSubscriptionImpl) _then)
      : super(_value, _then);

  /// Create a copy of UserAgentSubscription
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? userId = null,
    Object? agentId = null,
    Object? subscribedAt = null,
    Object? config = freezed,
    Object? agent = freezed,
  }) {
    return _then(_$UserAgentSubscriptionImpl(
      userId: null == userId
          ? _value.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String,
      agentId: null == agentId
          ? _value.agentId
          : agentId // ignore: cast_nullable_to_non_nullable
              as String,
      subscribedAt: null == subscribedAt
          ? _value.subscribedAt
          : subscribedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      config: freezed == config
          ? _value._config
          : config // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      agent: freezed == agent
          ? _value.agent
          : agent // ignore: cast_nullable_to_non_nullable
              as Agent?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UserAgentSubscriptionImpl implements _UserAgentSubscription {
  const _$UserAgentSubscriptionImpl(
      {@JsonKey(name: 'user_id') required this.userId,
      @JsonKey(name: 'agent_id') required this.agentId,
      @JsonKey(name: 'subscribed_at') required this.subscribedAt,
      final Map<String, dynamic>? config,
      this.agent})
      : _config = config;

  factory _$UserAgentSubscriptionImpl.fromJson(Map<String, dynamic> json) =>
      _$$UserAgentSubscriptionImplFromJson(json);

  @override
  @JsonKey(name: 'user_id')
  final String userId;
  @override
  @JsonKey(name: 'agent_id')
  final String agentId;
  @override
  @JsonKey(name: 'subscribed_at')
  final DateTime subscribedAt;
  final Map<String, dynamic>? _config;
  @override
  Map<String, dynamic>? get config {
    final value = _config;
    if (value == null) return null;
    if (_config is EqualUnmodifiableMapView) return _config;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final Agent? agent;

  @override
  String toString() {
    return 'UserAgentSubscription(userId: $userId, agentId: $agentId, subscribedAt: $subscribedAt, config: $config, agent: $agent)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UserAgentSubscriptionImpl &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.agentId, agentId) || other.agentId == agentId) &&
            (identical(other.subscribedAt, subscribedAt) ||
                other.subscribedAt == subscribedAt) &&
            const DeepCollectionEquality().equals(other._config, _config) &&
            (identical(other.agent, agent) || other.agent == agent));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, userId, agentId, subscribedAt,
      const DeepCollectionEquality().hash(_config), agent);

  /// Create a copy of UserAgentSubscription
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UserAgentSubscriptionImplCopyWith<_$UserAgentSubscriptionImpl>
      get copyWith => __$$UserAgentSubscriptionImplCopyWithImpl<
          _$UserAgentSubscriptionImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UserAgentSubscriptionImplToJson(
      this,
    );
  }
}

abstract class _UserAgentSubscription implements UserAgentSubscription {
  const factory _UserAgentSubscription(
      {@JsonKey(name: 'user_id') required final String userId,
      @JsonKey(name: 'agent_id') required final String agentId,
      @JsonKey(name: 'subscribed_at') required final DateTime subscribedAt,
      final Map<String, dynamic>? config,
      final Agent? agent}) = _$UserAgentSubscriptionImpl;

  factory _UserAgentSubscription.fromJson(Map<String, dynamic> json) =
      _$UserAgentSubscriptionImpl.fromJson;

  @override
  @JsonKey(name: 'user_id')
  String get userId;
  @override
  @JsonKey(name: 'agent_id')
  String get agentId;
  @override
  @JsonKey(name: 'subscribed_at')
  DateTime get subscribedAt;
  @override
  Map<String, dynamic>? get config;
  @override
  Agent? get agent;

  /// Create a copy of UserAgentSubscription
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UserAgentSubscriptionImplCopyWith<_$UserAgentSubscriptionImpl>
      get copyWith => throw _privateConstructorUsedError;
}
