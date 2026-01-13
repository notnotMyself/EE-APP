import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

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
      activeIcon: Icons.view_timeline,
    ),
    _TabConfig(
      path: '/agents',
      label: 'AI员工',
      icon: Icons.smart_toy_outlined,
      activeIcon: Icons.smart_toy,
    ),
    _TabConfig(
      path: '/conversations',
      label: '消息',
      icon: Icons.chat_bubble_outline,
      activeIcon: Icons.chat_bubble,
    ),
    _TabConfig(
      path: '/profile',
      label: '我的',
      icon: Icons.person_outline,
      activeIcon: Icons.person,
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
      body: widget.child,
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
        selectedItemColor: Theme.of(context).primaryColor,
        unselectedItemColor: Colors.grey,
        selectedFontSize: 12,
        unselectedFontSize: 12,
        items: _tabs.map((tab) {
          final isSelected = _tabs.indexOf(tab) == _currentIndex;
          return BottomNavigationBarItem(
            icon: Icon(isSelected ? tab.activeIcon : tab.icon),
            label: tab.label,
          );
        }).toList(),
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
