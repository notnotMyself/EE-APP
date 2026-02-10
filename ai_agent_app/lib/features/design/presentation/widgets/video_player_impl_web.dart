// ignore_for_file: avoid_web_libraries_in_flutter

import 'dart:html' as html;
import 'dart:ui_web' as ui_web;

import 'package:flutter/material.dart';

/// 全局唯一 ID 计数器
int _nextViewId = 0;

/// Web 端视频播放器 handle，使用原生 HTML <video> 元素
/// 不设置 crossOrigin 属性，避免 CORS 校验
class VideoPlayerHandle {
  final html.VideoElement _video;
  final String _viewType;

  VideoPlayerHandle._(this._video, this._viewType);

  void setMuted(bool muted) {
    _video.muted = muted;
  }

  Widget? buildPlayer(BuildContext context) {
    return HtmlElementView(viewType: _viewType);
  }

  void dispose() {
    _video.pause();
    _video.src = '';
    _video.load(); // 释放资源
  }
}

VideoPlayerHandle createVideoPlayer({
  required String url,
  required bool autoPlay,
  required VoidCallback onError,
  required VoidCallback onReady,
}) {
  final viewId = _nextViewId++;
  final viewType = 'feed-video-$viewId';

  final video = html.VideoElement()
    ..src = url
    ..autoplay = autoPlay
    ..muted = true
    ..loop = true
    ..setAttribute('playsinline', 'true')
    ..style.width = '100%'
    ..style.height = '100%'
    ..style.objectFit = 'cover'
    ..style.display = 'block'
    ..style.backgroundColor = '#1F2937'
    // 关键：禁止 video 元素拦截鼠标事件，让点击穿透到 Flutter 的 GestureDetector
    ..style.pointerEvents = 'none';

  // 关键：不设置 crossOrigin，绕过 CORS
  video.onCanPlay.first.then((_) => onReady());
  video.onError.first.then((_) => onError());

  // ignore: undefined_prefixed_name
  ui_web.platformViewRegistry.registerViewFactory(
    viewType,
    (int id) => video,
  );

  return VideoPlayerHandle._(video, viewType);
}
