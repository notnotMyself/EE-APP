import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

/// 全局 Dio 实例，复用连接池
final Dio _imageDio = Dio(BaseOptions(
  connectTimeout: const Duration(seconds: 10),
  receiveTimeout: const Duration(seconds: 30),
  responseType: ResponseType.bytes,
));

/// 简单的内存缓存，避免重复下载
final Map<String, Uint8List> _imageCache = {};

/// 最大缓存条目数
const int _maxCacheSize = 100;

/// 通过 Dio 加载网络图片的 Widget
///
/// 解决 Flutter Web CanvasKit 模式下 Image.network 的 CORS 问题。
/// Dio 的 XHR 请求与 FastAPI CORSMiddleware 配合正常，
/// 而 CanvasKit 内置的图片加载器走的是不同的 XHR 路径，会被浏览器拦截。
class DioImage extends StatefulWidget {
  final String url;
  final BoxFit fit;
  final double? width;
  final double? height;
  final Widget Function(BuildContext context, Object error)? errorBuilder;
  final Widget Function(BuildContext context)? loadingBuilder;

  const DioImage({
    super.key,
    required this.url,
    this.fit = BoxFit.cover,
    this.width,
    this.height,
    this.errorBuilder,
    this.loadingBuilder,
  });

  @override
  State<DioImage> createState() => _DioImageState();
}

class _DioImageState extends State<DioImage> {
  Uint8List? _bytes;
  Object? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadImage();
  }

  @override
  void didUpdateWidget(DioImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.url != widget.url) {
      _loadImage();
    }
  }

  Future<void> _loadImage() async {
    if (widget.url.isEmpty) {
      if (mounted) {
        setState(() {
          _error = Exception('Empty URL');
          _loading = false;
        });
      }
      return;
    }

    // 检查缓存
    final cached = _imageCache[widget.url];
    if (cached != null) {
      if (mounted) {
        setState(() {
          _bytes = cached;
          _loading = false;
          _error = null;
        });
      }
      return;
    }

    // 通过 Dio 获取字节流
    try {
      final response = await _imageDio.get<List<int>>(
        widget.url,
        options: Options(responseType: ResponseType.bytes),
      );
      final bytes = Uint8List.fromList(response.data!);

      // 存入缓存（LRU 淘汰）
      if (_imageCache.length >= _maxCacheSize) {
        _imageCache.remove(_imageCache.keys.first);
      }
      _imageCache[widget.url] = bytes;

      if (mounted) {
        setState(() {
          _bytes = bytes;
          _loading = false;
          _error = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e;
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return widget.loadingBuilder?.call(context) ??
          const Center(
            child: SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
          );
    }

    if (_error != null || _bytes == null) {
      return widget.errorBuilder?.call(context, _error ?? Exception('Unknown')) ??
          const Center(child: Icon(Icons.broken_image, color: Colors.grey));
    }

    return Image.memory(
      _bytes!,
      fit: widget.fit,
      width: widget.width,
      height: widget.height,
      errorBuilder: (context, error, stackTrace) {
        return widget.errorBuilder?.call(context, error) ??
            const Center(child: Icon(Icons.broken_image, color: Colors.grey));
      },
    );
  }
}
