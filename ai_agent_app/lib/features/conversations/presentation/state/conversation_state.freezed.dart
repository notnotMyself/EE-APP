// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'conversation_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$ToolExecutionState {
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() idle,
    required TResult Function(
            String toolName,
            String toolId,
            Map<String, dynamic>? toolInput,
            DateTime startedAt,
            double progress,
            String status,
            String? filePath,
            String? statusMessage)
        executing,
    required TResult Function(
            String toolName, String toolId, String? result, bool? isError)
        completed,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? idle,
    TResult? Function(
            String toolName,
            String toolId,
            Map<String, dynamic>? toolInput,
            DateTime startedAt,
            double progress,
            String status,
            String? filePath,
            String? statusMessage)?
        executing,
    TResult? Function(
            String toolName, String toolId, String? result, bool? isError)?
        completed,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? idle,
    TResult Function(
            String toolName,
            String toolId,
            Map<String, dynamic>? toolInput,
            DateTime startedAt,
            double progress,
            String status,
            String? filePath,
            String? statusMessage)?
        executing,
    TResult Function(
            String toolName, String toolId, String? result, bool? isError)?
        completed,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(ToolExecutionStateIdle value) idle,
    required TResult Function(ToolExecutionStateExecuting value) executing,
    required TResult Function(ToolExecutionStateCompleted value) completed,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(ToolExecutionStateIdle value)? idle,
    TResult? Function(ToolExecutionStateExecuting value)? executing,
    TResult? Function(ToolExecutionStateCompleted value)? completed,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(ToolExecutionStateIdle value)? idle,
    TResult Function(ToolExecutionStateExecuting value)? executing,
    TResult Function(ToolExecutionStateCompleted value)? completed,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ToolExecutionStateCopyWith<$Res> {
  factory $ToolExecutionStateCopyWith(
          ToolExecutionState value, $Res Function(ToolExecutionState) then) =
      _$ToolExecutionStateCopyWithImpl<$Res, ToolExecutionState>;
}

/// @nodoc
class _$ToolExecutionStateCopyWithImpl<$Res, $Val extends ToolExecutionState>
    implements $ToolExecutionStateCopyWith<$Res> {
  _$ToolExecutionStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ToolExecutionState
  /// with the given fields replaced by the non-null parameter values.
}

/// @nodoc
abstract class _$$ToolExecutionStateIdleImplCopyWith<$Res> {
  factory _$$ToolExecutionStateIdleImplCopyWith(
          _$ToolExecutionStateIdleImpl value,
          $Res Function(_$ToolExecutionStateIdleImpl) then) =
      __$$ToolExecutionStateIdleImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$ToolExecutionStateIdleImplCopyWithImpl<$Res>
    extends _$ToolExecutionStateCopyWithImpl<$Res, _$ToolExecutionStateIdleImpl>
    implements _$$ToolExecutionStateIdleImplCopyWith<$Res> {
  __$$ToolExecutionStateIdleImplCopyWithImpl(
      _$ToolExecutionStateIdleImpl _value,
      $Res Function(_$ToolExecutionStateIdleImpl) _then)
      : super(_value, _then);

  /// Create a copy of ToolExecutionState
  /// with the given fields replaced by the non-null parameter values.
}

/// @nodoc

class _$ToolExecutionStateIdleImpl implements ToolExecutionStateIdle {
  const _$ToolExecutionStateIdleImpl();

  @override
  String toString() {
    return 'ToolExecutionState.idle()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ToolExecutionStateIdleImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() idle,
    required TResult Function(
            String toolName,
            String toolId,
            Map<String, dynamic>? toolInput,
            DateTime startedAt,
            double progress,
            String status,
            String? filePath,
            String? statusMessage)
        executing,
    required TResult Function(
            String toolName, String toolId, String? result, bool? isError)
        completed,
  }) {
    return idle();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? idle,
    TResult? Function(
            String toolName,
            String toolId,
            Map<String, dynamic>? toolInput,
            DateTime startedAt,
            double progress,
            String status,
            String? filePath,
            String? statusMessage)?
        executing,
    TResult? Function(
            String toolName, String toolId, String? result, bool? isError)?
        completed,
  }) {
    return idle?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? idle,
    TResult Function(
            String toolName,
            String toolId,
            Map<String, dynamic>? toolInput,
            DateTime startedAt,
            double progress,
            String status,
            String? filePath,
            String? statusMessage)?
        executing,
    TResult Function(
            String toolName, String toolId, String? result, bool? isError)?
        completed,
    required TResult orElse(),
  }) {
    if (idle != null) {
      return idle();
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(ToolExecutionStateIdle value) idle,
    required TResult Function(ToolExecutionStateExecuting value) executing,
    required TResult Function(ToolExecutionStateCompleted value) completed,
  }) {
    return idle(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(ToolExecutionStateIdle value)? idle,
    TResult? Function(ToolExecutionStateExecuting value)? executing,
    TResult? Function(ToolExecutionStateCompleted value)? completed,
  }) {
    return idle?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(ToolExecutionStateIdle value)? idle,
    TResult Function(ToolExecutionStateExecuting value)? executing,
    TResult Function(ToolExecutionStateCompleted value)? completed,
    required TResult orElse(),
  }) {
    if (idle != null) {
      return idle(this);
    }
    return orElse();
  }
}

abstract class ToolExecutionStateIdle implements ToolExecutionState {
  const factory ToolExecutionStateIdle() = _$ToolExecutionStateIdleImpl;
}

/// @nodoc
abstract class _$$ToolExecutionStateExecutingImplCopyWith<$Res> {
  factory _$$ToolExecutionStateExecutingImplCopyWith(
          _$ToolExecutionStateExecutingImpl value,
          $Res Function(_$ToolExecutionStateExecutingImpl) then) =
      __$$ToolExecutionStateExecutingImplCopyWithImpl<$Res>;
  @useResult
  $Res call(
      {String toolName,
      String toolId,
      Map<String, dynamic>? toolInput,
      DateTime startedAt,
      double progress,
      String status,
      String? filePath,
      String? statusMessage});
}

/// @nodoc
class __$$ToolExecutionStateExecutingImplCopyWithImpl<$Res>
    extends _$ToolExecutionStateCopyWithImpl<$Res,
        _$ToolExecutionStateExecutingImpl>
    implements _$$ToolExecutionStateExecutingImplCopyWith<$Res> {
  __$$ToolExecutionStateExecutingImplCopyWithImpl(
      _$ToolExecutionStateExecutingImpl _value,
      $Res Function(_$ToolExecutionStateExecutingImpl) _then)
      : super(_value, _then);

  /// Create a copy of ToolExecutionState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? toolName = null,
    Object? toolId = null,
    Object? toolInput = freezed,
    Object? startedAt = null,
    Object? progress = null,
    Object? status = null,
    Object? filePath = freezed,
    Object? statusMessage = freezed,
  }) {
    return _then(_$ToolExecutionStateExecutingImpl(
      toolName: null == toolName
          ? _value.toolName
          : toolName // ignore: cast_nullable_to_non_nullable
              as String,
      toolId: null == toolId
          ? _value.toolId
          : toolId // ignore: cast_nullable_to_non_nullable
              as String,
      toolInput: freezed == toolInput
          ? _value._toolInput
          : toolInput // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      startedAt: null == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      progress: null == progress
          ? _value.progress
          : progress // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      filePath: freezed == filePath
          ? _value.filePath
          : filePath // ignore: cast_nullable_to_non_nullable
              as String?,
      statusMessage: freezed == statusMessage
          ? _value.statusMessage
          : statusMessage // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc

class _$ToolExecutionStateExecutingImpl implements ToolExecutionStateExecuting {
  const _$ToolExecutionStateExecutingImpl(
      {required this.toolName,
      required this.toolId,
      final Map<String, dynamic>? toolInput,
      required this.startedAt,
      this.progress = 0.0,
      this.status = 'executing',
      this.filePath,
      this.statusMessage})
      : _toolInput = toolInput;

  @override
  final String toolName;
  @override
  final String toolId;
  final Map<String, dynamic>? _toolInput;
  @override
  Map<String, dynamic>? get toolInput {
    final value = _toolInput;
    if (value == null) return null;
    if (_toolInput is EqualUnmodifiableMapView) return _toolInput;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final DateTime startedAt;
  @override
  @JsonKey()
  final double progress;
// 0.0 - 1.0
  @override
  @JsonKey()
  final String status;
// executing, writing, etc.
  @override
  final String? filePath;
// 对于 Write 工具，显示文件路径
  @override
  final String? statusMessage;

  @override
  String toString() {
    return 'ToolExecutionState.executing(toolName: $toolName, toolId: $toolId, toolInput: $toolInput, startedAt: $startedAt, progress: $progress, status: $status, filePath: $filePath, statusMessage: $statusMessage)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ToolExecutionStateExecutingImpl &&
            (identical(other.toolName, toolName) ||
                other.toolName == toolName) &&
            (identical(other.toolId, toolId) || other.toolId == toolId) &&
            const DeepCollectionEquality()
                .equals(other._toolInput, _toolInput) &&
            (identical(other.startedAt, startedAt) ||
                other.startedAt == startedAt) &&
            (identical(other.progress, progress) ||
                other.progress == progress) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.filePath, filePath) ||
                other.filePath == filePath) &&
            (identical(other.statusMessage, statusMessage) ||
                other.statusMessage == statusMessage));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      toolName,
      toolId,
      const DeepCollectionEquality().hash(_toolInput),
      startedAt,
      progress,
      status,
      filePath,
      statusMessage);

  /// Create a copy of ToolExecutionState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ToolExecutionStateExecutingImplCopyWith<_$ToolExecutionStateExecutingImpl>
      get copyWith => __$$ToolExecutionStateExecutingImplCopyWithImpl<
          _$ToolExecutionStateExecutingImpl>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() idle,
    required TResult Function(
            String toolName,
            String toolId,
            Map<String, dynamic>? toolInput,
            DateTime startedAt,
            double progress,
            String status,
            String? filePath,
            String? statusMessage)
        executing,
    required TResult Function(
            String toolName, String toolId, String? result, bool? isError)
        completed,
  }) {
    return executing(toolName, toolId, toolInput, startedAt, progress, status,
        filePath, statusMessage);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? idle,
    TResult? Function(
            String toolName,
            String toolId,
            Map<String, dynamic>? toolInput,
            DateTime startedAt,
            double progress,
            String status,
            String? filePath,
            String? statusMessage)?
        executing,
    TResult? Function(
            String toolName, String toolId, String? result, bool? isError)?
        completed,
  }) {
    return executing?.call(toolName, toolId, toolInput, startedAt, progress,
        status, filePath, statusMessage);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? idle,
    TResult Function(
            String toolName,
            String toolId,
            Map<String, dynamic>? toolInput,
            DateTime startedAt,
            double progress,
            String status,
            String? filePath,
            String? statusMessage)?
        executing,
    TResult Function(
            String toolName, String toolId, String? result, bool? isError)?
        completed,
    required TResult orElse(),
  }) {
    if (executing != null) {
      return executing(toolName, toolId, toolInput, startedAt, progress, status,
          filePath, statusMessage);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(ToolExecutionStateIdle value) idle,
    required TResult Function(ToolExecutionStateExecuting value) executing,
    required TResult Function(ToolExecutionStateCompleted value) completed,
  }) {
    return executing(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(ToolExecutionStateIdle value)? idle,
    TResult? Function(ToolExecutionStateExecuting value)? executing,
    TResult? Function(ToolExecutionStateCompleted value)? completed,
  }) {
    return executing?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(ToolExecutionStateIdle value)? idle,
    TResult Function(ToolExecutionStateExecuting value)? executing,
    TResult Function(ToolExecutionStateCompleted value)? completed,
    required TResult orElse(),
  }) {
    if (executing != null) {
      return executing(this);
    }
    return orElse();
  }
}

abstract class ToolExecutionStateExecuting implements ToolExecutionState {
  const factory ToolExecutionStateExecuting(
      {required final String toolName,
      required final String toolId,
      final Map<String, dynamic>? toolInput,
      required final DateTime startedAt,
      final double progress,
      final String status,
      final String? filePath,
      final String? statusMessage}) = _$ToolExecutionStateExecutingImpl;

  String get toolName;
  String get toolId;
  Map<String, dynamic>? get toolInput;
  DateTime get startedAt;
  double get progress; // 0.0 - 1.0
  String get status; // executing, writing, etc.
  String? get filePath; // 对于 Write 工具，显示文件路径
  String? get statusMessage;

  /// Create a copy of ToolExecutionState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ToolExecutionStateExecutingImplCopyWith<_$ToolExecutionStateExecutingImpl>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class _$$ToolExecutionStateCompletedImplCopyWith<$Res> {
  factory _$$ToolExecutionStateCompletedImplCopyWith(
          _$ToolExecutionStateCompletedImpl value,
          $Res Function(_$ToolExecutionStateCompletedImpl) then) =
      __$$ToolExecutionStateCompletedImplCopyWithImpl<$Res>;
  @useResult
  $Res call({String toolName, String toolId, String? result, bool? isError});
}

/// @nodoc
class __$$ToolExecutionStateCompletedImplCopyWithImpl<$Res>
    extends _$ToolExecutionStateCopyWithImpl<$Res,
        _$ToolExecutionStateCompletedImpl>
    implements _$$ToolExecutionStateCompletedImplCopyWith<$Res> {
  __$$ToolExecutionStateCompletedImplCopyWithImpl(
      _$ToolExecutionStateCompletedImpl _value,
      $Res Function(_$ToolExecutionStateCompletedImpl) _then)
      : super(_value, _then);

  /// Create a copy of ToolExecutionState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? toolName = null,
    Object? toolId = null,
    Object? result = freezed,
    Object? isError = freezed,
  }) {
    return _then(_$ToolExecutionStateCompletedImpl(
      toolName: null == toolName
          ? _value.toolName
          : toolName // ignore: cast_nullable_to_non_nullable
              as String,
      toolId: null == toolId
          ? _value.toolId
          : toolId // ignore: cast_nullable_to_non_nullable
              as String,
      result: freezed == result
          ? _value.result
          : result // ignore: cast_nullable_to_non_nullable
              as String?,
      isError: freezed == isError
          ? _value.isError
          : isError // ignore: cast_nullable_to_non_nullable
              as bool?,
    ));
  }
}

/// @nodoc

class _$ToolExecutionStateCompletedImpl implements ToolExecutionStateCompleted {
  const _$ToolExecutionStateCompletedImpl(
      {required this.toolName,
      required this.toolId,
      this.result,
      this.isError});

  @override
  final String toolName;
  @override
  final String toolId;
  @override
  final String? result;
  @override
  final bool? isError;

  @override
  String toString() {
    return 'ToolExecutionState.completed(toolName: $toolName, toolId: $toolId, result: $result, isError: $isError)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ToolExecutionStateCompletedImpl &&
            (identical(other.toolName, toolName) ||
                other.toolName == toolName) &&
            (identical(other.toolId, toolId) || other.toolId == toolId) &&
            (identical(other.result, result) || other.result == result) &&
            (identical(other.isError, isError) || other.isError == isError));
  }

  @override
  int get hashCode =>
      Object.hash(runtimeType, toolName, toolId, result, isError);

  /// Create a copy of ToolExecutionState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ToolExecutionStateCompletedImplCopyWith<_$ToolExecutionStateCompletedImpl>
      get copyWith => __$$ToolExecutionStateCompletedImplCopyWithImpl<
          _$ToolExecutionStateCompletedImpl>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() idle,
    required TResult Function(
            String toolName,
            String toolId,
            Map<String, dynamic>? toolInput,
            DateTime startedAt,
            double progress,
            String status,
            String? filePath,
            String? statusMessage)
        executing,
    required TResult Function(
            String toolName, String toolId, String? result, bool? isError)
        completed,
  }) {
    return completed(toolName, toolId, result, isError);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? idle,
    TResult? Function(
            String toolName,
            String toolId,
            Map<String, dynamic>? toolInput,
            DateTime startedAt,
            double progress,
            String status,
            String? filePath,
            String? statusMessage)?
        executing,
    TResult? Function(
            String toolName, String toolId, String? result, bool? isError)?
        completed,
  }) {
    return completed?.call(toolName, toolId, result, isError);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? idle,
    TResult Function(
            String toolName,
            String toolId,
            Map<String, dynamic>? toolInput,
            DateTime startedAt,
            double progress,
            String status,
            String? filePath,
            String? statusMessage)?
        executing,
    TResult Function(
            String toolName, String toolId, String? result, bool? isError)?
        completed,
    required TResult orElse(),
  }) {
    if (completed != null) {
      return completed(toolName, toolId, result, isError);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(ToolExecutionStateIdle value) idle,
    required TResult Function(ToolExecutionStateExecuting value) executing,
    required TResult Function(ToolExecutionStateCompleted value) completed,
  }) {
    return completed(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(ToolExecutionStateIdle value)? idle,
    TResult? Function(ToolExecutionStateExecuting value)? executing,
    TResult? Function(ToolExecutionStateCompleted value)? completed,
  }) {
    return completed?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(ToolExecutionStateIdle value)? idle,
    TResult Function(ToolExecutionStateExecuting value)? executing,
    TResult Function(ToolExecutionStateCompleted value)? completed,
    required TResult orElse(),
  }) {
    if (completed != null) {
      return completed(this);
    }
    return orElse();
  }
}

abstract class ToolExecutionStateCompleted implements ToolExecutionState {
  const factory ToolExecutionStateCompleted(
      {required final String toolName,
      required final String toolId,
      final String? result,
      final bool? isError}) = _$ToolExecutionStateCompletedImpl;

  String get toolName;
  String get toolId;
  String? get result;
  bool? get isError;

  /// Create a copy of ToolExecutionState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ToolExecutionStateCompletedImplCopyWith<_$ToolExecutionStateCompletedImpl>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$StreamingState {
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() idle,
    required TResult Function(DateTime startedAt) waiting,
    required TResult Function(String content, DateTime startedAt) streaming,
    required TResult Function() completed,
    required TResult Function(String message) error,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? idle,
    TResult? Function(DateTime startedAt)? waiting,
    TResult? Function(String content, DateTime startedAt)? streaming,
    TResult? Function()? completed,
    TResult? Function(String message)? error,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? idle,
    TResult Function(DateTime startedAt)? waiting,
    TResult Function(String content, DateTime startedAt)? streaming,
    TResult Function()? completed,
    TResult Function(String message)? error,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(StreamingStateIdle value) idle,
    required TResult Function(StreamingStateWaiting value) waiting,
    required TResult Function(StreamingStateStreaming value) streaming,
    required TResult Function(StreamingStateCompleted value) completed,
    required TResult Function(StreamingStateError value) error,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(StreamingStateIdle value)? idle,
    TResult? Function(StreamingStateWaiting value)? waiting,
    TResult? Function(StreamingStateStreaming value)? streaming,
    TResult? Function(StreamingStateCompleted value)? completed,
    TResult? Function(StreamingStateError value)? error,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(StreamingStateIdle value)? idle,
    TResult Function(StreamingStateWaiting value)? waiting,
    TResult Function(StreamingStateStreaming value)? streaming,
    TResult Function(StreamingStateCompleted value)? completed,
    TResult Function(StreamingStateError value)? error,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $StreamingStateCopyWith<$Res> {
  factory $StreamingStateCopyWith(
          StreamingState value, $Res Function(StreamingState) then) =
      _$StreamingStateCopyWithImpl<$Res, StreamingState>;
}

/// @nodoc
class _$StreamingStateCopyWithImpl<$Res, $Val extends StreamingState>
    implements $StreamingStateCopyWith<$Res> {
  _$StreamingStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of StreamingState
  /// with the given fields replaced by the non-null parameter values.
}

/// @nodoc
abstract class _$$StreamingStateIdleImplCopyWith<$Res> {
  factory _$$StreamingStateIdleImplCopyWith(_$StreamingStateIdleImpl value,
          $Res Function(_$StreamingStateIdleImpl) then) =
      __$$StreamingStateIdleImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$StreamingStateIdleImplCopyWithImpl<$Res>
    extends _$StreamingStateCopyWithImpl<$Res, _$StreamingStateIdleImpl>
    implements _$$StreamingStateIdleImplCopyWith<$Res> {
  __$$StreamingStateIdleImplCopyWithImpl(_$StreamingStateIdleImpl _value,
      $Res Function(_$StreamingStateIdleImpl) _then)
      : super(_value, _then);

  /// Create a copy of StreamingState
  /// with the given fields replaced by the non-null parameter values.
}

/// @nodoc

class _$StreamingStateIdleImpl implements StreamingStateIdle {
  const _$StreamingStateIdleImpl();

  @override
  String toString() {
    return 'StreamingState.idle()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is _$StreamingStateIdleImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() idle,
    required TResult Function(DateTime startedAt) waiting,
    required TResult Function(String content, DateTime startedAt) streaming,
    required TResult Function() completed,
    required TResult Function(String message) error,
  }) {
    return idle();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? idle,
    TResult? Function(DateTime startedAt)? waiting,
    TResult? Function(String content, DateTime startedAt)? streaming,
    TResult? Function()? completed,
    TResult? Function(String message)? error,
  }) {
    return idle?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? idle,
    TResult Function(DateTime startedAt)? waiting,
    TResult Function(String content, DateTime startedAt)? streaming,
    TResult Function()? completed,
    TResult Function(String message)? error,
    required TResult orElse(),
  }) {
    if (idle != null) {
      return idle();
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(StreamingStateIdle value) idle,
    required TResult Function(StreamingStateWaiting value) waiting,
    required TResult Function(StreamingStateStreaming value) streaming,
    required TResult Function(StreamingStateCompleted value) completed,
    required TResult Function(StreamingStateError value) error,
  }) {
    return idle(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(StreamingStateIdle value)? idle,
    TResult? Function(StreamingStateWaiting value)? waiting,
    TResult? Function(StreamingStateStreaming value)? streaming,
    TResult? Function(StreamingStateCompleted value)? completed,
    TResult? Function(StreamingStateError value)? error,
  }) {
    return idle?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(StreamingStateIdle value)? idle,
    TResult Function(StreamingStateWaiting value)? waiting,
    TResult Function(StreamingStateStreaming value)? streaming,
    TResult Function(StreamingStateCompleted value)? completed,
    TResult Function(StreamingStateError value)? error,
    required TResult orElse(),
  }) {
    if (idle != null) {
      return idle(this);
    }
    return orElse();
  }
}

abstract class StreamingStateIdle implements StreamingState {
  const factory StreamingStateIdle() = _$StreamingStateIdleImpl;
}

/// @nodoc
abstract class _$$StreamingStateWaitingImplCopyWith<$Res> {
  factory _$$StreamingStateWaitingImplCopyWith(
          _$StreamingStateWaitingImpl value,
          $Res Function(_$StreamingStateWaitingImpl) then) =
      __$$StreamingStateWaitingImplCopyWithImpl<$Res>;
  @useResult
  $Res call({DateTime startedAt});
}

/// @nodoc
class __$$StreamingStateWaitingImplCopyWithImpl<$Res>
    extends _$StreamingStateCopyWithImpl<$Res, _$StreamingStateWaitingImpl>
    implements _$$StreamingStateWaitingImplCopyWith<$Res> {
  __$$StreamingStateWaitingImplCopyWithImpl(_$StreamingStateWaitingImpl _value,
      $Res Function(_$StreamingStateWaitingImpl) _then)
      : super(_value, _then);

  /// Create a copy of StreamingState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? startedAt = null,
  }) {
    return _then(_$StreamingStateWaitingImpl(
      startedAt: null == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc

class _$StreamingStateWaitingImpl implements StreamingStateWaiting {
  const _$StreamingStateWaitingImpl({required this.startedAt});

  @override
  final DateTime startedAt;

  @override
  String toString() {
    return 'StreamingState.waiting(startedAt: $startedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$StreamingStateWaitingImpl &&
            (identical(other.startedAt, startedAt) ||
                other.startedAt == startedAt));
  }

  @override
  int get hashCode => Object.hash(runtimeType, startedAt);

  /// Create a copy of StreamingState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$StreamingStateWaitingImplCopyWith<_$StreamingStateWaitingImpl>
      get copyWith => __$$StreamingStateWaitingImplCopyWithImpl<
          _$StreamingStateWaitingImpl>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() idle,
    required TResult Function(DateTime startedAt) waiting,
    required TResult Function(String content, DateTime startedAt) streaming,
    required TResult Function() completed,
    required TResult Function(String message) error,
  }) {
    return waiting(startedAt);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? idle,
    TResult? Function(DateTime startedAt)? waiting,
    TResult? Function(String content, DateTime startedAt)? streaming,
    TResult? Function()? completed,
    TResult? Function(String message)? error,
  }) {
    return waiting?.call(startedAt);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? idle,
    TResult Function(DateTime startedAt)? waiting,
    TResult Function(String content, DateTime startedAt)? streaming,
    TResult Function()? completed,
    TResult Function(String message)? error,
    required TResult orElse(),
  }) {
    if (waiting != null) {
      return waiting(startedAt);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(StreamingStateIdle value) idle,
    required TResult Function(StreamingStateWaiting value) waiting,
    required TResult Function(StreamingStateStreaming value) streaming,
    required TResult Function(StreamingStateCompleted value) completed,
    required TResult Function(StreamingStateError value) error,
  }) {
    return waiting(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(StreamingStateIdle value)? idle,
    TResult? Function(StreamingStateWaiting value)? waiting,
    TResult? Function(StreamingStateStreaming value)? streaming,
    TResult? Function(StreamingStateCompleted value)? completed,
    TResult? Function(StreamingStateError value)? error,
  }) {
    return waiting?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(StreamingStateIdle value)? idle,
    TResult Function(StreamingStateWaiting value)? waiting,
    TResult Function(StreamingStateStreaming value)? streaming,
    TResult Function(StreamingStateCompleted value)? completed,
    TResult Function(StreamingStateError value)? error,
    required TResult orElse(),
  }) {
    if (waiting != null) {
      return waiting(this);
    }
    return orElse();
  }
}

abstract class StreamingStateWaiting implements StreamingState {
  const factory StreamingStateWaiting({required final DateTime startedAt}) =
      _$StreamingStateWaitingImpl;

  DateTime get startedAt;

  /// Create a copy of StreamingState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$StreamingStateWaitingImplCopyWith<_$StreamingStateWaitingImpl>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class _$$StreamingStateStreamingImplCopyWith<$Res> {
  factory _$$StreamingStateStreamingImplCopyWith(
          _$StreamingStateStreamingImpl value,
          $Res Function(_$StreamingStateStreamingImpl) then) =
      __$$StreamingStateStreamingImplCopyWithImpl<$Res>;
  @useResult
  $Res call({String content, DateTime startedAt});
}

/// @nodoc
class __$$StreamingStateStreamingImplCopyWithImpl<$Res>
    extends _$StreamingStateCopyWithImpl<$Res, _$StreamingStateStreamingImpl>
    implements _$$StreamingStateStreamingImplCopyWith<$Res> {
  __$$StreamingStateStreamingImplCopyWithImpl(
      _$StreamingStateStreamingImpl _value,
      $Res Function(_$StreamingStateStreamingImpl) _then)
      : super(_value, _then);

  /// Create a copy of StreamingState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? content = null,
    Object? startedAt = null,
  }) {
    return _then(_$StreamingStateStreamingImpl(
      content: null == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String,
      startedAt: null == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc

class _$StreamingStateStreamingImpl implements StreamingStateStreaming {
  const _$StreamingStateStreamingImpl(
      {required this.content, required this.startedAt});

  @override
  final String content;
  @override
  final DateTime startedAt;

  @override
  String toString() {
    return 'StreamingState.streaming(content: $content, startedAt: $startedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$StreamingStateStreamingImpl &&
            (identical(other.content, content) || other.content == content) &&
            (identical(other.startedAt, startedAt) ||
                other.startedAt == startedAt));
  }

  @override
  int get hashCode => Object.hash(runtimeType, content, startedAt);

  /// Create a copy of StreamingState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$StreamingStateStreamingImplCopyWith<_$StreamingStateStreamingImpl>
      get copyWith => __$$StreamingStateStreamingImplCopyWithImpl<
          _$StreamingStateStreamingImpl>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() idle,
    required TResult Function(DateTime startedAt) waiting,
    required TResult Function(String content, DateTime startedAt) streaming,
    required TResult Function() completed,
    required TResult Function(String message) error,
  }) {
    return streaming(content, startedAt);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? idle,
    TResult? Function(DateTime startedAt)? waiting,
    TResult? Function(String content, DateTime startedAt)? streaming,
    TResult? Function()? completed,
    TResult? Function(String message)? error,
  }) {
    return streaming?.call(content, startedAt);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? idle,
    TResult Function(DateTime startedAt)? waiting,
    TResult Function(String content, DateTime startedAt)? streaming,
    TResult Function()? completed,
    TResult Function(String message)? error,
    required TResult orElse(),
  }) {
    if (streaming != null) {
      return streaming(content, startedAt);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(StreamingStateIdle value) idle,
    required TResult Function(StreamingStateWaiting value) waiting,
    required TResult Function(StreamingStateStreaming value) streaming,
    required TResult Function(StreamingStateCompleted value) completed,
    required TResult Function(StreamingStateError value) error,
  }) {
    return streaming(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(StreamingStateIdle value)? idle,
    TResult? Function(StreamingStateWaiting value)? waiting,
    TResult? Function(StreamingStateStreaming value)? streaming,
    TResult? Function(StreamingStateCompleted value)? completed,
    TResult? Function(StreamingStateError value)? error,
  }) {
    return streaming?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(StreamingStateIdle value)? idle,
    TResult Function(StreamingStateWaiting value)? waiting,
    TResult Function(StreamingStateStreaming value)? streaming,
    TResult Function(StreamingStateCompleted value)? completed,
    TResult Function(StreamingStateError value)? error,
    required TResult orElse(),
  }) {
    if (streaming != null) {
      return streaming(this);
    }
    return orElse();
  }
}

abstract class StreamingStateStreaming implements StreamingState {
  const factory StreamingStateStreaming(
      {required final String content,
      required final DateTime startedAt}) = _$StreamingStateStreamingImpl;

  String get content;
  DateTime get startedAt;

  /// Create a copy of StreamingState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$StreamingStateStreamingImplCopyWith<_$StreamingStateStreamingImpl>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class _$$StreamingStateCompletedImplCopyWith<$Res> {
  factory _$$StreamingStateCompletedImplCopyWith(
          _$StreamingStateCompletedImpl value,
          $Res Function(_$StreamingStateCompletedImpl) then) =
      __$$StreamingStateCompletedImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$StreamingStateCompletedImplCopyWithImpl<$Res>
    extends _$StreamingStateCopyWithImpl<$Res, _$StreamingStateCompletedImpl>
    implements _$$StreamingStateCompletedImplCopyWith<$Res> {
  __$$StreamingStateCompletedImplCopyWithImpl(
      _$StreamingStateCompletedImpl _value,
      $Res Function(_$StreamingStateCompletedImpl) _then)
      : super(_value, _then);

  /// Create a copy of StreamingState
  /// with the given fields replaced by the non-null parameter values.
}

/// @nodoc

class _$StreamingStateCompletedImpl implements StreamingStateCompleted {
  const _$StreamingStateCompletedImpl();

  @override
  String toString() {
    return 'StreamingState.completed()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$StreamingStateCompletedImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() idle,
    required TResult Function(DateTime startedAt) waiting,
    required TResult Function(String content, DateTime startedAt) streaming,
    required TResult Function() completed,
    required TResult Function(String message) error,
  }) {
    return completed();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? idle,
    TResult? Function(DateTime startedAt)? waiting,
    TResult? Function(String content, DateTime startedAt)? streaming,
    TResult? Function()? completed,
    TResult? Function(String message)? error,
  }) {
    return completed?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? idle,
    TResult Function(DateTime startedAt)? waiting,
    TResult Function(String content, DateTime startedAt)? streaming,
    TResult Function()? completed,
    TResult Function(String message)? error,
    required TResult orElse(),
  }) {
    if (completed != null) {
      return completed();
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(StreamingStateIdle value) idle,
    required TResult Function(StreamingStateWaiting value) waiting,
    required TResult Function(StreamingStateStreaming value) streaming,
    required TResult Function(StreamingStateCompleted value) completed,
    required TResult Function(StreamingStateError value) error,
  }) {
    return completed(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(StreamingStateIdle value)? idle,
    TResult? Function(StreamingStateWaiting value)? waiting,
    TResult? Function(StreamingStateStreaming value)? streaming,
    TResult? Function(StreamingStateCompleted value)? completed,
    TResult? Function(StreamingStateError value)? error,
  }) {
    return completed?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(StreamingStateIdle value)? idle,
    TResult Function(StreamingStateWaiting value)? waiting,
    TResult Function(StreamingStateStreaming value)? streaming,
    TResult Function(StreamingStateCompleted value)? completed,
    TResult Function(StreamingStateError value)? error,
    required TResult orElse(),
  }) {
    if (completed != null) {
      return completed(this);
    }
    return orElse();
  }
}

abstract class StreamingStateCompleted implements StreamingState {
  const factory StreamingStateCompleted() = _$StreamingStateCompletedImpl;
}

/// @nodoc
abstract class _$$StreamingStateErrorImplCopyWith<$Res> {
  factory _$$StreamingStateErrorImplCopyWith(_$StreamingStateErrorImpl value,
          $Res Function(_$StreamingStateErrorImpl) then) =
      __$$StreamingStateErrorImplCopyWithImpl<$Res>;
  @useResult
  $Res call({String message});
}

/// @nodoc
class __$$StreamingStateErrorImplCopyWithImpl<$Res>
    extends _$StreamingStateCopyWithImpl<$Res, _$StreamingStateErrorImpl>
    implements _$$StreamingStateErrorImplCopyWith<$Res> {
  __$$StreamingStateErrorImplCopyWithImpl(_$StreamingStateErrorImpl _value,
      $Res Function(_$StreamingStateErrorImpl) _then)
      : super(_value, _then);

  /// Create a copy of StreamingState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? message = null,
  }) {
    return _then(_$StreamingStateErrorImpl(
      null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc

class _$StreamingStateErrorImpl implements StreamingStateError {
  const _$StreamingStateErrorImpl(this.message);

  @override
  final String message;

  @override
  String toString() {
    return 'StreamingState.error(message: $message)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$StreamingStateErrorImpl &&
            (identical(other.message, message) || other.message == message));
  }

  @override
  int get hashCode => Object.hash(runtimeType, message);

  /// Create a copy of StreamingState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$StreamingStateErrorImplCopyWith<_$StreamingStateErrorImpl> get copyWith =>
      __$$StreamingStateErrorImplCopyWithImpl<_$StreamingStateErrorImpl>(
          this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() idle,
    required TResult Function(DateTime startedAt) waiting,
    required TResult Function(String content, DateTime startedAt) streaming,
    required TResult Function() completed,
    required TResult Function(String message) error,
  }) {
    return error(message);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? idle,
    TResult? Function(DateTime startedAt)? waiting,
    TResult? Function(String content, DateTime startedAt)? streaming,
    TResult? Function()? completed,
    TResult? Function(String message)? error,
  }) {
    return error?.call(message);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? idle,
    TResult Function(DateTime startedAt)? waiting,
    TResult Function(String content, DateTime startedAt)? streaming,
    TResult Function()? completed,
    TResult Function(String message)? error,
    required TResult orElse(),
  }) {
    if (error != null) {
      return error(message);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(StreamingStateIdle value) idle,
    required TResult Function(StreamingStateWaiting value) waiting,
    required TResult Function(StreamingStateStreaming value) streaming,
    required TResult Function(StreamingStateCompleted value) completed,
    required TResult Function(StreamingStateError value) error,
  }) {
    return error(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(StreamingStateIdle value)? idle,
    TResult? Function(StreamingStateWaiting value)? waiting,
    TResult? Function(StreamingStateStreaming value)? streaming,
    TResult? Function(StreamingStateCompleted value)? completed,
    TResult? Function(StreamingStateError value)? error,
  }) {
    return error?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(StreamingStateIdle value)? idle,
    TResult Function(StreamingStateWaiting value)? waiting,
    TResult Function(StreamingStateStreaming value)? streaming,
    TResult Function(StreamingStateCompleted value)? completed,
    TResult Function(StreamingStateError value)? error,
    required TResult orElse(),
  }) {
    if (error != null) {
      return error(this);
    }
    return orElse();
  }
}

abstract class StreamingStateError implements StreamingState {
  const factory StreamingStateError(final String message) =
      _$StreamingStateErrorImpl;

  String get message;

  /// Create a copy of StreamingState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$StreamingStateErrorImplCopyWith<_$StreamingStateErrorImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$WsConnectionState {
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() disconnected,
    required TResult Function() connecting,
    required TResult Function() connected,
    required TResult Function(int attempt) reconnecting,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? disconnected,
    TResult? Function()? connecting,
    TResult? Function()? connected,
    TResult? Function(int attempt)? reconnecting,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? disconnected,
    TResult Function()? connecting,
    TResult Function()? connected,
    TResult Function(int attempt)? reconnecting,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(WsConnectionStateDisconnected value) disconnected,
    required TResult Function(WsConnectionStateConnecting value) connecting,
    required TResult Function(WsConnectionStateConnected value) connected,
    required TResult Function(WsConnectionStateReconnecting value) reconnecting,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(WsConnectionStateDisconnected value)? disconnected,
    TResult? Function(WsConnectionStateConnecting value)? connecting,
    TResult? Function(WsConnectionStateConnected value)? connected,
    TResult? Function(WsConnectionStateReconnecting value)? reconnecting,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(WsConnectionStateDisconnected value)? disconnected,
    TResult Function(WsConnectionStateConnecting value)? connecting,
    TResult Function(WsConnectionStateConnected value)? connected,
    TResult Function(WsConnectionStateReconnecting value)? reconnecting,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WsConnectionStateCopyWith<$Res> {
  factory $WsConnectionStateCopyWith(
          WsConnectionState value, $Res Function(WsConnectionState) then) =
      _$WsConnectionStateCopyWithImpl<$Res, WsConnectionState>;
}

/// @nodoc
class _$WsConnectionStateCopyWithImpl<$Res, $Val extends WsConnectionState>
    implements $WsConnectionStateCopyWith<$Res> {
  _$WsConnectionStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of WsConnectionState
  /// with the given fields replaced by the non-null parameter values.
}

/// @nodoc
abstract class _$$WsConnectionStateDisconnectedImplCopyWith<$Res> {
  factory _$$WsConnectionStateDisconnectedImplCopyWith(
          _$WsConnectionStateDisconnectedImpl value,
          $Res Function(_$WsConnectionStateDisconnectedImpl) then) =
      __$$WsConnectionStateDisconnectedImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$WsConnectionStateDisconnectedImplCopyWithImpl<$Res>
    extends _$WsConnectionStateCopyWithImpl<$Res,
        _$WsConnectionStateDisconnectedImpl>
    implements _$$WsConnectionStateDisconnectedImplCopyWith<$Res> {
  __$$WsConnectionStateDisconnectedImplCopyWithImpl(
      _$WsConnectionStateDisconnectedImpl _value,
      $Res Function(_$WsConnectionStateDisconnectedImpl) _then)
      : super(_value, _then);

  /// Create a copy of WsConnectionState
  /// with the given fields replaced by the non-null parameter values.
}

/// @nodoc

class _$WsConnectionStateDisconnectedImpl
    implements WsConnectionStateDisconnected {
  const _$WsConnectionStateDisconnectedImpl();

  @override
  String toString() {
    return 'WsConnectionState.disconnected()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WsConnectionStateDisconnectedImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() disconnected,
    required TResult Function() connecting,
    required TResult Function() connected,
    required TResult Function(int attempt) reconnecting,
  }) {
    return disconnected();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? disconnected,
    TResult? Function()? connecting,
    TResult? Function()? connected,
    TResult? Function(int attempt)? reconnecting,
  }) {
    return disconnected?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? disconnected,
    TResult Function()? connecting,
    TResult Function()? connected,
    TResult Function(int attempt)? reconnecting,
    required TResult orElse(),
  }) {
    if (disconnected != null) {
      return disconnected();
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(WsConnectionStateDisconnected value) disconnected,
    required TResult Function(WsConnectionStateConnecting value) connecting,
    required TResult Function(WsConnectionStateConnected value) connected,
    required TResult Function(WsConnectionStateReconnecting value) reconnecting,
  }) {
    return disconnected(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(WsConnectionStateDisconnected value)? disconnected,
    TResult? Function(WsConnectionStateConnecting value)? connecting,
    TResult? Function(WsConnectionStateConnected value)? connected,
    TResult? Function(WsConnectionStateReconnecting value)? reconnecting,
  }) {
    return disconnected?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(WsConnectionStateDisconnected value)? disconnected,
    TResult Function(WsConnectionStateConnecting value)? connecting,
    TResult Function(WsConnectionStateConnected value)? connected,
    TResult Function(WsConnectionStateReconnecting value)? reconnecting,
    required TResult orElse(),
  }) {
    if (disconnected != null) {
      return disconnected(this);
    }
    return orElse();
  }
}

abstract class WsConnectionStateDisconnected implements WsConnectionState {
  const factory WsConnectionStateDisconnected() =
      _$WsConnectionStateDisconnectedImpl;
}

/// @nodoc
abstract class _$$WsConnectionStateConnectingImplCopyWith<$Res> {
  factory _$$WsConnectionStateConnectingImplCopyWith(
          _$WsConnectionStateConnectingImpl value,
          $Res Function(_$WsConnectionStateConnectingImpl) then) =
      __$$WsConnectionStateConnectingImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$WsConnectionStateConnectingImplCopyWithImpl<$Res>
    extends _$WsConnectionStateCopyWithImpl<$Res,
        _$WsConnectionStateConnectingImpl>
    implements _$$WsConnectionStateConnectingImplCopyWith<$Res> {
  __$$WsConnectionStateConnectingImplCopyWithImpl(
      _$WsConnectionStateConnectingImpl _value,
      $Res Function(_$WsConnectionStateConnectingImpl) _then)
      : super(_value, _then);

  /// Create a copy of WsConnectionState
  /// with the given fields replaced by the non-null parameter values.
}

/// @nodoc

class _$WsConnectionStateConnectingImpl implements WsConnectionStateConnecting {
  const _$WsConnectionStateConnectingImpl();

  @override
  String toString() {
    return 'WsConnectionState.connecting()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WsConnectionStateConnectingImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() disconnected,
    required TResult Function() connecting,
    required TResult Function() connected,
    required TResult Function(int attempt) reconnecting,
  }) {
    return connecting();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? disconnected,
    TResult? Function()? connecting,
    TResult? Function()? connected,
    TResult? Function(int attempt)? reconnecting,
  }) {
    return connecting?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? disconnected,
    TResult Function()? connecting,
    TResult Function()? connected,
    TResult Function(int attempt)? reconnecting,
    required TResult orElse(),
  }) {
    if (connecting != null) {
      return connecting();
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(WsConnectionStateDisconnected value) disconnected,
    required TResult Function(WsConnectionStateConnecting value) connecting,
    required TResult Function(WsConnectionStateConnected value) connected,
    required TResult Function(WsConnectionStateReconnecting value) reconnecting,
  }) {
    return connecting(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(WsConnectionStateDisconnected value)? disconnected,
    TResult? Function(WsConnectionStateConnecting value)? connecting,
    TResult? Function(WsConnectionStateConnected value)? connected,
    TResult? Function(WsConnectionStateReconnecting value)? reconnecting,
  }) {
    return connecting?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(WsConnectionStateDisconnected value)? disconnected,
    TResult Function(WsConnectionStateConnecting value)? connecting,
    TResult Function(WsConnectionStateConnected value)? connected,
    TResult Function(WsConnectionStateReconnecting value)? reconnecting,
    required TResult orElse(),
  }) {
    if (connecting != null) {
      return connecting(this);
    }
    return orElse();
  }
}

abstract class WsConnectionStateConnecting implements WsConnectionState {
  const factory WsConnectionStateConnecting() =
      _$WsConnectionStateConnectingImpl;
}

/// @nodoc
abstract class _$$WsConnectionStateConnectedImplCopyWith<$Res> {
  factory _$$WsConnectionStateConnectedImplCopyWith(
          _$WsConnectionStateConnectedImpl value,
          $Res Function(_$WsConnectionStateConnectedImpl) then) =
      __$$WsConnectionStateConnectedImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$WsConnectionStateConnectedImplCopyWithImpl<$Res>
    extends _$WsConnectionStateCopyWithImpl<$Res,
        _$WsConnectionStateConnectedImpl>
    implements _$$WsConnectionStateConnectedImplCopyWith<$Res> {
  __$$WsConnectionStateConnectedImplCopyWithImpl(
      _$WsConnectionStateConnectedImpl _value,
      $Res Function(_$WsConnectionStateConnectedImpl) _then)
      : super(_value, _then);

  /// Create a copy of WsConnectionState
  /// with the given fields replaced by the non-null parameter values.
}

/// @nodoc

class _$WsConnectionStateConnectedImpl implements WsConnectionStateConnected {
  const _$WsConnectionStateConnectedImpl();

  @override
  String toString() {
    return 'WsConnectionState.connected()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WsConnectionStateConnectedImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() disconnected,
    required TResult Function() connecting,
    required TResult Function() connected,
    required TResult Function(int attempt) reconnecting,
  }) {
    return connected();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? disconnected,
    TResult? Function()? connecting,
    TResult? Function()? connected,
    TResult? Function(int attempt)? reconnecting,
  }) {
    return connected?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? disconnected,
    TResult Function()? connecting,
    TResult Function()? connected,
    TResult Function(int attempt)? reconnecting,
    required TResult orElse(),
  }) {
    if (connected != null) {
      return connected();
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(WsConnectionStateDisconnected value) disconnected,
    required TResult Function(WsConnectionStateConnecting value) connecting,
    required TResult Function(WsConnectionStateConnected value) connected,
    required TResult Function(WsConnectionStateReconnecting value) reconnecting,
  }) {
    return connected(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(WsConnectionStateDisconnected value)? disconnected,
    TResult? Function(WsConnectionStateConnecting value)? connecting,
    TResult? Function(WsConnectionStateConnected value)? connected,
    TResult? Function(WsConnectionStateReconnecting value)? reconnecting,
  }) {
    return connected?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(WsConnectionStateDisconnected value)? disconnected,
    TResult Function(WsConnectionStateConnecting value)? connecting,
    TResult Function(WsConnectionStateConnected value)? connected,
    TResult Function(WsConnectionStateReconnecting value)? reconnecting,
    required TResult orElse(),
  }) {
    if (connected != null) {
      return connected(this);
    }
    return orElse();
  }
}

abstract class WsConnectionStateConnected implements WsConnectionState {
  const factory WsConnectionStateConnected() = _$WsConnectionStateConnectedImpl;
}

/// @nodoc
abstract class _$$WsConnectionStateReconnectingImplCopyWith<$Res> {
  factory _$$WsConnectionStateReconnectingImplCopyWith(
          _$WsConnectionStateReconnectingImpl value,
          $Res Function(_$WsConnectionStateReconnectingImpl) then) =
      __$$WsConnectionStateReconnectingImplCopyWithImpl<$Res>;
  @useResult
  $Res call({int attempt});
}

/// @nodoc
class __$$WsConnectionStateReconnectingImplCopyWithImpl<$Res>
    extends _$WsConnectionStateCopyWithImpl<$Res,
        _$WsConnectionStateReconnectingImpl>
    implements _$$WsConnectionStateReconnectingImplCopyWith<$Res> {
  __$$WsConnectionStateReconnectingImplCopyWithImpl(
      _$WsConnectionStateReconnectingImpl _value,
      $Res Function(_$WsConnectionStateReconnectingImpl) _then)
      : super(_value, _then);

  /// Create a copy of WsConnectionState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? attempt = null,
  }) {
    return _then(_$WsConnectionStateReconnectingImpl(
      attempt: null == attempt
          ? _value.attempt
          : attempt // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc

class _$WsConnectionStateReconnectingImpl
    implements WsConnectionStateReconnecting {
  const _$WsConnectionStateReconnectingImpl({required this.attempt});

  @override
  final int attempt;

  @override
  String toString() {
    return 'WsConnectionState.reconnecting(attempt: $attempt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WsConnectionStateReconnectingImpl &&
            (identical(other.attempt, attempt) || other.attempt == attempt));
  }

  @override
  int get hashCode => Object.hash(runtimeType, attempt);

  /// Create a copy of WsConnectionState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$WsConnectionStateReconnectingImplCopyWith<
          _$WsConnectionStateReconnectingImpl>
      get copyWith => __$$WsConnectionStateReconnectingImplCopyWithImpl<
          _$WsConnectionStateReconnectingImpl>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() disconnected,
    required TResult Function() connecting,
    required TResult Function() connected,
    required TResult Function(int attempt) reconnecting,
  }) {
    return reconnecting(attempt);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? disconnected,
    TResult? Function()? connecting,
    TResult? Function()? connected,
    TResult? Function(int attempt)? reconnecting,
  }) {
    return reconnecting?.call(attempt);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? disconnected,
    TResult Function()? connecting,
    TResult Function()? connected,
    TResult Function(int attempt)? reconnecting,
    required TResult orElse(),
  }) {
    if (reconnecting != null) {
      return reconnecting(attempt);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(WsConnectionStateDisconnected value) disconnected,
    required TResult Function(WsConnectionStateConnecting value) connecting,
    required TResult Function(WsConnectionStateConnected value) connected,
    required TResult Function(WsConnectionStateReconnecting value) reconnecting,
  }) {
    return reconnecting(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(WsConnectionStateDisconnected value)? disconnected,
    TResult? Function(WsConnectionStateConnecting value)? connecting,
    TResult? Function(WsConnectionStateConnected value)? connected,
    TResult? Function(WsConnectionStateReconnecting value)? reconnecting,
  }) {
    return reconnecting?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(WsConnectionStateDisconnected value)? disconnected,
    TResult Function(WsConnectionStateConnecting value)? connecting,
    TResult Function(WsConnectionStateConnected value)? connected,
    TResult Function(WsConnectionStateReconnecting value)? reconnecting,
    required TResult orElse(),
  }) {
    if (reconnecting != null) {
      return reconnecting(this);
    }
    return orElse();
  }
}

abstract class WsConnectionStateReconnecting implements WsConnectionState {
  const factory WsConnectionStateReconnecting({required final int attempt}) =
      _$WsConnectionStateReconnectingImpl;

  int get attempt;

  /// Create a copy of WsConnectionState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$WsConnectionStateReconnectingImplCopyWith<
          _$WsConnectionStateReconnectingImpl>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$ConversationViewState {
  String get conversationId => throw _privateConstructorUsedError;
  List<Message> get messages => throw _privateConstructorUsedError;
  StreamingState get streamingState => throw _privateConstructorUsedError;
  WsConnectionState get connectionState => throw _privateConstructorUsedError;

  /// 工具执行状态（新增：让用户看到工具执行进度）
  ToolExecutionState get toolState => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;
  bool get isLoading => throw _privateConstructorUsedError;

  /// Create a copy of ConversationViewState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConversationViewStateCopyWith<ConversationViewState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConversationViewStateCopyWith<$Res> {
  factory $ConversationViewStateCopyWith(ConversationViewState value,
          $Res Function(ConversationViewState) then) =
      _$ConversationViewStateCopyWithImpl<$Res, ConversationViewState>;
  @useResult
  $Res call(
      {String conversationId,
      List<Message> messages,
      StreamingState streamingState,
      WsConnectionState connectionState,
      ToolExecutionState toolState,
      String? error,
      bool isLoading});

  $StreamingStateCopyWith<$Res> get streamingState;
  $WsConnectionStateCopyWith<$Res> get connectionState;
  $ToolExecutionStateCopyWith<$Res> get toolState;
}

/// @nodoc
class _$ConversationViewStateCopyWithImpl<$Res,
        $Val extends ConversationViewState>
    implements $ConversationViewStateCopyWith<$Res> {
  _$ConversationViewStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConversationViewState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? conversationId = null,
    Object? messages = null,
    Object? streamingState = null,
    Object? connectionState = null,
    Object? toolState = null,
    Object? error = freezed,
    Object? isLoading = null,
  }) {
    return _then(_value.copyWith(
      conversationId: null == conversationId
          ? _value.conversationId
          : conversationId // ignore: cast_nullable_to_non_nullable
              as String,
      messages: null == messages
          ? _value.messages
          : messages // ignore: cast_nullable_to_non_nullable
              as List<Message>,
      streamingState: null == streamingState
          ? _value.streamingState
          : streamingState // ignore: cast_nullable_to_non_nullable
              as StreamingState,
      connectionState: null == connectionState
          ? _value.connectionState
          : connectionState // ignore: cast_nullable_to_non_nullable
              as WsConnectionState,
      toolState: null == toolState
          ? _value.toolState
          : toolState // ignore: cast_nullable_to_non_nullable
              as ToolExecutionState,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }

  /// Create a copy of ConversationViewState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $StreamingStateCopyWith<$Res> get streamingState {
    return $StreamingStateCopyWith<$Res>(_value.streamingState, (value) {
      return _then(_value.copyWith(streamingState: value) as $Val);
    });
  }

  /// Create a copy of ConversationViewState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $WsConnectionStateCopyWith<$Res> get connectionState {
    return $WsConnectionStateCopyWith<$Res>(_value.connectionState, (value) {
      return _then(_value.copyWith(connectionState: value) as $Val);
    });
  }

  /// Create a copy of ConversationViewState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $ToolExecutionStateCopyWith<$Res> get toolState {
    return $ToolExecutionStateCopyWith<$Res>(_value.toolState, (value) {
      return _then(_value.copyWith(toolState: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$ConversationViewStateImplCopyWith<$Res>
    implements $ConversationViewStateCopyWith<$Res> {
  factory _$$ConversationViewStateImplCopyWith(
          _$ConversationViewStateImpl value,
          $Res Function(_$ConversationViewStateImpl) then) =
      __$$ConversationViewStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String conversationId,
      List<Message> messages,
      StreamingState streamingState,
      WsConnectionState connectionState,
      ToolExecutionState toolState,
      String? error,
      bool isLoading});

  @override
  $StreamingStateCopyWith<$Res> get streamingState;
  @override
  $WsConnectionStateCopyWith<$Res> get connectionState;
  @override
  $ToolExecutionStateCopyWith<$Res> get toolState;
}

/// @nodoc
class __$$ConversationViewStateImplCopyWithImpl<$Res>
    extends _$ConversationViewStateCopyWithImpl<$Res,
        _$ConversationViewStateImpl>
    implements _$$ConversationViewStateImplCopyWith<$Res> {
  __$$ConversationViewStateImplCopyWithImpl(_$ConversationViewStateImpl _value,
      $Res Function(_$ConversationViewStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConversationViewState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? conversationId = null,
    Object? messages = null,
    Object? streamingState = null,
    Object? connectionState = null,
    Object? toolState = null,
    Object? error = freezed,
    Object? isLoading = null,
  }) {
    return _then(_$ConversationViewStateImpl(
      conversationId: null == conversationId
          ? _value.conversationId
          : conversationId // ignore: cast_nullable_to_non_nullable
              as String,
      messages: null == messages
          ? _value._messages
          : messages // ignore: cast_nullable_to_non_nullable
              as List<Message>,
      streamingState: null == streamingState
          ? _value.streamingState
          : streamingState // ignore: cast_nullable_to_non_nullable
              as StreamingState,
      connectionState: null == connectionState
          ? _value.connectionState
          : connectionState // ignore: cast_nullable_to_non_nullable
              as WsConnectionState,
      toolState: null == toolState
          ? _value.toolState
          : toolState // ignore: cast_nullable_to_non_nullable
              as ToolExecutionState,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc

class _$ConversationViewStateImpl implements _ConversationViewState {
  const _$ConversationViewStateImpl(
      {required this.conversationId,
      required final List<Message> messages,
      required this.streamingState,
      required this.connectionState,
      this.toolState = const ToolExecutionState.idle(),
      this.error,
      this.isLoading = false})
      : _messages = messages;

  @override
  final String conversationId;
  final List<Message> _messages;
  @override
  List<Message> get messages {
    if (_messages is EqualUnmodifiableListView) return _messages;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_messages);
  }

  @override
  final StreamingState streamingState;
  @override
  final WsConnectionState connectionState;

  /// 工具执行状态（新增：让用户看到工具执行进度）
  @override
  @JsonKey()
  final ToolExecutionState toolState;
  @override
  final String? error;
  @override
  @JsonKey()
  final bool isLoading;

  @override
  String toString() {
    return 'ConversationViewState(conversationId: $conversationId, messages: $messages, streamingState: $streamingState, connectionState: $connectionState, toolState: $toolState, error: $error, isLoading: $isLoading)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConversationViewStateImpl &&
            (identical(other.conversationId, conversationId) ||
                other.conversationId == conversationId) &&
            const DeepCollectionEquality().equals(other._messages, _messages) &&
            (identical(other.streamingState, streamingState) ||
                other.streamingState == streamingState) &&
            (identical(other.connectionState, connectionState) ||
                other.connectionState == connectionState) &&
            (identical(other.toolState, toolState) ||
                other.toolState == toolState) &&
            (identical(other.error, error) || other.error == error) &&
            (identical(other.isLoading, isLoading) ||
                other.isLoading == isLoading));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      conversationId,
      const DeepCollectionEquality().hash(_messages),
      streamingState,
      connectionState,
      toolState,
      error,
      isLoading);

  /// Create a copy of ConversationViewState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConversationViewStateImplCopyWith<_$ConversationViewStateImpl>
      get copyWith => __$$ConversationViewStateImplCopyWithImpl<
          _$ConversationViewStateImpl>(this, _$identity);
}

abstract class _ConversationViewState implements ConversationViewState {
  const factory _ConversationViewState(
      {required final String conversationId,
      required final List<Message> messages,
      required final StreamingState streamingState,
      required final WsConnectionState connectionState,
      final ToolExecutionState toolState,
      final String? error,
      final bool isLoading}) = _$ConversationViewStateImpl;

  @override
  String get conversationId;
  @override
  List<Message> get messages;
  @override
  StreamingState get streamingState;
  @override
  WsConnectionState get connectionState;

  /// 工具执行状态（新增：让用户看到工具执行进度）
  @override
  ToolExecutionState get toolState;
  @override
  String? get error;
  @override
  bool get isLoading;

  /// Create a copy of ConversationViewState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConversationViewStateImplCopyWith<_$ConversationViewStateImpl>
      get copyWith => throw _privateConstructorUsedError;
}
