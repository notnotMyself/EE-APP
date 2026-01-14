import 'package:flutter/material.dart';
import 'dart:ui';
import '../../domain/models/briefing.dart';

/// Glassmorphism 风格的堆叠卡片组件
class BriefingStackCard extends StatelessWidget {
  const BriefingStackCard({
    super.key,
    required this.briefing,
    required this.onTap,
    required this.onAction,
  });

  final Briefing briefing;
  final VoidCallback onTap;
  final VoidCallback onAction;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    // 映射类型到渐变色
    final gradientColors = _getGradientColors(briefing.briefingType);
    final borderColor = _getBorderColor(briefing.briefingType);

    // 获取第一个操作作为主操作，或者默认操作
    final mainActionLabel = briefing.actions.isNotEmpty
        ? briefing.actions.first.label
        : 'Action';

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: gradientColors,
              ),
              border: Border.all(
                color: borderColor,
                width: 1,
              ),
            ),
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 头部：Avatar + Title
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildAvatar(),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            briefing.agentName ?? 'AI Assistant',
                            style: theme.textTheme.labelMedium?.copyWith(
                              color: Colors.white.withOpacity(0.6),
                              fontWeight: FontWeight.bold,
                              letterSpacing: 1.0,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            briefing.title,
                            style: theme.textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                              height: 1.2,
                              color: Colors.white.withOpacity(0.95),
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                    _buildTime(briefing.createdAt),
                  ],
                ),

                const SizedBox(height: 20),

                // 内容区域 (带图片背景)
                Expanded(
                  child: Container(
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.05),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Stack(
                      children: [
                        // 渐变遮罩，保证文字清晰
                        Container(
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(16),
                            gradient: LinearGradient(
                              begin: Alignment.topCenter,
                              end: Alignment.bottomCenter,
                              colors: [
                                Colors.transparent,
                                Colors.black.withOpacity(0.8),
                              ],
                              stops: const [0.3, 1.0],
                            ),
                          ),
                        ),
                        // 摘要内容
                        Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.end,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                briefing.summary,
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  color: Colors.white.withOpacity(0.9),
                                  height: 1.5,
                                  fontWeight: FontWeight.w500,
                                ),
                                maxLines: 4,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 20),

                // 底部按钮区域
                Row(
                  children: [
                    // Details Button
                    Expanded(
                      child: GestureDetector(
                        onTap: onTap,
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(
                              color: Colors.white.withOpacity(0.1),
                            ),
                          ),
                          child: const Center(
                            child: Text(
                              'Details',
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    // Action Button
                    Expanded(
                      child: GestureDetector(
                        onTap: onAction,
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          decoration: BoxDecoration(
                            color: theme.colorScheme.primary,
                            borderRadius: BorderRadius.circular(16),
                            boxShadow: [
                              BoxShadow(
                                color: theme.colorScheme.primary.withOpacity(0.4),
                                blurRadius: 12,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: Center(
                            child: Text(
                              mainActionLabel,
                              style: TextStyle(
                                color: theme.colorScheme.onPrimary,
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildAvatar() {
    if (briefing.agentAvatarUrl != null) {
      final assetPath = _getAssetForAgent(briefing.agentId);
      if (assetPath != null) {
        return Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.2),
            shape: BoxShape.circle,
          ),
          padding: const EdgeInsets.all(2),
          child: ClipOval(
            child: Image.asset(
              assetPath,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) => _buildDefaultAvatar(),
            ),
          ),
        );
      }
    }

    return _buildDefaultAvatar();
  }

  Widget _buildDefaultAvatar() {
    return Container(
      width: 44,
      height: 44,
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        shape: BoxShape.circle,
      ),
      child: Center(
        child: Icon(
          Icons.person,
          color: Colors.white.withOpacity(0.8),
        ),
      ),
    );
  }

  String? _getAssetForAgent(String agentId) {
    if (agentId.contains('dev')) {
      return 'assets/images/secretary-girl-avatar.png';
    } else if (agentId.contains('business')) {
      return 'assets/images/secretary-woman-avatar.png';
    } else {
      return 'assets/images/secretary-boy-avatar.png';
    }
  }

  Widget _buildTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);
    String timeStr;

    if (diff.inMinutes < 60) {
      timeStr = '${diff.inMinutes}m ago';
    } else if (diff.inHours < 24) {
      timeStr = '${diff.inHours}h ago';
    } else {
      timeStr = '${diff.inDays}d ago';
    }

    return Row(
      children: [
        Icon(
          Icons.access_time,
          size: 12,
          color: Colors.white.withOpacity(0.5),
        ),
        const SizedBox(width: 4),
        Text(
          timeStr,
          style: TextStyle(
            color: Colors.white.withOpacity(0.5),
            fontSize: 12,
            fontFamily: 'monospace',
          ),
        ),
      ],
    );
  }

  // 背景渐变：根据 BriefingType
  List<Color> _getGradientColors(BriefingType type) {
    const baseWhite = Color(0x1AFFFFFF); // white/10

    switch (type) {
      case BriefingType.alert:
        return [baseWhite, const Color(0x0DFF0000)]; // red/5
      case BriefingType.insight:
        return [baseWhite, const Color(0x0DA020F0)]; // purple/5
      case BriefingType.summary:
      case BriefingType.action:
        return [baseWhite, const Color(0x0D0000FF)]; // blue/5
    }
  }

  Color _getBorderColor(BriefingType type) {
    switch (type) {
      case BriefingType.alert:
        return const Color(0x33FFCDD2); // red-200/20
      case BriefingType.insight:
        return const Color(0x33E1BEE7); // purple-200/20
      case BriefingType.summary:
      case BriefingType.action:
        return const Color(0x33BBDEFB); // blue-200/20
    }
  }
}
