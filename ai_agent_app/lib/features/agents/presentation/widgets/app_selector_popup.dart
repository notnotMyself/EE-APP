import 'package:flutter/material.dart';

/// 应用数据模型
class AppInfo {
  final String id;
  final String name;
  final String iconPath; // 图标资源路径

  const AppInfo({
    required this.id,
    required this.name,
    required this.iconPath,
  });
}

/// 预定义的应用列表
class AppInfoList {
  static const notepad = AppInfo(
    id: 'notepad',
    name: '便签',
    iconPath: 'assets/images/app_icons/app_notepad.png',
  );

  static const gallery = AppInfo(
    id: 'gallery',
    name: '相册',
    iconPath: 'assets/images/app_icons/app_gallery.png',
  );

  static const recorder = AppInfo(
    id: 'recorder',
    name: '录音',
    iconPath: 'assets/images/app_icons/app_recorder.png',
  );

  static const camera = AppInfo(
    id: 'camera',
    name: '相机',
    iconPath: 'assets/images/app_icons/app_camera.png',
  );

  static const weather = AppInfo(
    id: 'weather',
    name: '天气',
    iconPath: 'assets/images/app_icons/app_weather.png',
  );

  /// 所有应用
  static List<AppInfo> get all => [
        notepad,
        gallery,
        recorder,
        camera,
        weather,
      ];
}

/// 应用选择弹窗
class AppSelectorPopup extends StatefulWidget {
  final AppInfo? selectedApp;
  final ValueChanged<AppInfo?> onAppSelected;

  const AppSelectorPopup({
    super.key,
    this.selectedApp,
    required this.onAppSelected,
  });

  @override
  State<AppSelectorPopup> createState() => _AppSelectorPopupState();
}

class _AppSelectorPopupState extends State<AppSelectorPopup> {
  final _searchController = TextEditingController();
  List<AppInfo> _filteredApps = [];

  @override
  void initState() {
    super.initState();
    _filteredApps = AppInfoList.all;
    _searchController.addListener(_onSearchChanged);
  }

  @override
  void dispose() {
    _searchController.removeListener(_onSearchChanged);
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged() {
    final query = _searchController.text.toLowerCase();
    setState(() {
      if (query.isEmpty) {
        _filteredApps = AppInfoList.all;
      } else {
        _filteredApps = AppInfoList.all
            .where((app) => app.name.toLowerCase().contains(query))
            .toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: const BoxConstraints(minWidth: 168, maxWidth: 256),
      width: 196,
      decoration: ShapeDecoration(
        color: const Color(0xCCEFEFEF),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
        ),
        shadows: const [
          BoxShadow(
            color: Color(0x23000000),
            blurRadius: 54,
            offset: Offset(0, 6),
            spreadRadius: 0,
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 搜索框
          _buildSearchBar(),

          // 应用列表
          ..._filteredApps.map((app) => _buildAppItem(app)),

          const SizedBox(height: 8),
        ],
      ),
    );
  }

  /// 搜索框
  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.all(8),
      child: Container(
        height: 40,
        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
        decoration: ShapeDecoration(
          color: Colors.black.withOpacity(0.08),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(100),
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              child: Icon(
                Icons.search,
                size: 20,
                color: Colors.black.withOpacity(0.54),
              ),
            ),
            Expanded(
              child: TextField(
                controller: _searchController,
                style: TextStyle(
                  color: Colors.black.withOpacity(0.90),
                  fontSize: 16,
                  fontWeight: FontWeight.w400,
                ),
                decoration: InputDecoration(
                  hintText: '搜索...',
                  hintStyle: TextStyle(
                    color: Colors.black.withOpacity(0.54),
                    fontSize: 16,
                    fontWeight: FontWeight.w400,
                  ),
                  border: InputBorder.none,
                  isDense: true,
                  contentPadding: EdgeInsets.zero,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 应用项
  Widget _buildAppItem(AppInfo app) {
    final isSelected = widget.selectedApp?.id == app.id;

    return GestureDetector(
      onTap: () {
        widget.onAppSelected(app);
        Navigator.of(context).pop();
      },
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? Colors.black.withOpacity(0.06) : null,
        ),
        child: Row(
          children: [
            // 应用图标
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: Image.asset(
                app.iconPath,
                width: 20,
                height: 20,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => Container(
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Icon(Icons.apps, size: 14),
                ),
              ),
            ),
            const SizedBox(width: 12),
            // 应用名称
            Expanded(
              child: Text(
                app.name,
                style: TextStyle(
                  color: Colors.black.withOpacity(0.90),
                  fontSize: 16,
                  fontWeight: FontWeight.w400,
                  height: 1.38,
                ),
              ),
            ),
            // 选中标记
            if (isSelected)
              const Icon(
                Icons.check,
                size: 20,
                color: Color(0xFF0066FF),
              ),
          ],
        ),
      ),
    );
  }
}

/// 显示应用选择弹窗
/// 
/// 返回选中的应用，如果取消则返回 null
Future<AppInfo?> showAppSelectorPopup(
  BuildContext context, {
  AppInfo? selectedApp,
  required RelativeRect position,
}) async {
  AppInfo? result;

  await showMenu<AppInfo>(
    context: context,
    position: position,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(24),
    ),
    color: Colors.transparent,
    elevation: 0,
    items: [
      PopupMenuItem<AppInfo>(
        enabled: false,
        padding: EdgeInsets.zero,
        child: AppSelectorPopup(
          selectedApp: selectedApp,
          onAppSelected: (app) {
            result = app;
          },
        ),
      ),
    ],
  );

  return result;
}
