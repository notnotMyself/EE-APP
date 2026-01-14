import 'package:flutter/material.dart';
import '../controllers/home_provider.dart';

class ViewToggle extends StatelessWidget {
  final ViewMode mode;
  final ValueChanged<ViewMode> onToggle;

  const ViewToggle({
    super.key,
    required this.mode,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      padding: const EdgeInsets.all(4),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildButton(
            context,
            icon: Icons.layers_outlined,
            isSelected: mode == ViewMode.cards,
            onTap: () => onToggle(ViewMode.cards),
          ),
          _buildButton(
            context,
            icon: Icons.grid_view,
            isSelected: mode == ViewMode.grid,
            onTap: () => onToggle(ViewMode.grid),
          ),
        ],
      ),
    );
  }

  Widget _buildButton(
    BuildContext context, {
    required IconData icon,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: isSelected ? Colors.blue.shade400 : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
          gradient: isSelected
              ? const LinearGradient(
                  colors: [Color(0xFF60A5FA), Color(0xFF3B82F6)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                )
              : null,
        ),
        child: Icon(
          icon,
          size: 20,
          color: isSelected ? Colors.white : Colors.black54,
        ),
      ),
    );
  }
}
