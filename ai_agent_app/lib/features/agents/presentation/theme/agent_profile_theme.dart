import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../../core/theme/figma_tokens.dart';

/// OPPO Sans 字体家族名称（Figma: OPPO Sans 4.0）
const String oppoSansFamily = FigmaTokens.fontPrimary;

/// AI员工详情页面的设计规范
/// 基于 Figma 设计稿提取
class AgentProfileTheme {
  // ============================================
  // 颜色定义 (引用 FigmaTokens)
  // ============================================

  /// 页面背景色 (Figma: 中性色/背景色/BG Gray #F0F1F2)
  static const Color backgroundColor = FigmaTokens.backgroundGray;

  /// 主标题颜色（深蓝黑）
  static const Color titleColor = Color(0xFF0D1B34);

  /// 副标题/标签颜色（蓝灰色）
  static const Color labelColor = Color(0xFF8696BB);

  /// 主要文字颜色
  static const Color textPrimary = FigmaTokens.labelPrimary;

  /// 次要文字颜色
  static const Color textSecondary = FigmaTokens.labelSecondary;

  /// 三级文字颜色
  static const Color textTertiary = FigmaTokens.labelTertiary;
  
  /// 卡片/按钮背景色（半透明白，Figma: white 68%）
  static const Color cardBackground = Color(0xADFFFFFF); // 68% white

  /// 卡片边框色（Figma: white）
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
  
  /// AI员工名称样式 (Figma: Poppins 700, 26px, lineHeight 1.1em, #0D1B34)
  static TextStyle get agentNameStyle => GoogleFonts.poppins(
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
  
  /// 输入框提示文字样式 (Figma: Body/L · Regular)
  static TextStyle get inputHintStyle => const TextStyle(
    fontFamily: oppoSansFamily,
    color: Colors.black,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1.375,
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
  
  /// 头像尺寸 (Figma: 130x130 visible circle, image 154x158 overflows)
  static const double avatarWidth = 130.0;
  static const double avatarHeight = 130.0;
  /// 兼容旧代码
  static const double avatarSize = 130.0;
  
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

