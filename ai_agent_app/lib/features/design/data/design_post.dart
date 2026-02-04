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
  });

  factory DesignPost.fromJson(Map<String, dynamic> json) {
    return DesignPost(
      id: json['id'] ?? '',
      author: json['author'] ?? '',
      username: json['username'] ?? '',
      content: json['content'] ?? '',
      xUrl: json['x_url'] ?? '',
      mediaUrls: List<String>.from(json['media_urls'] ?? []),
      videoUrls: List<String>.from(json['video_urls'] ?? []),
      avatarUrl: json['avatar_url'] ?? '',
      fetchedAt: json['fetched_at'] ?? '',
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
