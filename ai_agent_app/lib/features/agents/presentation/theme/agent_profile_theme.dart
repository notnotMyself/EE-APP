import 'package:flutter/material.dart';

/// OPPO Sans 字体家族名称
const String oppoSansFamily = 'PingFang SC';

/// AI员工详情页面的设计规范
/// 基于 Figma 设计稿提取
class AgentProfileTheme {
  // ============================================
  // 颜色定义
  // ============================================
  
  /// 页面背景色
  static const Color backgroundColor = Color(0xFFE9EAF0);
  
  /// 主标题颜色（深蓝黑）
  static const Color titleColor = Color(0xFF0D1B34);
  
  /// 副标题/标签颜色（蓝灰色）
  static const Color labelColor = Color(0xFF8696BB);
  
  /// 主要文字颜色
  static const Color textPrimary = Color(0xE6000000); // 90% black
  
  /// 次要文字颜色
  static const Color textSecondary = Color(0x8A000000); // 54% black
  
  /// 三级文字颜色
  static const Color textTertiary = Color(0x42000000); // 26% black
  
  /// 卡片/按钮背景色（半透明白）
  static const Color cardBackground = Color(0xADFFFFFF); // 68% white
  
  /// 卡片边框色
  static const Color cardBorder = Colors.white;
  
  /// 头像占位背景色
  static const Color avatarPlaceholder = Color(0xFFD9D9D9);
  
  /// Chris Chen 头像资源路径
  static const String chrisChenAvatar = 'assets/images/chris_chen_avatar.jpeg';
  
  /// 强调色（蓝色）
  static const Color accentBlue = Color(0xFF378AFF);
  
  // ============================================
  // 字体样式 - 使用 OPPO Sans 字体
  // ============================================
  
  /// 问候语样式（"早上好"）
  static TextStyle get greetingStyle => const TextStyle(
    fontFamily: oppoSansFamily,
    color: labelColor,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1.20,
  );
  
  /// 用户名样式
  static TextStyle get userNameStyle => const TextStyle(
    fontFamily: oppoSansFamily,
    color: titleColor,
    fontSize: 20,
    fontWeight: FontWeight.w700,
    height: 1.10,
  );
  
  /// AI员工名称样式
  static TextStyle get agentNameStyle => const TextStyle(
    fontFamily: oppoSansFamily,
    color: titleColor,
    fontSize: 26,
    fontWeight: FontWeight.w700,
    height: 1.10,
  );
  
  /// AI员工描述样式
  static TextStyle get agentDescriptionStyle => const TextStyle(
    fontFamily: oppoSansFamily,
    color: textSecondary,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    height: 1.43,
  );
  
  /// 输入框提示文字样式
  static TextStyle get inputHintStyle => const TextStyle(
    fontFamily: oppoSansFamily,
    color: Colors.black,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1,
  );
  
  /// 快捷按钮标签样式
  static TextStyle get quickActionLabelStyle => const TextStyle(
    fontFamily: oppoSansFamily,
    color: labelColor,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1.20,
  );
  
  // ============================================
  // 尺寸定义
  // ============================================
  
  /// 头像尺寸 (Figma: 154.13 x 158.15)
  static const double avatarWidth = 154.0;
  static const double avatarHeight = 158.0;
  /// 兼容旧代码
  static const double avatarSize = 154.0;
  
  /// 快捷按钮尺寸
  static const double quickActionSize = 72.0;
  
  /// 快捷按钮图标尺寸
  static const double quickActionIconSize = 24.0;
  
  /// 输入框高度
  static const double inputHeight = 56.0;
  
  /// 页面水平内边距
  static const double horizontalPadding = 16.0;
  
  /// 快捷按钮间距
  static const double quickActionSpacing = 13.0;
  
  // ============================================
  // 装饰样式
  // ============================================
  
  /// 头像阴影
  static List<BoxShadow> get avatarShadow => const [
    BoxShadow(
      color: Color(0x19000000),
      blurRadius: 32,
      offset: Offset(0, 6),
      spreadRadius: 0,
    ),
  ];
  
  /// 卡片/按钮装饰
  static ShapeDecoration get cardDecoration => ShapeDecoration(
    color: cardBackground,
    shape: RoundedRectangleBorder(
      side: const BorderSide(width: 1, color: cardBorder),
      borderRadius: BorderRadius.circular(100),
    ),
  );
  
  /// 快捷按钮装饰
  static ShapeDecoration get quickActionDecoration => ShapeDecoration(
    color: cardBackground,
    shape: RoundedRectangleBorder(
      side: const BorderSide(width: 1, color: cardBorder),
      borderRadius: BorderRadius.circular(100),
    ),
  );
}

