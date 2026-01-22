import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/voice_input_service.dart';
import '../theme/agent_profile_theme.dart';

/// 语音输入弹窗
/// 
/// 显示语音录入界面，包含：
/// - 音量波形动画
/// - 识别文字实时显示
/// - 取消/确认按钮
class VoiceInputDialog extends ConsumerStatefulWidget {
  final ValueChanged<String> onResult;

  const VoiceInputDialog({
    super.key,
    required this.onResult,
  });

  @override
  ConsumerState<VoiceInputDialog> createState() => _VoiceInputDialogState();
}

class _VoiceInputDialogState extends ConsumerState<VoiceInputDialog>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();

    // 开始录音
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(voiceInputServiceProvider.notifier).startListening();
    });
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _onConfirm() async {
    final text = await ref.read(voiceInputServiceProvider.notifier).stopListening();
    if (text.isNotEmpty) {
      widget.onResult(text);
    }
    if (mounted) {
      Navigator.of(context).pop();
    }
  }

  void _onCancel() async {
    await ref.read(voiceInputServiceProvider.notifier).cancelListening();
    if (mounted) {
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final voiceState = ref.watch(voiceInputServiceProvider);

    return Dialog(
      backgroundColor: Colors.transparent,
      child: Container(
        width: 300,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // 标题
            Text(
              voiceState.isListening ? '正在聆听...' : '语音输入',
              style: AgentProfileTheme.agentNameStyle.copyWith(fontSize: 18),
            ),
            const SizedBox(height: 24),

            // 麦克风动画
            _buildMicrophoneAnimation(voiceState),
            const SizedBox(height: 24),

            // 识别文字
            Container(
              width: double.infinity,
              constraints: const BoxConstraints(minHeight: 60),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                voiceState.recognizedText.isEmpty
                    ? '请说话...'
                    : voiceState.recognizedText,
                style: TextStyle(
                  color: voiceState.recognizedText.isEmpty
                      ? Colors.grey
                      : Colors.black87,
                  fontSize: 16,
                ),
                textAlign: TextAlign.center,
              ),
            ),

            // 错误提示
            if (voiceState.hasError) ...[
              const SizedBox(height: 12),
              Text(
                voiceState.errorMessage ?? '发生错误',
                style: const TextStyle(
                  color: Colors.red,
                  fontSize: 14,
                ),
                textAlign: TextAlign.center,
              ),
            ],

            const SizedBox(height: 24),

            // 操作按钮
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                // 取消按钮
                _buildActionButton(
                  icon: Icons.close,
                  label: '取消',
                  color: Colors.grey,
                  onTap: _onCancel,
                ),
                // 确认按钮
                _buildActionButton(
                  icon: Icons.check,
                  label: '完成',
                  color: const Color(0xFF0066FF),
                  onTap: _onConfirm,
                  enabled: voiceState.recognizedText.isNotEmpty,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// 麦克风动画
  Widget _buildMicrophoneAnimation(VoiceInputState voiceState) {
    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        final scale = 1.0 + (voiceState.soundLevel * 0.3);
        final opacity = 0.3 + (voiceState.soundLevel * 0.4);

        return Stack(
          alignment: Alignment.center,
          children: [
            // 外圈波纹
            if (voiceState.isListening) ...[
              _buildRipple(80, opacity * 0.3, _animationController.value),
              _buildRipple(60, opacity * 0.5, (_animationController.value + 0.3) % 1),
            ],
            // 麦克风图标
            Transform.scale(
              scale: scale,
              child: Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: voiceState.isListening
                      ? const Color(0xFF0066FF)
                      : Colors.grey.shade300,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  voiceState.isListening ? Icons.mic : Icons.mic_none,
                  size: 40,
                  color: Colors.white,
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  /// 波纹效果
  Widget _buildRipple(double size, double opacity, double progress) {
    return Container(
      width: size + (progress * 40),
      height: size + (progress * 40),
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(
          color: const Color(0xFF0066FF).withOpacity(opacity * (1 - progress)),
          width: 2,
        ),
      ),
    );
  }

  /// 操作按钮
  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
    bool enabled = true,
  }) {
    return GestureDetector(
      onTap: enabled ? onTap : null,
      child: Opacity(
        opacity: enabled ? 1.0 : 0.5,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(height: 8),
            Text(
              label,
              style: TextStyle(
                color: color,
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// 显示语音输入弹窗
Future<void> showVoiceInputDialog(
  BuildContext context, {
  required ValueChanged<String> onResult,
}) {
  return showDialog(
    context: context,
    barrierDismissible: false,
    builder: (context) => VoiceInputDialog(onResult: onResult),
  );
}

