import 'package:flutter/material.dart';

/// 人物个性数据模型
class Personality {
  final String id;
  final String name;
  final String? description;

  const Personality({
    required this.id,
    required this.name,
    this.description,
  });
}

/// 预定义的人物个性
class PersonalityList {
  static const defaultPersonality = Personality(
    id: 'default',
    name: '默认',
    description: '专业、严谨的设计评审风格',
  );

  static const friendly = Personality(
    id: 'friendly',
    name: '亲和',
    description: '温和友好，循循善诱',
  );

  static const strict = Personality(
    id: 'strict',
    name: '严格',
    description: '高标准、严要求',
  );

  static const creative = Personality(
    id: 'creative',
    name: '创意',
    description: '天马行空，激发灵感',
  );

  static const mentor = Personality(
    id: 'mentor',
    name: '导师',
    description: '耐心指导，传授经验',
  );

  /// 所有个性
  static List<Personality> get all => [
        defaultPersonality,
        friendly,
        strict,
        creative,
        mentor,
      ];
}

/// 人物个性选择弹窗
class PersonalitySelectorPopup extends StatelessWidget {
  final Personality? selectedPersonality;
  final ValueChanged<Personality> onPersonalitySelected;

  const PersonalitySelectorPopup({
    super.key,
    this.selectedPersonality,
    required this.onPersonalitySelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 196,
      padding: const EdgeInsets.only(top: 12, left: 20, right: 20, bottom: 8),
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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题
          Text(
            '选择 Chris 人物个性',
            style: TextStyle(
              color: Colors.black.withOpacity(0.54),
              fontSize: 12,
              fontWeight: FontWeight.w500,
              height: 1.33,
            ),
          ),
          const SizedBox(height: 7),

          // 个性列表
          ...PersonalityList.all.map((personality) => _buildItem(context, personality)),
        ],
      ),
    );
  }

  Widget _buildItem(BuildContext context, Personality personality) {
    final isSelected = selectedPersonality?.id == personality.id;

    return GestureDetector(
      onTap: () {
        onPersonalitySelected(personality);
        Navigator.of(context).pop();
      },
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 10),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    personality.name,
                    style: TextStyle(
                      color: Colors.black.withOpacity(0.90),
                      fontSize: 16,
                      fontWeight: FontWeight.w400,
                      height: 1.38,
                    ),
                  ),
                  if (personality.description != null)
                    Text(
                      personality.description!,
                      style: TextStyle(
                        color: Colors.black.withOpacity(0.54),
                        fontSize: 12,
                        fontWeight: FontWeight.w400,
                      ),
                    ),
                ],
              ),
            ),
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

/// 显示人物个性选择弹窗
Future<Personality?> showPersonalitySelectorPopup(
  BuildContext context, {
  Personality? selectedPersonality,
  required RelativeRect position,
}) async {
  Personality? result;

  await showMenu<Personality>(
    context: context,
    position: position,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(24),
    ),
    color: Colors.transparent,
    elevation: 0,
    items: [
      PopupMenuItem<Personality>(
        enabled: false,
        padding: EdgeInsets.zero,
        child: PersonalitySelectorPopup(
          selectedPersonality: selectedPersonality,
          onPersonalitySelected: (p) {
            result = p;
          },
        ),
      ),
    ],
  );

  return result;
}

