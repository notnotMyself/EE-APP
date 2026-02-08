import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

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
class MainScaffold extends StatefulWidget {
  final Widget child;
  final String location;

  const MainScaffold({
    super.key,
    required this.child,
    required this.location,
  });

  @override
  State<MainScaffold> createState() => _MainScaffoldState();
}

class _MainScaffoldState extends State<MainScaffold> {
  int _currentIndex = 0;

  // Tab navigation configuration
  static const List<_TabConfig> _tabs = [
    _TabConfig(
      path: '/home',
      label: 'AI 评审官',
      icon: Icons.chat_bubble_outline_rounded,
      activeIcon: Icons.chat_bubble_rounded,
    ),
    _TabConfig(
      path: '/inspiration',
      label: '灵感资讯',
      icon: Icons.auto_awesome_outlined,
      activeIcon: Icons.auto_awesome,
    ),
    _TabConfig(
      path: '/library',
      label: '资料库',
      icon: Icons.folder_open_rounded,
      activeIcon: Icons.folder_rounded,
    ),
    _TabConfig(
      path: '/profile',
      label: '我的',
      icon: Icons.person_outline_rounded,
      activeIcon: Icons.person_rounded,
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _NavDesign.backgroundColor,
      // 使用 Stack 让导航栏悬浮在内容上方
      body: Stack(
        children: [
          // === 内容层：占满全屏 ===
          Positioned.fill(
            child: widget.child,
          ),

          // === 悬浮导航栏：固定在底部 ===
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

  /// 构建悬浮毛玻璃胶囊导航栏 + 系统导航条
  Widget _buildFloatingNavBar(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // === 导航栏区域 ===
        Container(
          padding: const EdgeInsets.only(
            top: 16,
            left: 16,
            right: 16,
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
        ),

        // === 系统手势导航条 ===
        Container(
          width: double.infinity,
          height: 32,
          decoration: const BoxDecoration(
            color: Color(0xCCF0F1F2),
          ),
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: Center(
            child: Container(
              width: 120,
              height: 4,
              decoration: ShapeDecoration(
                color: Colors.black.withOpacity(0.50),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  /// 构建毛玻璃胶囊本体
  Widget _buildGlassPill() {
    return SizedBox(
      height: 56,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // --- 内层阴影/边框层（向右下偏移，营造玻璃厚度感） ---
          Positioned(
            left: 8,
            top: 12,
            right: 8,
            bottom: -8,
            child: Container(
              decoration: ShapeDecoration(
                gradient: LinearGradient(
                  begin: const Alignment(0.50, 0.00),
                  end: const Alignment(0.50, 1.00),
                  colors: [
                    Colors.white.withOpacity(0.50),
                    Colors.white,
                  ],
                ),
                shape: RoundedRectangleBorder(
                  side: BorderSide(
                    width: 1.60,
                    color: Colors.white.withOpacity(0.3),
                  ),
                  borderRadius: BorderRadius.circular(100),
                ),
              ),
            ),
          ),

          // --- 外层主体：毛玻璃 + 渐变 ---
          Positioned.fill(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(100),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
                child: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: const Alignment(0.50, 0.00),
                      end: const Alignment(0.50, 1.00),
                      colors: [
                        Colors.white.withOpacity(0.60),
                        Colors.white.withOpacity(0.92),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(100),
                    boxShadow: const [
                      BoxShadow(
                        color: Color(0x19000000),
                        blurRadius: 32,
                        offset: Offset(0, 6),
                        spreadRadius: 0,
                      ),
                    ],
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
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        behavior: HitTestBehavior.opaque,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          children: [
            // 图标
            Icon(
              isSelected ? tab.activeIcon : tab.icon,
              size: 24,
              color: isSelected
                  ? _NavDesign.activeColor
                  : _NavDesign.inactiveColor,
            ),
            const SizedBox(height: 2),
            // 标签文字
            SizedBox(
              width: 70,
              child: Text(
                tab.label,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: isSelected
                      ? _NavDesign.activeColor
                      : _NavDesign.inactiveColor,
                  fontSize: _NavDesign.fontSize,
                  fontWeight: _NavDesign.fontWeight,
                  height: 1.40,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Configuration for a tab in the bottom navigation bar
class _TabConfig {
  final String path;
  final String label;
  final IconData icon;
  final IconData activeIcon;

  const _TabConfig({
    required this.path,
    required this.label,
    required this.icon,
    required this.activeIcon,
  });
}
