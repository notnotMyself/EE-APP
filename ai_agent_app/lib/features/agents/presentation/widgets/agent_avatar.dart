import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../theme/agent_profile_theme.dart';

/// AI员工头像组件
/// 
/// 带阴影的头像，支持网络图片、本地资源和占位符
/// Figma规范: 154.13 x 158.15
class AgentAvatar extends StatelessWidget {
  final String? avatarUrl;
  final String? assetPath;  // 本地资源路径
  final double width;
  final double height;
  final String? fallbackText;

  const AgentAvatar({
    super.key,
    this.avatarUrl,
    this.assetPath,
    this.width = AgentProfileTheme.avatarWidth,
    this.height = AgentProfileTheme.avatarHeight,
    this.fallbackText,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        boxShadow: AgentProfileTheme.avatarShadow,
        borderRadius: BorderRadius.circular(width / 2),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(width / 2),
        child: _buildAvatarContent(),
      ),
    );
  }

  Widget _buildAvatarContent() {
    // 优先使用本地资源
    if (assetPath != null && assetPath!.isNotEmpty) {
      return Image.asset(
        assetPath!,
        width: width,
        height: height,
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) => _buildPlaceholder(),
      );
    }
    
    // 其次使用网络图片
    if (avatarUrl != null && avatarUrl!.isNotEmpty) {
      return CachedNetworkImage(
        imageUrl: avatarUrl!,
        width: width,
        height: height,
        fit: BoxFit.cover,
        placeholder: (context, url) => _buildPlaceholder(),
        errorWidget: (context, url, error) => _buildPlaceholder(),
      );
    }
    
    return _buildPlaceholder();
  }

  Widget _buildPlaceholder() {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: AgentProfileTheme.avatarPlaceholder,
        borderRadius: BorderRadius.circular(width / 2),
      ),
      child: Center(
        child: fallbackText != null
            ? Text(
                fallbackText!.substring(0, 1).toUpperCase(),
                style: TextStyle(
                  color: AgentProfileTheme.titleColor,
                  fontSize: width * 0.4,
                  fontWeight: FontWeight.bold,
                ),
              )
            : Icon(
                Icons.person,
                size: width * 0.5,
                color: AgentProfileTheme.labelColor,
              ),
      ),
    );
  }
}

