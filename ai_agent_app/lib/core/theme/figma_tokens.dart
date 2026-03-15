import 'package:flutter/material.dart';

/// Figma 设计稿语义 Token 映射
///
/// 所有数值直接从 Figma 设计稿提取，作为 Single Source of Truth。
/// 组件代码应引用此处的常量，而非硬编码。
class FigmaTokens {
  FigmaTokens._();

  // ============================================
  // 颜色 Token
  // ============================================

  // --- 中性色/文本&图标（黑） ---

  /// 90% black - "90 · Primary"
  static const Color labelPrimary = Color(0xE6000000);

  /// 54% black - "54 · Secondary"
  static const Color labelSecondary = Color(0x8A000000);

  /// 26% black - "26 · Tertiary"
  static const Color labelTertiary = Color(0x42000000);

  /// 16% black - "互联网专用 40"
  static const Color labelQuaternary = Color(0x29000000);

  /// 35% black - 输入框占位文字
  static const Color labelPlaceholder = Color(0x59000000);

  // --- 中性色/填充色 ---

  /// 4% black - "4 · Thin" (按钮/卡片背景)
  static const Color containerThin = Color(0x0A000000);

  // --- 中性色/文本&图标（白） ---

  /// White · On Color
  static const Color onColorWhite = Colors.white;

  // --- 品牌色 ---

  /// 用户消息蓝 (#2C69FF)
  static const Color brandBlue = Color(0xFF2C69FF);

  // --- 背景色 ---

  /// 页面背景 (Figma: #F0F1F2)
  static const Color backgroundGray = Color(0xFFF0F1F2);

  // ============================================
  // 字体 Token
  // ============================================

  /// 主字体 (Figma: OPPO Sans 4.0)
  static const String fontPrimary = 'OPPO Sans 4.0';

  /// 辅助字体 (Figma: OPlus Sans SC 3.5)
  static const String fontSecondary = 'OPlus Sans SC 3.5';

  // --- Body/L 样式 ---

  /// Body/L · Regular - 16px, 400, lineHeight 1.4em
  static const TextStyle bodyLRegular = TextStyle(
    fontFamily: fontPrimary,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1.4,
  );

  /// Body/L · Medium - 16px, 500, lineHeight 1.5em
  static const TextStyle bodyLMedium = TextStyle(
    fontFamily: fontPrimary,
    fontSize: 16,
    fontWeight: FontWeight.w500,
    height: 1.5,
  );

  // --- Body/M 样式 ---

  /// Body/M · Regular - 14px, 400, lineHeight 1.4em
  static const TextStyle bodyMRegular = TextStyle(
    fontFamily: fontPrimary,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    height: 1.4,
  );

  // --- 标题样式 ---

  /// Title/M · Medium - 18px, 500, lineHeight 1.44em
  static const TextStyle titleMMedium = TextStyle(
    fontFamily: fontPrimary,
    fontSize: 18,
    fontWeight: FontWeight.w500,
    height: 1.44,
  );

  // ============================================
  // 消息气泡 Token
  // ============================================

  /// 消息卡片圆角 (Figma: 12px)
  static const double radiusMessage = 12.0;

  /// 按钮/胶囊圆角 (Figma: 80px / 90px)
  static const double radiusPill = 80.0;

  /// 操作按钮尺寸 (Figma: 32x32)
  static const double actionButtonSize = 32.0;

  /// 操作按钮图标尺寸 (Figma: 16x16)
  static const double actionButtonIconSize = 16.0;

  /// 用户消息内容区最大宽度 (Figma: 240dp)
  static const double userMessageContentWidth = 240.0;

  /// 用户消息气泡水平 padding (Figma: 16dp)
  static const double messagePaddingH = 16.0;

  /// 用户消息气泡顶部 padding (Figma: 12dp)
  static const double messagePaddingTop = 12.0;

  /// 用户消息气泡底部 padding (Figma: 16dp)
  static const double messagePaddingBottom = 16.0;

  /// 用户消息气泡总宽度 = 内容 240 + padding 16*2 = 272dp
  static const double userMessageMaxWidth = 272.0;

  /// AI 消息固定宽度 (Figma: 328dp)
  static const double aiMessageWidth = 328.0;

  /// AI 消息内容区宽度 = 328 - 16*2 = 296dp
  static const double aiMessageContentWidth = 296.0;

  /// 消息内部元素间距 (Figma: gap 8px)
  static const double messageGap = 8.0;

  // ============================================
  // 用户消息文字样式
  // ============================================

  /// 用户消息文字 (Figma: OPlus Sans SC 3.5, 500, 16px, 1.5em, white, justified)
  static const TextStyle userMessageText = TextStyle(
    fontFamily: fontSecondary,
    fontSize: 16,
    fontWeight: FontWeight.w500,
    height: 1.5,
    color: onColorWhite,
  );

  // ============================================
  // AI 消息文字样式
  // ============================================

  /// AI 消息文字 (Figma: OPPO Sans 4.0, 400, 16px, 1.4em, 90% black, left-align)
  static const TextStyle aiMessageText = TextStyle(
    fontFamily: fontPrimary,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1.4,
    color: labelPrimary,
  );

  // ============================================
  // 阴影 Token
  // ============================================

  /// AI 消息气泡阴影 (Figma: 0px 2px 8px rgba(0,0,0,0.04))
  static const BoxShadow messageShadow = BoxShadow(
    color: Color(0x0A000000),
    blurRadius: 8,
    offset: Offset(0, 2),
  );

  // ============================================
  // 导航栏 Token
  // ============================================

  /// 导航栏高度 (Figma: 52dp)
  static const double navBarHeight = 52.0;

  /// 导航栏按钮尺寸 (Figma: 40x40)
  static const double navButtonSize = 40.0;

  /// 导航栏按钮触摸区域 (48dp)
  static const double navButtonTouchArea = 48.0;

  // ============================================
  // 输入框 Token
  // ============================================

  /// 输入框高度 (Figma: 48dp)
  static const double inputHeight = 48.0;

  /// 输入框圆角 (Figma: 24dp)
  static const double inputRadius = 24.0;

  /// 附件缩略图尺寸 (Figma: 43x43)
  static const double thumbnailSize = 43.0;

  /// 附件缩略图圆角 (Figma: 4px)
  static const double thumbnailRadius = 4.0;

  /// 附件缩略图间距 (Figma: 3px)
  static const double thumbnailSpacing = 3.0;
}
