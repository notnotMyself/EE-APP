import 'package:flutter/material.dart';
import '../../domain/models/secretary.dart';

class RoleDial extends StatelessWidget {
  final List<Map<String, dynamic>> visibleAgents;
  final int activeIndex;
  final ValueChanged<int> onSelect;

  const RoleDial({
    super.key,
    required this.visibleAgents,
    required this.activeIndex,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: Colors.white.withOpacity(0.2)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: List.generate(visibleAgents.length, (index) {
          final isLast = index == visibleAgents.length - 1;
          return Padding(
            padding: EdgeInsets.only(bottom: isLast ? 0 : 6),
            child: _buildRoleButton(context, index),
          );
        }),
      ),
    );
  }

  Widget _buildRoleButton(BuildContext context, int index) {
    final isActive = index == activeIndex;
    final agentData = visibleAgents[index];
    final secretary = agentData['secretary'] as Secretary;

    return GestureDetector(
      onTap: () => onSelect(index),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        width: isActive ? 40 : 36,
        height: isActive ? 40 : 36,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          border: Border.all(
            color: isActive ? Colors.blue.shade400 : Colors.white.withOpacity(0.3),
            width: 2,
          ),
          boxShadow: isActive
              ? [
                  BoxShadow(
                    color: Colors.blue.withOpacity(0.3),
                    blurRadius: 8,
                    spreadRadius: 2,
                  )
                ]
              : [],
        ),
        child: Stack(
          clipBehavior: Clip.none,
          children: [
            ClipOval(
              child: Image.asset(
                secretary.avatar,
                fit: BoxFit.cover,
                width: double.infinity,
                height: double.infinity,
                errorBuilder: (context, error, stackTrace) =>
                    const Icon(Icons.person, color: Colors.grey),
              ),
            ),
            if (isActive)
              Positioned(
                right: -1,
                top: -1,
                child: Container(
                  width: 10,
                  height: 10,
                  decoration: BoxDecoration(
                    color: Colors.greenAccent,
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 2),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.greenAccent.withOpacity(0.5),
                        blurRadius: 4,
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
