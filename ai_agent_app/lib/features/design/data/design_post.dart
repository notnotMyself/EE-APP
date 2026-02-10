import 'design_repository.dart' show toProxyUrl;

/// 设计帖子数据模型
class DesignPost {
  final String id;
  final String author;
  final String username;
  final String content;
  final String xUrl;
  final List<String> mediaUrls;
  final List<String> videoUrls;
  final String avatarUrl;
  final String fetchedAt;
  final bool hasVideo;

  DesignPost({
    required this.id,
    required this.author,
    required this.username,
    required this.content,
    required this.xUrl,
    required this.mediaUrls,
    required this.videoUrls,
    required this.avatarUrl,
    required this.fetchedAt,
    this.hasVideo = false,
  });

  factory DesignPost.fromJson(Map<String, dynamic> json) {
    // 解析 video_urls - 可能是字符串列表或对象列表
    final rawVideoUrls = json['video_urls'] ?? [];
    final videoUrls = <String>[];
    for (final item in rawVideoUrls) {
      if (item is String) {
        videoUrls.add(toProxyUrl(item));
      } else if (item is Map<String, dynamic>) {
        // 视频对象格式: {"src": "...", "poster": "..."}
        final src = item['src'] as String?;
        if (src != null && src.isNotEmpty) {
          videoUrls.add(toProxyUrl(src));
        }
      }
    }

    // 将所有媒体 URL 转换为代理 URL
    final rawMediaUrls = json['media_urls'] as List? ?? [];
    final mediaUrls = rawMediaUrls
        .map((url) => toProxyUrl(url as String))
        .toList();

    // 头像 URL 也需要代理
    final rawAvatarUrl = json['avatar_url'] as String? ?? '';
    final avatarUrl = rawAvatarUrl.isNotEmpty ? toProxyUrl(rawAvatarUrl) : '';

    return DesignPost(
      id: json['id'] ?? '',
      author: json['author'] ?? '',
      username: json['username'] ?? '',
      content: json['content'] ?? '',
      xUrl: json['x_url'] ?? '',
      mediaUrls: mediaUrls,
      videoUrls: videoUrls,
      avatarUrl: avatarUrl,
      fetchedAt: json['fetched_at'] ?? '',
      hasVideo: json['has_video'] == true || videoUrls.isNotEmpty,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'author': author,
      'username': username,
      'content': content,
      'x_url': xUrl,
      'media_urls': mediaUrls,
      'video_urls': videoUrls,
      'avatar_url': avatarUrl,
      'fetched_at': fetchedAt,
    };
  }
}
