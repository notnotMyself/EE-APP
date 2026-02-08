import 'package:flutter/material.dart';
import '../../../agents/presentation/theme/agent_profile_theme.dart';

/// 资料库页面 - 功能开发中占位
class LibraryPage extends StatelessWidget {
  const LibraryPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AgentProfileTheme.backgroundColor,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 标题区域
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 16, 24, 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '资料库',
                    style: TextStyle(
                      color: AgentProfileTheme.titleColor,
                      fontSize: 24,
                      fontWeight: FontWeight.w700,
                      height: 1.33,
                      letterSpacing: -0.53,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '设计资源与素材管理',
                    style: TextStyle(
                      color: AgentProfileTheme.labelColor,
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      height: 1.33,
                    ),
                  ),
                ],
              ),
            ),
            // 内容区域 - 开发中占位
            Expanded(
              child: Center(
                child: Padding(
                  padding: const EdgeInsets.all(48),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // 图标容器
                      Container(
                        width: 96,
                        height: 96,
                        decoration: BoxDecoration(
                          color: AgentProfileTheme.accentBlue.withOpacity(0.08),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          Icons.folder_open_rounded,
                          size: 44,
                          color: AgentProfileTheme.accentBlue.withOpacity(0.6),
                        ),
                      ),
                      const SizedBox(height: 24),
                      Text(
                        '功能开发中',
                        style: TextStyle(
                          color: AgentProfileTheme.titleColor,
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                          height: 1.4,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '设计规范、组件库、素材集\n即将上线，敬请期待',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: AgentProfileTheme.labelColor,
                          fontSize: 14,
                          fontWeight: FontWeight.w400,
                          height: 1.6,
                        ),
                      ),
                      const SizedBox(height: 32),
                      // 功能预告卡片
                      _buildFeaturePreviewCard(
                        icon: Icons.design_services_outlined,
                        title: '设计规范',
                        subtitle: '统一的设计系统与规范文档',
                      ),
                      const SizedBox(height: 12),
                      _buildFeaturePreviewCard(
                        icon: Icons.widgets_outlined,
                        title: '组件库',
                        subtitle: '可复用的 UI 组件与模板',
                      ),
                      const SizedBox(height: 12),
                      _buildFeaturePreviewCard(
                        icon: Icons.palette_outlined,
                        title: '素材集',
                        subtitle: '图标、插画、品牌素材管理',
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeaturePreviewCard({
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.68),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white, width: 1),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AgentProfileTheme.accentBlue.withOpacity(0.08),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(
              icon,
              size: 20,
              color: AgentProfileTheme.accentBlue,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    color: AgentProfileTheme.titleColor,
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: TextStyle(
                    color: AgentProfileTheme.labelColor,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Icon(
            Icons.lock_outline_rounded,
            size: 16,
            color: AgentProfileTheme.labelColor.withOpacity(0.5),
          ),
        ],
      ),
    );
  }
}
