// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'usage_stats.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

UsageStats _$UsageStatsFromJson(Map<String, dynamic> json) {
  return _UsageStats.fromJson(json);
}

/// @nodoc
mixin _$UsageStats {
  @JsonKey(name: 'total_briefings')
  int get totalBriefings => throw _privateConstructorUsedError;
  @JsonKey(name: 'weekly_briefings')
  int get weeklyBriefings => throw _privateConstructorUsedError;
  @JsonKey(name: 'active_conversations')
  int get activeConversations => throw _privateConstructorUsedError;
  @JsonKey(name: 'total_messages')
  int get totalMessages => throw _privateConstructorUsedError;

  /// Serializes this UsageStats to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UsageStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UsageStatsCopyWith<UsageStats> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UsageStatsCopyWith<$Res> {
  factory $UsageStatsCopyWith(
          UsageStats value, $Res Function(UsageStats) then) =
      _$UsageStatsCopyWithImpl<$Res, UsageStats>;
  @useResult
  $Res call(
      {@JsonKey(name: 'total_briefings') int totalBriefings,
      @JsonKey(name: 'weekly_briefings') int weeklyBriefings,
      @JsonKey(name: 'active_conversations') int activeConversations,
      @JsonKey(name: 'total_messages') int totalMessages});
}

/// @nodoc
class _$UsageStatsCopyWithImpl<$Res, $Val extends UsageStats>
    implements $UsageStatsCopyWith<$Res> {
  _$UsageStatsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UsageStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalBriefings = null,
    Object? weeklyBriefings = null,
    Object? activeConversations = null,
    Object? totalMessages = null,
  }) {
    return _then(_value.copyWith(
      totalBriefings: null == totalBriefings
          ? _value.totalBriefings
          : totalBriefings // ignore: cast_nullable_to_non_nullable
              as int,
      weeklyBriefings: null == weeklyBriefings
          ? _value.weeklyBriefings
          : weeklyBriefings // ignore: cast_nullable_to_non_nullable
              as int,
      activeConversations: null == activeConversations
          ? _value.activeConversations
          : activeConversations // ignore: cast_nullable_to_non_nullable
              as int,
      totalMessages: null == totalMessages
          ? _value.totalMessages
          : totalMessages // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UsageStatsImplCopyWith<$Res>
    implements $UsageStatsCopyWith<$Res> {
  factory _$$UsageStatsImplCopyWith(
          _$UsageStatsImpl value, $Res Function(_$UsageStatsImpl) then) =
      __$$UsageStatsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'total_briefings') int totalBriefings,
      @JsonKey(name: 'weekly_briefings') int weeklyBriefings,
      @JsonKey(name: 'active_conversations') int activeConversations,
      @JsonKey(name: 'total_messages') int totalMessages});
}

/// @nodoc
class __$$UsageStatsImplCopyWithImpl<$Res>
    extends _$UsageStatsCopyWithImpl<$Res, _$UsageStatsImpl>
    implements _$$UsageStatsImplCopyWith<$Res> {
  __$$UsageStatsImplCopyWithImpl(
      _$UsageStatsImpl _value, $Res Function(_$UsageStatsImpl) _then)
      : super(_value, _then);

  /// Create a copy of UsageStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalBriefings = null,
    Object? weeklyBriefings = null,
    Object? activeConversations = null,
    Object? totalMessages = null,
  }) {
    return _then(_$UsageStatsImpl(
      totalBriefings: null == totalBriefings
          ? _value.totalBriefings
          : totalBriefings // ignore: cast_nullable_to_non_nullable
              as int,
      weeklyBriefings: null == weeklyBriefings
          ? _value.weeklyBriefings
          : weeklyBriefings // ignore: cast_nullable_to_non_nullable
              as int,
      activeConversations: null == activeConversations
          ? _value.activeConversations
          : activeConversations // ignore: cast_nullable_to_non_nullable
              as int,
      totalMessages: null == totalMessages
          ? _value.totalMessages
          : totalMessages // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UsageStatsImpl implements _UsageStats {
  const _$UsageStatsImpl(
      {@JsonKey(name: 'total_briefings') this.totalBriefings = 0,
      @JsonKey(name: 'weekly_briefings') this.weeklyBriefings = 0,
      @JsonKey(name: 'active_conversations') this.activeConversations = 0,
      @JsonKey(name: 'total_messages') this.totalMessages = 0});

  factory _$UsageStatsImpl.fromJson(Map<String, dynamic> json) =>
      _$$UsageStatsImplFromJson(json);

  @override
  @JsonKey(name: 'total_briefings')
  final int totalBriefings;
  @override
  @JsonKey(name: 'weekly_briefings')
  final int weeklyBriefings;
  @override
  @JsonKey(name: 'active_conversations')
  final int activeConversations;
  @override
  @JsonKey(name: 'total_messages')
  final int totalMessages;

  @override
  String toString() {
    return 'UsageStats(totalBriefings: $totalBriefings, weeklyBriefings: $weeklyBriefings, activeConversations: $activeConversations, totalMessages: $totalMessages)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UsageStatsImpl &&
            (identical(other.totalBriefings, totalBriefings) ||
                other.totalBriefings == totalBriefings) &&
            (identical(other.weeklyBriefings, weeklyBriefings) ||
                other.weeklyBriefings == weeklyBriefings) &&
            (identical(other.activeConversations, activeConversations) ||
                other.activeConversations == activeConversations) &&
            (identical(other.totalMessages, totalMessages) ||
                other.totalMessages == totalMessages));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, totalBriefings, weeklyBriefings,
      activeConversations, totalMessages);

  /// Create a copy of UsageStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UsageStatsImplCopyWith<_$UsageStatsImpl> get copyWith =>
      __$$UsageStatsImplCopyWithImpl<_$UsageStatsImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UsageStatsImplToJson(
      this,
    );
  }
}

abstract class _UsageStats implements UsageStats {
  const factory _UsageStats(
          {@JsonKey(name: 'total_briefings') final int totalBriefings,
          @JsonKey(name: 'weekly_briefings') final int weeklyBriefings,
          @JsonKey(name: 'active_conversations') final int activeConversations,
          @JsonKey(name: 'total_messages') final int totalMessages}) =
      _$UsageStatsImpl;

  factory _UsageStats.fromJson(Map<String, dynamic> json) =
      _$UsageStatsImpl.fromJson;

  @override
  @JsonKey(name: 'total_briefings')
  int get totalBriefings;
  @override
  @JsonKey(name: 'weekly_briefings')
  int get weeklyBriefings;
  @override
  @JsonKey(name: 'active_conversations')
  int get activeConversations;
  @override
  @JsonKey(name: 'total_messages')
  int get totalMessages;

  /// Create a copy of UsageStats
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UsageStatsImplCopyWith<_$UsageStatsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
