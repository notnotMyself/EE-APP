import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

/// 移动端视频播放器 handle
class VideoPlayerHandle {
  final VideoPlayerController _controller;

  VideoPlayerHandle._(this._controller);

  void setMuted(bool muted) {
    _controller.setVolume(muted ? 0 : 1);
  }

  Widget? buildPlayer(BuildContext context) {
    if (!_controller.value.isInitialized) return null;
    return FittedBox(
      fit: BoxFit.cover,
      clipBehavior: Clip.antiAlias,
      child: SizedBox(
        width: _controller.value.size.width,
        height: _controller.value.size.height,
        child: VideoPlayer(_controller),
      ),
    );
  }

  void dispose() {
    _controller.dispose();
  }
}

VideoPlayerHandle createVideoPlayer({
  required String url,
  required bool autoPlay,
  required VoidCallback onError,
  required VoidCallback onReady,
}) {
  final controller = VideoPlayerController.networkUrl(Uri.parse(url));

  controller.initialize().then((_) {
    controller.setLooping(true);
    controller.setVolume(0);
    if (autoPlay) controller.play();
    onReady();
  }).catchError((_) {
    onError();
  });

  return VideoPlayerHandle._(controller);
}
