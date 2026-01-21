import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../theme/agent_profile_theme.dart';

/// AI员工头像组件
/// 
/// 带阴影的圆形头像，支持网络图片和占位符
class AgentAvatar extends StatelessWidget {
  final String? avatarUrl;
  final double size;
  final String? fallbackText;

  const AgentAvatar({
    super.key,
    this.avatarUrl,
    this.size = AgentProfileTheme.avatarSize,
    this.fallbackText,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        boxShadow: AgentProfileTheme.avatarShadow,
        shape: BoxShape.circle,
      ),
      child: ClipOval(
        child: _buildAvatarContent(),
      ),
    );
  }

  Widget _buildAvatarContent() {
    if (avatarUrl != null && avatarUrl!.isNotEmpty) {
      return CachedNetworkImage(
        imageUrl: avatarUrl!,
        width: size,
        height: size,
        fit: BoxFit.cover,
        placeholder: (context, url) => _buildPlaceholder(),
        errorWidget: (context, url, error) => _buildPlaceholder(),
      );
    }
    return _buildPlaceholder();
  }

  Widget _buildPlaceholder() {
    return Container(
      width: size,
      height: size,
      decoration: const BoxDecoration(
        color: AgentProfileTheme.avatarPlaceholder,
        shape: BoxShape.circle,
      ),
      child: Center(
        child: fallbackText != null
            ? Text(
                fallbackText!.substring(0, 1).toUpperCase(),
                style: TextStyle(
                  color: AgentProfileTheme.titleColor,
                  fontSize: size * 0.4,
                  fontWeight: FontWeight.bold,
                ),
              )
            : Icon(
                Icons.person,
                size: size * 0.5,
                color: AgentProfileTheme.labelColor,
              ),
      ),
    );
  }
}

