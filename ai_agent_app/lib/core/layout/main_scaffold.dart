import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

/// 统一设计主题颜色（与 AgentProfileTheme 保持一致）
class _NavDesign {
  static const Color backgroundColor = Color(0xFFE9EAF0);
  static const Color titleColor = Color(0xFF0D1B34);
  static const Color labelColor = Color(0xFF8696BB);
  static const Color cardBackground = Color(0xADFFFFFF);
  static const Color accentBlue = Color(0xFF378AFF);
}

/// Main scaffold with bottom navigation bar for the app.
/// Uses IndexedStack to preserve page state when switching tabs.
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
      path: '/feed',
      label: '信息流',
      icon: Icons.view_timeline_outlined,
      activeIcon: Icons.view_timeline_rounded,
    ),
    _TabConfig(
      path: '/agents',
      label: 'AI员工',
      icon: Icons.smart_toy_outlined,
      activeIcon: Icons.smart_toy_rounded,
    ),
    _TabConfig(
      path: '/conversations',
      label: '消息',
      icon: Icons.chat_bubble_outline_rounded,
      activeIcon: Icons.chat_bubble_rounded,
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
      body: widget.child,
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.06),
              blurRadius: 20,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: SafeArea(
          top: false,
          child: Container(
            height: 64,
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
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
          mainAxisSize: MainAxisSize.max,
          children: [
            // 图标容器
            AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              curve: Curves.easeInOut,
              width: isSelected ? 52 : 36,
              height: 28,
              decoration: BoxDecoration(
                color: isSelected
                    ? _NavDesign.accentBlue.withOpacity(0.12)
                    : Colors.transparent,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Center(
                child: Icon(
                  isSelected ? tab.activeIcon : tab.icon,
                  size: 22,
                  color: isSelected
                      ? _NavDesign.accentBlue
                      : _NavDesign.labelColor,
                ),
              ),
            ),
            const SizedBox(height: 2),
            // 标签
            Text(
              tab.label,
              style: GoogleFonts.poppins(
                fontSize: 10,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                color: isSelected
                    ? _NavDesign.accentBlue
                    : _NavDesign.labelColor,
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
