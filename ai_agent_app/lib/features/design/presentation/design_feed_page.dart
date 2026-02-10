import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_staggered_grid_view/flutter_staggered_grid_view.dart';
import 'package:url_launcher/url_launcher.dart';
import '../data/design_post.dart';
import '../data/design_repository.dart';
import 'widgets/dio_image.dart';
import 'widgets/feed_video_player.dart';
import '../../../core/layout/main_scaffold.dart';

/// 设计颜色常量 - 基于 Figma 设计稿
class DesignColors {
  static const Color background = Color(0xFFEFF0F2);
  static const Color textPrimary = Color(0xFF101828);
  static const Color textSecondary = Color(0xFF99A1AF);
  static const Color textTertiary = Color(0xFF6A7282);
  static const Color textGray = Color(0xFF4A5565);
  static const Color primaryBlue = Color(0xFF155DFC);
  static const Color cardBackground = Colors.white;
  static const Color cardBorder = Color(0xFFF3F4F6);
  static const Color tagBackground = Color(0xFFEFF6FF);
  static const Color chipBackground = Color(0xFFF9FAFB);
  static const Color chipActiveBackground = Color(0xFF101828);
}

/// 设计内容展示页面
class DesignFeedPage extends StatefulWidget {
  const DesignFeedPage({super.key});

  @override
  State<DesignFeedPage> createState() => _DesignFeedPageState();
}

class _DesignFeedPageState extends State<DesignFeedPage>
    with SingleTickerProviderStateMixin {
  final DesignRepository _repository = DesignRepository();
  List<DesignPost>? _posts;
  String? _error;
  bool _isLoading = true;

  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadDesignPosts();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
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

  String _formatDate() {
    final now = DateTime.now();
    final weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    final weekday = weekdays[now.weekday - 1];
    return '${now.month}月${now.day}日，$weekday';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: DesignColors.background,
      body: SafeArea(
        child: NestedScrollView(
          headerSliverBuilder: (context, innerBoxIsScrolled) => [
            // 标题区域 + Tab 栏 - 均随滚动消失
            SliverToBoxAdapter(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeader(),
                  _buildTabBar(),
                ],
              ),
            ),
          ],
          body: TabBarView(
            controller: _tabController,
            children: [
              _buildInspireTab(),
              _buildInformationTab(),
            ],
          ),
        ),
      ),
    );
  }

  /// 构建顶部标题区域 - 基于 Figma inspire_title 设计稿
  /// 高度 56 以容纳两行文字（24*1.33 + 4 + 12*1.33 ≈ 52px），避免 RenderFlex 溢出
  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 6),
      child: SizedBox(
        height: 56,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '设计灵感',
              style: const TextStyle(
                color: Color(0xFF101828),
                fontSize: 24,
                fontWeight: FontWeight.w600,
                height: 1.33,
                letterSpacing: -0.53,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              _formatDate(),
              style: const TextStyle(
                color: Color(0xFF99A1AF),
                fontSize: 12,
                fontWeight: FontWeight.w500,
                height: 1.33,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 构建Tab切换栏 - 基于 Figma inspiration-tab 设计稿
  Widget _buildTabBar() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Center(
        child: Container(
          width: 120,
          height: 40,
          clipBehavior: Clip.antiAlias,
          decoration: ShapeDecoration(
            color: Colors.black.withOpacity(0.03),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(100),
            ),
            shadows: const [
              BoxShadow(
                color: Color(0x0F000000),
                blurRadius: 12,
                offset: Offset(0, 4),
              ),
              BoxShadow(
                color: Color(0x14000000),
                blurRadius: 2,
                offset: Offset(0, 0),
              ),
              BoxShadow(
                color: Color(0x0A000000),
                blurRadius: 24,
                offset: Offset(0, 2),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(4),
            child: AnimatedBuilder(
              animation: _tabController,
              builder: (context, child) {
                return Row(
                  children: [
                    _buildSegmentItem('灵感', 0),
                    _buildSegmentItem('AI 资讯', 1),
                  ],
                );
              },
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSegmentItem(String title, int index) {
    final selected = _tabController.index == index;
    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() {
            _tabController.animateTo(index);
          });
        },
        child: Container(
          height: double.infinity,
          clipBehavior: Clip.antiAlias,
          decoration: ShapeDecoration(
            color: selected ? Colors.white.withOpacity(0.80) : Colors.transparent,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(200),
            ),
          ),
          child: Center(
            child: Text(
              title,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.black.withOpacity(0.90),
                fontSize: 14,
                fontWeight: FontWeight.w500,
                height: 1.43,
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// 构建灵感Tab内容 - 基于 Figma 设计稿（无分类标签）
  Widget _buildInspireTab() {
    return Padding(
      padding: const EdgeInsets.only(top: 10),
      child: _buildMasonryGrid(),
    );
  }

  /// 构建瀑布流网格
  Widget _buildMasonryGrid() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return _buildErrorWidget();
    }

    if (_posts == null || _posts!.isEmpty) {
      return const Center(child: Text('暂无设计内容'));
    }

    // 只取有图片的帖子
    final postsWithMedia = _posts!.where((p) => p.mediaUrls.isNotEmpty).toList();

    // 获取悬浮导航栏高度，为滚动内容底部留白
    final navBarHeight = MainScaffold.floatingNavBarHeight(context);

    return RefreshIndicator(
      onRefresh: _loadDesignPosts,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        child: MasonryGridView.count(
          crossAxisCount: 2,
          mainAxisSpacing: 16,
          crossAxisSpacing: 10,
          // 额外 +1 项作为底部留白占位
          itemCount: postsWithMedia.length + 1,
          itemBuilder: (context, index) {
            // 最后一项为底部留白，确保最后的卡片可以滚动到导航栏上方
            if (index == postsWithMedia.length) {
              return SizedBox(height: navBarHeight);
            }
            return _buildMasonryItem(postsWithMedia[index], index);
          },
        ),
      ),
    );
  }

  Widget _buildMasonryItem(DesignPost post, int index) {
    // 根据index生成不同高度，模拟瀑布流效果
    // 视频帖子给更高的高度以容纳播放器
    final heights = post.hasVideo
        ? [200.0, 220.0, 240.0, 210.0, 250.0, 230.0]
        : [116.0, 150.0, 180.0, 130.0, 200.0, 140.0];
    final height = heights[index % heights.length];

    return Container(
      height: height,
      decoration: BoxDecoration(
        color: DesignColors.chipBackground,
        borderRadius: BorderRadius.circular(16),
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        children: [
          // 底层：视频或图片内容
          Positioned.fill(
            child: _buildMasonryContent(post, height),
          ),
          // 顶层：透明点击层（Web 端 HtmlElementView 会拦截事件，
          // 这里用 opaque GestureDetector 覆盖在平台视图之上捕获点击）
          Positioned.fill(
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: () => _showDetailDialog(post),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMasonryContent(DesignPost post, double height) {
    // 视频帖子：直接内联播放
    if (post.hasVideo && post.videoUrls.isNotEmpty) {
      return FeedVideoPlayer(
        videoUrl: post.videoUrls[0],
        height: height,
        width: double.infinity,
        autoPlay: true,
      );
    }

    // 图片帖子
    if (post.mediaUrls.isNotEmpty) {
      return DioImage(
        url: post.mediaUrls[0],
        fit: BoxFit.cover,
        width: double.infinity,
        height: height,
        loadingBuilder: (context) {
          return Container(
            color: DesignColors.chipBackground,
            child: Center(
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: DesignColors.textSecondary.withOpacity(0.4),
                ),
              ),
            ),
          );
        },
        errorBuilder: (context, error) {
          return Container(
            color: DesignColors.chipBackground,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.image_outlined,
                    size: 28, color: DesignColors.textSecondary.withOpacity(0.4)),
                const SizedBox(height: 4),
                Text(
                  post.author.isNotEmpty ? post.author : '',
                  style: TextStyle(
                    fontSize: 10,
                    color: DesignColors.textSecondary.withOpacity(0.6),
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          );
        },
      );
    }

    return Container(
      color: DesignColors.chipBackground,
      child: const Center(
        child: Icon(Icons.image, color: DesignColors.textSecondary),
      ),
    );
  }

  /// 显示帖子详情弹窗 - 基于 Figma detail-card 设计稿
  void _showDetailDialog(DesignPost post) {
    showGeneralDialog(
      context: context,
      barrierDismissible: true,
      barrierLabel: '关闭',
      barrierColor: Colors.black.withOpacity(0.4),
      transitionDuration: const Duration(milliseconds: 250),
      transitionBuilder: (context, animation, secondaryAnimation, child) {
        return FadeTransition(
          opacity: animation,
          child: ScaleTransition(
            scale: Tween<double>(begin: 0.9, end: 1.0).animate(
              CurvedAnimation(parent: animation, curve: Curves.easeOutCubic),
            ),
            child: child,
          ),
        );
      },
      pageBuilder: (context, animation, secondaryAnimation) {
        return Center(
          child: _DesignDetailCard(
            post: post,
            onClose: () => Navigator.of(context).pop(),
            onCopyLink: () {
              Clipboard.setData(ClipboardData(text: post.xUrl));
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('链接已复制'),
                  duration: Duration(seconds: 2),
                ),
              );
            },
          ),
        );
      },
    );
  }

  /// 构建AI资讯Tab内容
  Widget _buildInformationTab() {
    final navBarHeight = MainScaffold.floatingNavBarHeight(context);

    return RefreshIndicator(
      onRefresh: _loadDesignPosts,
      child: SingleChildScrollView(
        padding: EdgeInsets.only(
          left: 20, right: 20, top: 16,
          bottom: navBarHeight + 16,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildTrendingHeader(),
            const SizedBox(height: 12),
            _buildArticleList(),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  /// 构建Trending Updates标题
  Widget _buildTrendingHeader() {
    return const Text(
      'Trending Updates',
      style: TextStyle(
        color: DesignColors.textPrimary,
        fontSize: 20,
        fontWeight: FontWeight.w700,
        height: 1.40,
        letterSpacing: -0.95,
      ),
    );
  }

  /// 构建文章列表
  Widget _buildArticleList() {
    if (_isLoading) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (_error != null) {
      return _buildErrorWidget();
    }

    if (_posts == null || _posts!.isEmpty) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Text('暂无资讯内容'),
        ),
      );
    }

    // 取前5条作为文章列表
    final articles = _posts!.take(5).toList();
    final tags = ['TRENDING', 'GUIDE', 'OPINION', 'TRENDING', 'GUIDE'];
    final times = ['2h ago', '5h ago', '1d ago', '2h ago', '5h ago'];

    return Column(
      children: List.generate(
        articles.length,
        (index) => Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: _buildArticleCard(
            articles[index],
            tags[index % tags.length],
            times[index % times.length],
          ),
        ),
      ),
    );
  }

  /// 构建文章卡片
  Widget _buildArticleCard(DesignPost post, String tag, String time) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: DesignColors.cardBackground,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: DesignColors.cardBorder),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 2,
            offset: const Offset(0, 1),
          ),
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 3,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: InkWell(
        onTap: () => _openUrl(post.xUrl),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 左侧图片
            Container(
              width: 96,
              height: 96,
              decoration: BoxDecoration(
                color: DesignColors.cardBorder,
                borderRadius: BorderRadius.circular(14),
              ),
              clipBehavior: Clip.antiAlias,
              child: post.mediaUrls.isNotEmpty
                  ? DioImage(
                      url: post.mediaUrls[0],
                      fit: BoxFit.cover,
                      errorBuilder: (context, error) {
                        return const Center(
                          child: Icon(Icons.image, color: DesignColors.textSecondary),
                        );
                      },
                    )
                  : const Center(
                      child: Icon(Icons.image, color: DesignColors.textSecondary),
                    ),
            ),
            const SizedBox(width: 16),
            // 右侧内容
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 标签和时间
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: DesignColors.tagBackground,
                          borderRadius: BorderRadius.circular(100),
                        ),
                        child: Text(
                          tag,
                          style: const TextStyle(
                            color: DesignColors.primaryBlue,
                            fontSize: 10,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.37,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        time,
                        style: const TextStyle(
                          color: DesignColors.textSecondary,
                          fontSize: 10,
                          fontWeight: FontWeight.w400,
                          letterSpacing: 0.12,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  // 标题
                  Text(
                    post.author.isNotEmpty ? post.author : 'Design Update',
                    style: const TextStyle(
                      color: DesignColors.textPrimary,
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      height: 1.25,
                      letterSpacing: -0.15,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 6),
                  // 描述
                  Text(
                    post.content.isNotEmpty
                        ? post.content
                        : 'Discover the latest design trends and insights.',
                    style: const TextStyle(
                      color: DesignColors.textTertiary,
                      fontSize: 12,
                      fontWeight: FontWeight.w400,
                      height: 1.63,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorWidget() {
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

/// 设计详情弹窗卡片 - 基于 Figma detail-card 设计稿
class _DesignDetailCard extends StatelessWidget {
  final DesignPost post;
  final VoidCallback onClose;
  final VoidCallback onCopyLink;

  const _DesignDetailCard({
    required this.post,
    required this.onClose,
    required this.onCopyLink,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(28),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 40, sigmaY: 40),
          child: Container(
            width: 328,
            decoration: ShapeDecoration(
              gradient: LinearGradient(
                begin: const Alignment(0.5, 0.0),
                end: const Alignment(0.5, 1.0),
                colors: [
                  Colors.white.withOpacity(0.85),
                  Colors.white.withOpacity(0.95),
                ],
              ),
              shape: RoundedRectangleBorder(
                side: BorderSide(
                    width: 1, color: Colors.white.withOpacity(0.8)),
                borderRadius: BorderRadius.circular(28),
              ),
              shadows: const [
                BoxShadow(
                  color: Color(0x28000000),
                  blurRadius: 40,
                  offset: Offset(0, 12),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // 关闭按钮行
                Padding(
                  padding: const EdgeInsets.only(top: 12, right: 11, left: 11),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      GestureDetector(
                        onTap: onClose,
                        child: Container(
                          width: 36,
                          height: 36,
                          decoration: ShapeDecoration(
                            color: const Color(0x197B7B7B),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(29),
                            ),
                          ),
                          child: const Center(
                            child: Icon(
                              Icons.close,
                              size: 18,
                              color: Color(0xFF4C4C4C),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                // 内容区域
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 17),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 作者信息（头像 + 姓名/副标题）
                      Padding(
                        padding: const EdgeInsets.only(
                            top: 6, bottom: 6),
                        child: Row(
                          children: [
                            // 头像
                            Container(
                              width: 48,
                              height: 48,
                              decoration: ShapeDecoration(
                                color: const Color(0xFFF9FAFB),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(24),
                                ),
                              ),
                              clipBehavior: Clip.antiAlias,
                              child: post.avatarUrl.isNotEmpty
                                  ? DioImage(
                                      url: post.avatarUrl,
                                      fit: BoxFit.cover,
                                      errorBuilder:
                                          (context, error) {
                                        return const Center(
                                          child: Icon(
                                            Icons.person,
                                            size: 24,
                                            color: DesignColors.textSecondary,
                                          ),
                                        );
                                      },
                                    )
                                  : const Center(
                                      child: Icon(
                                        Icons.person,
                                        size: 24,
                                        color: DesignColors.textSecondary,
                                      ),
                                    ),
                            ),
                            const SizedBox(width: 12),
                            // 姓名 + 副标题
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    post.author.isNotEmpty
                                        ? post.author
                                        : 'Design Post',
                                    style: TextStyle(
                                      color: Colors.black.withOpacity(0.90),
                                      fontSize: 18,
                                      fontWeight: FontWeight.w600,
                                      height: 1.44,
                                    ),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  Text(
                                    post.username.isNotEmpty
                                        ? '@${post.username}'
                                        : '',
                                    style: TextStyle(
                                      color: Colors.black.withOpacity(0.54),
                                      fontSize: 14,
                                      fontWeight: FontWeight.w400,
                                      height: 1.43,
                                    ),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 10),
                      // 描述文字
                      if (post.content.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          child: Text(
                            post.content,
                            style: TextStyle(
                              color: Colors.black.withOpacity(0.54),
                              fontSize: 14,
                              fontWeight: FontWeight.w400,
                              height: 1.43,
                            ),
                            maxLines: 3,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      // 图片预览
                      // 视频或图片预览
                      if (post.hasVideo && post.videoUrls.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          child: Container(
                            width: 294,
                            height: 220,
                            clipBehavior: Clip.antiAlias,
                            decoration: ShapeDecoration(
                              color: const Color(0xFFF9FAFB),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(30),
                              ),
                            ),
                            child: FeedVideoPlayer(
                              videoUrl: post.videoUrls[0],
                              width: 294,
                              height: 220,
                              autoPlay: true,
                            ),
                          ),
                        )
                      else if (post.mediaUrls.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          child: Container(
                            width: 294,
                            height: 196,
                            clipBehavior: Clip.antiAlias,
                            decoration: ShapeDecoration(
                              color: const Color(0xFFF9FAFB),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(30),
                              ),
                            ),
                            child: DioImage(
                              url: post.mediaUrls[0],
                              fit: BoxFit.cover,
                              errorBuilder: (context, error) {
                                return const Center(
                                  child: Icon(
                                    Icons.broken_image,
                                    color: DesignColors.textSecondary,
                                    size: 32,
                                  ),
                                );
                              },
                            ),
                          ),
                        ),
                      const SizedBox(height: 10),
                      // 复制链接按钮 - 与登录页"开始"按钮保持一致的黑色样式
                      Center(
                        child: GestureDetector(
                          onTap: onCopyLink,
                          child: Container(
                            width: 267,
                            height: 44,
                            decoration: ShapeDecoration(
                              color: Colors.black,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(100),
                              ),
                              shadows: const [
                                BoxShadow(
                                  color: Color(0x23000000),
                                  blurRadius: 54,
                                  offset: Offset(0, 6),
                                ),
                              ],
                            ),
                            child: const Center(
                              child: Text(
                                '复制链接',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 16,
                                  fontWeight: FontWeight.w500,
                                  height: 1.50,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 25),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
