import 'package:flutter/material.dart';

/// 附件类型
enum AttachmentType {
  image,    // 图片
  file,     // 文件
  figma,    // Figma 链接
}

/// 附件菜单选项
class AttachmentOption {
  final AttachmentType type;
  final String label;
  final IconData icon;

  const AttachmentOption({
    required this.type,
    required this.label,
    required this.icon,
  });
}

/// 预定义的附件选项
class AttachmentOptions {
  static const image = AttachmentOption(
    type: AttachmentType.image,
    label: '图片',
    icon: Icons.image_outlined,
  );

  static const file = AttachmentOption(
    type: AttachmentType.file,
    label: '文件',
    icon: Icons.insert_drive_file_outlined,
  );

  static const figma = AttachmentOption(
    type: AttachmentType.figma,
    label: 'Figma 链接',
    icon: Icons.link,
  );

  static List<AttachmentOption> get all => [image, file, figma];
}

/// 附件菜单弹窗
class AttachmentMenuPopup extends StatelessWidget {
  final ValueChanged<AttachmentType> onOptionSelected;

  const AttachmentMenuPopup({
    super.key,
    required this.onOptionSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 196,
      padding: const EdgeInsets.symmetric(vertical: 8),
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
        children: AttachmentOptions.all
            .map((option) => _buildOptionItem(context, option))
            .toList(),
      ),
    );
  }

  Widget _buildOptionItem(BuildContext context, AttachmentOption option) {
    return GestureDetector(
      onTap: () {
        onOptionSelected(option.type);
        Navigator.of(context).pop();
      },
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
        child: Row(
          children: [
            // 图标
            Icon(
              option.icon,
              size: 20,
              color: Colors.black.withOpacity(0.7),
            ),
            const SizedBox(width: 12),
            // 标签
            Expanded(
              child: Text(
                option.label,
                style: TextStyle(
                  color: Colors.black.withOpacity(0.90),
                  fontSize: 16,
                  fontWeight: FontWeight.w400,
                  height: 1.38,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// 显示附件菜单弹窗
Future<AttachmentType?> showAttachmentMenuPopup(
  BuildContext context, {
  required RelativeRect position,
}) async {
  AttachmentType? result;

  await showMenu<AttachmentType>(
    context: context,
    position: position,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(24),
    ),
    color: Colors.transparent,
    elevation: 0,
    items: [
      PopupMenuItem<AttachmentType>(
        enabled: false,
        padding: EdgeInsets.zero,
        child: AttachmentMenuPopup(
          onOptionSelected: (type) {
            result = type;
          },
        ),
      ),
    ],
  );

  return result;
}

