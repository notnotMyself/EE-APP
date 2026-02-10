import 'package:dio/dio.dart';
import '../../../core/config/app_config.dart';
import 'design_post.dart';

/// 缓存 baseUrl，避免每次调用都走 getter 逻辑
final String _cachedBaseUrl = AppConfig.apiBaseUrl;

/// 将外部媒体 URL 转换为代理 URL
String toProxyUrl(String originalUrl) {
  if (originalUrl.isEmpty) return originalUrl;
  // 使用后端代理解决 CORS 问题
  return '$_cachedBaseUrl/api/v1/design-feed/media?url=${Uri.encodeComponent(originalUrl)}';
}

/// 设计内容仓库
/// 负责从后端获取设计帖子数据
class DesignRepository {
  final Dio _dio;

  DesignRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: AppConfig.apiBaseUrl,
              connectTimeout: const Duration(seconds: 10),
              receiveTimeout: const Duration(seconds: 10),
            ));

  /// 获取设计帖子列表
  ///
  /// [limit] 返回的帖子数量，默认 20
  Future<DesignFeedResponse> getDesignPosts({int limit = 20}) async {
    try {
      final response = await _dio.get(
        '/api/v1/design-feed',
        queryParameters: {'limit': limit},
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final posts = (data['posts'] as List)
            .map((json) => DesignPost.fromJson(json as Map<String, dynamic>))
            .toList();

        return DesignFeedResponse(
          success: data['success'] ?? true,
          posts: posts,
          total: data['total'] ?? 0,
          returned: data['returned'] ?? posts.length,
        );
      } else {
        throw Exception('Failed to load design posts: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Network error: ${e.message}');
    }
  }

  /// 获取 AI 资讯文章列表
  Future<AiNewsResponse> getAiNews({int limit = 15, String source = ''}) async {
    try {
      final params = <String, dynamic>{'limit': limit};
      if (source.isNotEmpty) params['source'] = source;

      final response = await _dio.get(
        '/api/v1/ai-news',
        queryParameters: params,
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final articles = (data['articles'] as List)
            .map((json) => NewsArticle.fromJson(json as Map<String, dynamic>))
            .toList();

        return AiNewsResponse(
          success: data['success'] ?? true,
          articles: articles,
          total: data['total'] ?? 0,
        );
      } else {
        throw Exception('Failed to load AI news: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Network error: ${e.message}');
    }
  }

  /// 获取设计内容统计信息
  Future<DesignStats> getDesignStats() async {
    try {
      final response = await _dio.get('/api/v1/design-feed/stats');

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        return DesignStats.fromJson(data);
      } else {
        throw Exception('Failed to load design stats: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Network error: ${e.message}');
    }
  }
}

/// 设计内容响应
class DesignFeedResponse {
  final bool success;
  final List<DesignPost> posts;
  final int total;
  final int returned;

  DesignFeedResponse({
    required this.success,
    required this.posts,
    required this.total,
    required this.returned,
  });
}

/// 设计内容统计
class DesignStats {
  final bool success;
  final int totalPosts;
  final int postsWithMedia;
  final int postsWithVideo;
  final int totalAuthors;
  final List<List<dynamic>> topAuthors;
  final String lastUpdated;

  DesignStats({
    required this.success,
    required this.totalPosts,
    required this.postsWithMedia,
    required this.postsWithVideo,
    required this.totalAuthors,
    required this.topAuthors,
    required this.lastUpdated,
  });

  factory DesignStats.fromJson(Map<String, dynamic> json) {
    return DesignStats(
      success: json['success'] ?? true,
      totalPosts: json['total_posts'] ?? 0,
      postsWithMedia: json['posts_with_media'] ?? 0,
      postsWithVideo: json['posts_with_video'] ?? 0,
      totalAuthors: json['total_authors'] ?? 0,
      topAuthors: List<List<dynamic>>.from(json['top_authors'] ?? []),
      lastUpdated: json['last_updated'] ?? '',
    );
  }
}

/// AI 资讯文章
class NewsArticle {
  final String id;
  final String title;
  final String summary;
  final String url;
  final String imageUrl;
  final String source;
  final String tag;
  final String author;
  final String publishedAt;
  final String relativeTime;

  NewsArticle({
    required this.id,
    required this.title,
    required this.summary,
    required this.url,
    required this.imageUrl,
    required this.source,
    required this.tag,
    required this.author,
    required this.publishedAt,
    required this.relativeTime,
  });

  factory NewsArticle.fromJson(Map<String, dynamic> json) {
    final rawImageUrl = json['image_url'] as String? ?? '';
    return NewsArticle(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      summary: json['summary'] ?? '',
      url: json['url'] ?? '',
      imageUrl: rawImageUrl.isNotEmpty ? toProxyUrl(rawImageUrl) : '',
      source: json['source'] ?? '',
      tag: json['tag'] ?? '',
      author: json['author'] ?? '',
      publishedAt: json['published_at'] ?? '',
      relativeTime: json['relative_time'] ?? '',
    );
  }
}

/// AI 资讯响应
class AiNewsResponse {
  final bool success;
  final List<NewsArticle> articles;
  final int total;

  AiNewsResponse({
    required this.success,
    required this.articles,
    required this.total,
  });
}
