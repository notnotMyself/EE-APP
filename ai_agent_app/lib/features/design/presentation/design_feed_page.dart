import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../data/design_post.dart';
import '../data/design_repository.dart';

/// 设计内容展示页面
class DesignFeedPage extends StatefulWidget {
  const DesignFeedPage({super.key});

  @override
  State<DesignFeedPage> createState() => _DesignFeedPageState();
}

class _DesignFeedPageState extends State<DesignFeedPage> {
  final DesignRepository _repository = DesignRepository();
  List<DesignPost>? _posts;
  String? _error;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDesignPosts();
  }

  Future<void> _loadDesignPosts() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await _repository.getDesignPosts(limit: 20);
      setState(() {
        _posts = response.posts;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('设计灵感'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadDesignPosts,
            tooltip: '刷新',
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.red),
            const SizedBox(height: 16),
            Text('加载失败: $_error'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadDesignPosts,
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    if (_posts == null || _posts!.isEmpty) {
      return const Center(child: Text('暂无设计内容'));
    }

    return RefreshIndicator(
      onRefresh: _loadDesignPosts,
      child: ListView.builder(
        itemCount: _posts!.length,
        itemBuilder: (context, index) {
          return _buildDesignCard(_posts![index]);
        },
      ),
    );
  }

  Widget _buildDesignCard(DesignPost post) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 作者信息
          ListTile(
            leading: post.avatarUrl.isNotEmpty
                ? CircleAvatar(
                    backgroundImage: NetworkImage(post.avatarUrl),
                    onBackgroundImageError: (_, __) {},
                  )
                : const CircleAvatar(
                    child: Icon(Icons.person),
                  ),
            title: Text(
              post.author.isNotEmpty ? post.author : 'Unknown',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: post.username.isNotEmpty ? Text('@${post.username}') : null,
          ),

          // 内容文本
          if (post.content.isNotEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Text(
                post.content,
                style: const TextStyle(fontSize: 15),
              ),
            ),

          // 图片展示
          if (post.mediaUrls.isNotEmpty) _buildMediaGallery(post.mediaUrls),

          // 操作按钮
          Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton.icon(
                  icon: const Icon(Icons.open_in_new, size: 18),
                  label: const Text('查看原文'),
                  onPressed: () => _openUrl(post.xUrl),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMediaGallery(List<String> mediaUrls) {
    if (mediaUrls.length == 1) {
      // 单张图片
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: Image.network(
            mediaUrls[0],
            fit: BoxFit.cover,
            width: double.infinity,
            errorBuilder: (context, error, stackTrace) {
              return Container(
                height: 200,
                color: Colors.grey[300],
                child: const Center(
                  child: Icon(Icons.broken_image, size: 48),
                ),
              );
            },
          ),
        ),
      );
    } else {
      // 多张图片 - 网格展示
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: mediaUrls.length == 2 ? 2 : 2,
            crossAxisSpacing: 8,
            mainAxisSpacing: 8,
          ),
          itemCount: mediaUrls.length,
          itemBuilder: (context, index) {
            return ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                mediaUrls[index],
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    color: Colors.grey[300],
                    child: const Center(
                      child: Icon(Icons.broken_image),
                    ),
                  );
                },
              ),
            );
          },
        ),
      );
    }
  }

  Future<void> _openUrl(String url) async {
    if (url.isEmpty) return;

    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('无法打开链接: $url')),
        );
      }
    }
  }
}
