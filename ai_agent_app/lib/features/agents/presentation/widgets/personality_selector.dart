import 'package:flutter/material.dart';

/// OPPO Sans 字体家族名称
const String _oppoSansFamily = 'OPPO Sans';

/// 人物个性数据模型
class Personality {
  final String id;
  final String name;
  final IconData icon;

  const Personality({
    required this.id,
    required this.name,
    required this.icon,
  });
}

/// 预定义的人物个性（按Figma设计）
class PersonalityList {
  static const defaultPersonality = Personality(
    id: 'default',
    name: '默认',
    icon: Icons.person_outline,
  );

  static const friendly = Personality(
    id: 'friendly',
    name: '亲和友善',
    icon: Icons.sentiment_satisfied_alt_outlined,
  );

  static const straightforward = Personality(
    id: 'straightforward',
    name: '直言不讳',
    icon: Icons.record_voice_over_outlined,
  );

  static const professional = Personality(
    id: 'professional',
    name: '专业可靠',
    icon: Icons.verified_outlined,
  );

  static const creative = Personality(
    id: 'creative',
    name: '天马行空',
    icon: Icons.auto_awesome_outlined,
  );

  /// 所有个性
  static List<Personality> get all => [
        defaultPersonality,
        friendly,
        straightforward,
        professional,
        creative,
      ];
}

/// 人物个性选择弹窗内容
class PersonalitySelectorPopup extends StatelessWidget {
  final Personality? selectedPersonality;
  final ValueChanged<Personality> onPersonalitySelected;
  final String? agentName;

  const PersonalitySelectorPopup({
    super.key,
    this.selectedPersonality,
    required this.onPersonalitySelected,
    this.agentName,
  });

  @override
  Widget build(BuildContext context) {
    final displayName = agentName ?? 'AI';
    
    return ConstrainedBox(
      constraints: const BoxConstraints(minWidth: 168, maxWidth: 256),
      child: Container(
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
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 标题
            Padding(
              padding: const EdgeInsets.only(top: 12, left: 20, right: 20),
              child: SizedBox(
                width: 156,
                child: Text(
                  '选择 $displayName 人物个性',
                  style: TextStyle(
                    color: Colors.black.withOpacity(0.54),
                    fontSize: 12,
                    fontFamily: _oppoSansFamily,
                    fontWeight: FontWeight.w500,
                    height: 1.33,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 7),

            // 个性列表
            ...PersonalityList.all.map((personality) => _buildItem(context, personality)),
            const SizedBox(height: 8),
          ],
        ),
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
        padding: const EdgeInsets.symmetric(horizontal: 8),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Row(
            children: [
              // 左侧图标
              Container(
                width: 20,
                height: 20,
                clipBehavior: Clip.antiAlias,
                decoration: const BoxDecoration(),
                child: Icon(
                  personality.icon,
                  size: 20,
                  color: isSelected
                      ? const Color(0xFF0066FF)
                      : Colors.black.withOpacity(0.54),
                ),
              ),
              const SizedBox(width: 12),
              // 文字
              Expanded(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(minHeight: 40),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            personality.name,
                            style: TextStyle(
                              color: isSelected
                                  ? const Color(0xFF0066FF)
                                  : Colors.black.withOpacity(0.90),
                              fontSize: 16,
                              fontFamily: _oppoSansFamily,
                              fontWeight: FontWeight.w400,
                              height: 1.38,
                            ),
                          ),
                        ),
                        // 选中勾选图标
                        if (isSelected)
                          Container(
                            width: 20,
                            height: 20,
                            child: const Icon(
                              Icons.check,
                              size: 20,
                              color: Color(0xFF0066FF),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
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
  String? agentName,
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
          agentName: agentName,
        ),
      ),
    ],
  );

  return result;
}

