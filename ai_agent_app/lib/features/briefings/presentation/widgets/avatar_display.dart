import 'package:flutter/material.dart';
import '../../domain/models/secretary.dart';

class AvatarDisplay extends StatelessWidget {
  final Secretary secretary;

  const AvatarDisplay({
    super.key,
    required this.secretary,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 120,
      height: 120,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Glow effect
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: Colors.blue.withOpacity(0.2),
                  blurRadius: 30,
                  spreadRadius: 10,
                ),
              ],
            ),
          ),
          // Avatar
          if (secretary.animatedAvatar != null)
             Image.asset(
               secretary.animatedAvatar!,
               fit: BoxFit.contain,
               errorBuilder: (context, error, stackTrace) =>
                   _buildStaticAvatar(),
             )
          else
            _buildStaticAvatar(),
        ],
      ),
    );
  }

  Widget _buildStaticAvatar() {
    return CircleAvatar(
      radius: 50,
      backgroundImage: AssetImage(secretary.avatar),
      backgroundColor: Colors.transparent,
    );
  }
}
