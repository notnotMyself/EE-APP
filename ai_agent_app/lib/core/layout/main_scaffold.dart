import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import '../../features/agents/presentation/pages/agent_profile_page.dart';

/// 导航栏设计常量 - 基于 Figma 设计稿
class _NavDesign {
  /// 页面背景色（与 AgentProfileTheme 一致）
  static const Color backgroundColor = Color(0xFFE9EAF0);

  /// 选中态文字颜色（主题蓝）
  static const Color activeColor = Color(0xFF0066FF);

  /// 未选中态文字颜色（黑色 90%）
  static const Color inactiveColor = Color(0xE6000000);

  /// 导航栏字体大小
  static const double fontSize = 10.0;

  /// 导航栏字体粗细
  static const FontWeight fontWeight = FontWeight.w500;
}

/// Main scaffold with floating bottom navigation bar.
/// 导航栏悬浮在内容上方，使用 Stack 实现覆盖效果。
/// 在聊天模式下自动隐藏底部导航栏。
class MainScaffold extends ConsumerStatefulWidget {
  final Widget child;
  final String location;

  const MainScaffold({
    super.key,
    required this.child,
    required this.location,
  });

  @override
  ConsumerState<MainScaffold> createState() => _MainScaffoldState();
}

class _MainScaffoldState extends ConsumerState<MainScaffold> {
  int _currentIndex = 0;

  // Tab navigation configuration
  static const List<_TabConfig> _tabs = [
    _TabConfig(
      path: '/home',
      label: 'AI 评审官',
      svgAsset: 'assets/icons/nav_ai_reviewer.svg',
    ),
    _TabConfig(
      path: '/inspiration',
      label: '灵感资讯',
      svgAsset: 'assets/icons/nav_inspiration.svg',
    ),
    _TabConfig(
      path: '/library',
      label: '资料库',
      svgAsset: 'assets/icons/nav_library.svg',
    ),
    _TabConfig(
      path: '/profile',
      label: '我的',
      svgAsset: 'assets/icons/nav_profile.svg',
    ),
  ];

  @override
  void didUpdateWidget(MainScaffold oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.location != oldWidget.location) {
      _updateSelectedIndex(widget.location);
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _updateSelectedIndex(widget.location);
  }

  void _updateSelectedIndex(String location) {
    final index = _tabs.indexWhere((tab) => location.startsWith(tab.path));
    if (index != -1 && index != _currentIndex) {
      setState(() {
        _currentIndex = index;
      });
    }
  }

  void _onTabTapped(int index) {
    if (index != _currentIndex) {
      setState(() {
        _currentIndex = index;
      });
      context.go(_tabs[index].path);
    }
  }

  /// 悬浮导航栏总高度（渐变区 + 胶囊 + 底部安全区），用于给内容区预留底部空间，避免 RenderFlex 溢出
  static double _floatingNavBarHeight(BuildContext context) {
    final bottomSafe = MediaQuery.paddingOf(context).bottom;
    final bottomPad = bottomSafe > 0 ? bottomSafe : 8.0;
    return 16 + 56 + bottomPad; // topPadding + pillHeight + bottomPadding
  }

  @override
  Widget build(BuildContext context) {
    // 监听聊天模式状态：聊天中隐藏底部导航栏
    final isChatActive = ref.watch(chatModeActiveProvider);
    final bottomPadding = isChatActive ? 0.0 : _floatingNavBarHeight(context);

    return Scaffold(
      backgroundColor: _NavDesign.backgroundColor,
      // 使用 Stack 让导航栏悬浮在内容上方
      body: Stack(
        children: [
          // === 内容层：占满全屏，底部预留导航栏高度，避免内容被遮挡导致溢出 ===
          Positioned.fill(
            child: Padding(
              padding: EdgeInsets.only(bottom: bottomPadding),
              child: widget.child,
            ),
          ),

          // === 悬浮导航栏：固定在底部（聊天模式下隐藏） ===
          if (!isChatActive)
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: _buildFloatingNavBar(context),
            ),
        ],
      ),
    );
  }

  /// 构建悬浮毛玻璃胶囊导航栏
  Widget _buildFloatingNavBar(BuildContext context) {
    final bottomSafe = MediaQuery.paddingOf(context).bottom;
    return Container(
      padding: EdgeInsets.only(
        top: 16,
        left: 16,
        right: 16,
        bottom: bottomSafe > 0 ? bottomSafe : 8,
      ),
      // 顶部渐变遮罩（从透明到半透明背景，平滑过渡内容）
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment(0.50, 0.00),
          end: Alignment(0.50, 1.00),
          colors: [Color(0x00F0F1F2), Color(0xCCF0F1F2)],
        ),
      ),
      child: _buildGlassPill(),
    );
  }

  /// 构建毛玻璃胶囊本体
  Widget _buildGlassPill() {
    const double pillHeight = 56;
    const borderRadius = BorderRadius.all(Radius.circular(28));

    return SizedBox(
      height: pillHeight,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // --- 底层柔和阴影（营造浮起感） ---
          Positioned(
            left: 6,
            right: 6,
            top: 6,
            bottom: -4,
            child: Container(
              decoration: BoxDecoration(
                borderRadius: borderRadius,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.08),
                    blurRadius: 24,
                    offset: const Offset(0, 8),
                  ),
                  BoxShadow(
                    color: Colors.black.withOpacity(0.04),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
            ),
          ),

          // --- 外层主体：毛玻璃 + 渐变 + 高光边框 ---
          Positioned.fill(
            child: ClipRRect(
              borderRadius: borderRadius,
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 40, sigmaY: 40),
                child: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: const Alignment(0.0, -1.0),
                      end: const Alignment(0.0, 1.0),
                      colors: [
                        Colors.white.withOpacity(0.72),
                        Colors.white.withOpacity(0.56),
                      ],
                    ),
                    borderRadius: borderRadius,
                    border: Border.all(
                      width: 0.5,
                      color: Colors.white.withOpacity(0.80),
                    ),
                  ),
                ),
              ),
            ),
          ),

          // --- Tab 内容层 ---
          Positioned.fill(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: List.generate(_tabs.length, (index) {
                  final tab = _tabs[index];
                  final isSelected = index == _currentIndex;
                  return _buildNavItem(
                    tab: tab,
                    isSelected: isSelected,
                    onTap: () => _onTabTapped(index),
                  );
                }),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem({
    required _TabConfig tab,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    final color = isSelected
        ? _NavDesign.activeColor
        : _NavDesign.inactiveColor;

    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        behavior: HitTestBehavior.opaque,
        child: Center(
          child: SvgPicture.asset(
            tab.svgAsset,
            width: 70,
            height: 48,
            colorFilter: ColorFilter.mode(color, BlendMode.srcIn),
          ),
        ),
      ),
    );
  }
}

/// Configuration for a tab in the bottom navigation bar
class _TabConfig {
  final String path;
  final String label;
  final String svgAsset;

  const _TabConfig({
    required this.path,
    required this.label,
    required this.svgAsset,
  });
}
