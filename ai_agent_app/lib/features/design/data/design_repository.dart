import 'package:dio/dio.dart';
import 'design_post.dart';

/// 设计内容仓库
/// 负责从后端获取设计帖子数据
class DesignRepository {
  final Dio _dio;

  DesignRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: 'http://localhost:8000',
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
