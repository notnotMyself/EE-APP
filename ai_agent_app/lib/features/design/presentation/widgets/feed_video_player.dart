import 'package:flutter/material.dart';

import 'video_player_impl_stub.dart'
    if (dart.library.html) 'video_player_impl_web.dart' as impl;

/// 设计 Feed 视频播放器
///
/// Web 端使用原生 HTML <video> 元素（避免 video_player 包的 CORS 问题）；
/// 移动端使用 video_player 包。
class FeedVideoPlayer extends StatefulWidget {
  final String videoUrl;
  final double? width;
  final double? height;
  final BoxFit fit;
  final bool autoPlay;

  const FeedVideoPlayer({
    super.key,
    required this.videoUrl,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
    this.autoPlay = true,
  });

  @override
  State<FeedVideoPlayer> createState() => _FeedVideoPlayerState();
}

class _FeedVideoPlayerState extends State<FeedVideoPlayer> {
  late final impl.VideoPlayerHandle _handle;
  bool _hasError = false;

  @override
  void initState() {
    super.initState();
    _handle = impl.createVideoPlayer(
      url: widget.videoUrl,
      autoPlay: widget.autoPlay,
      onError: () {
        if (mounted) setState(() => _hasError = true);
      },
      onReady: () {
        if (mounted) setState(() {});
      },
    );
  }

  @override
  void dispose() {
    _handle.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_hasError) return _buildErrorState();

    final playerWidget = _handle.buildPlayer(context);
    if (playerWidget == null) return _buildLoadingState();

    return SizedBox(
      width: widget.width,
      height: widget.height,
      child: playerWidget,
    );
  }

  Widget _buildLoadingState() {
    return Container(
      width: widget.width,
      height: widget.height,
      color: const Color(0xFFF3F4F6),
      child: const Center(
        child: SizedBox(
          width: 24,
          height: 24,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            color: Color(0xFF9CA3AF),
          ),
        ),
      ),
    );
  }

  Widget _buildErrorState() {
    return Container(
      width: widget.width,
      height: widget.height,
      color: const Color(0xFFF3F4F6),
      child: const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.videocam_off_rounded,
                size: 28, color: Color(0xFF9CA3AF)),
            SizedBox(height: 4),
            Text('视频加载失败',
                style: TextStyle(fontSize: 10, color: Color(0xFF9CA3AF))),
          ],
        ),
      ),
    );
  }
}
