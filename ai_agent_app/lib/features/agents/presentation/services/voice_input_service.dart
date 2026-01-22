import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:speech_to_text/speech_recognition_result.dart';
import 'package:permission_handler/permission_handler.dart';

/// 语音输入状态
enum VoiceInputStatus {
  idle,       // 空闲
  listening,  // 正在听
  processing, // 处理中
  error,      // 错误
}

/// 语音输入状态数据
class VoiceInputState {
  final VoiceInputStatus status;
  final String recognizedText;
  final String? errorMessage;
  final double soundLevel;

  const VoiceInputState({
    this.status = VoiceInputStatus.idle,
    this.recognizedText = '',
    this.errorMessage,
    this.soundLevel = 0.0,
  });

  VoiceInputState copyWith({
    VoiceInputStatus? status,
    String? recognizedText,
    String? errorMessage,
    double? soundLevel,
  }) {
    return VoiceInputState(
      status: status ?? this.status,
      recognizedText: recognizedText ?? this.recognizedText,
      errorMessage: errorMessage,
      soundLevel: soundLevel ?? this.soundLevel,
    );
  }

  bool get isListening => status == VoiceInputStatus.listening;
  bool get hasError => status == VoiceInputStatus.error;
}

/// 语音输入服务
/// 
/// 提供语音转文字功能
class VoiceInputService extends StateNotifier<VoiceInputState> {
  VoiceInputService() : super(const VoiceInputState());

  final SpeechToText _speechToText = SpeechToText();
  bool _isInitialized = false;

  /// 初始化语音识别
  Future<bool> initialize() async {
    if (_isInitialized) return true;

    try {
      // 请求麦克风权限
      final permissionStatus = await Permission.microphone.request();
      if (!permissionStatus.isGranted) {
        state = state.copyWith(
          status: VoiceInputStatus.error,
          errorMessage: '需要麦克风权限才能使用语音输入',
        );
        return false;
      }

      // 初始化语音识别
      _isInitialized = await _speechToText.initialize(
        onError: _onError,
        onStatus: _onStatus,
      );

      if (!_isInitialized) {
        state = state.copyWith(
          status: VoiceInputStatus.error,
          errorMessage: '语音识别初始化失败',
        );
      }

      return _isInitialized;
    } catch (e) {
      debugPrint('语音识别初始化异常: $e');
      state = state.copyWith(
        status: VoiceInputStatus.error,
        errorMessage: '语音识别初始化异常: $e',
      );
      return false;
    }
  }

  /// 开始录音
  Future<void> startListening({String localeId = 'zh_CN'}) async {
    if (!_isInitialized) {
      final success = await initialize();
      if (!success) return;
    }

    if (_speechToText.isListening) {
      await stopListening();
      return;
    }

    state = state.copyWith(
      status: VoiceInputStatus.listening,
      recognizedText: '',
      errorMessage: null,
    );

    try {
      await _speechToText.listen(
        onResult: _onResult,
        onSoundLevelChange: _onSoundLevelChange,
        localeId: localeId,
        listenMode: ListenMode.dictation,
        cancelOnError: true,
        partialResults: true,
      );
    } catch (e) {
      debugPrint('开始录音失败: $e');
      state = state.copyWith(
        status: VoiceInputStatus.error,
        errorMessage: '开始录音失败: $e',
      );
    }
  }

  /// 停止录音
  Future<String> stopListening() async {
    if (_speechToText.isListening) {
      await _speechToText.stop();
    }
    
    final text = state.recognizedText;
    state = state.copyWith(
      status: VoiceInputStatus.idle,
      soundLevel: 0.0,
    );
    
    return text;
  }

  /// 取消录音
  Future<void> cancelListening() async {
    if (_speechToText.isListening) {
      await _speechToText.cancel();
    }
    
    state = state.copyWith(
      status: VoiceInputStatus.idle,
      recognizedText: '',
      soundLevel: 0.0,
    );
  }

  /// 语音识别结果回调
  void _onResult(SpeechRecognitionResult result) {
    state = state.copyWith(
      recognizedText: result.recognizedWords,
      status: result.finalResult 
          ? VoiceInputStatus.idle 
          : VoiceInputStatus.listening,
    );
  }

  /// 音量变化回调
  void _onSoundLevelChange(double level) {
    // 将音量归一化到 0-1
    final normalizedLevel = (level + 160) / 160;
    state = state.copyWith(
      soundLevel: normalizedLevel.clamp(0.0, 1.0),
    );
  }

  /// 错误回调
  void _onError(dynamic error) {
    debugPrint('语音识别错误: $error');
    state = state.copyWith(
      status: VoiceInputStatus.error,
      errorMessage: '语音识别错误: $error',
    );
  }

  /// 状态变化回调
  void _onStatus(String status) {
    debugPrint('语音识别状态: $status');
    if (status == 'done' || status == 'notListening') {
      state = state.copyWith(status: VoiceInputStatus.idle);
    }
  }

  /// 检查是否支持语音识别
  Future<bool> isAvailable() async {
    if (!_isInitialized) {
      await initialize();
    }
    return _isInitialized;
  }

  /// 获取可用的语言列表
  Future<List<LocaleName>> getLocales() async {
    if (!_isInitialized) {
      await initialize();
    }
    return _speechToText.locales();
  }

  @override
  void dispose() {
    _speechToText.stop();
    super.dispose();
  }
}

/// 语音输入服务 Provider
final voiceInputServiceProvider = StateNotifierProvider<VoiceInputService, VoiceInputState>((ref) {
  return VoiceInputService();
});

