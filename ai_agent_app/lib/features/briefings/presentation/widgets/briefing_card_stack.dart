import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../../domain/models/briefing.dart';
import 'briefing_stack_card.dart';

/// 堆叠卡片容器，处理手势和堆叠动画
class BriefingCardStack extends StatefulWidget {
  const BriefingCardStack({
    super.key,
    required this.briefings,
    required this.dismissedIds,
    required this.onCardDismissed,
    required this.onCardAction,
  });

  final List<Briefing> briefings;
  final Set<String> dismissedIds;
  final Function(Briefing briefing) onCardDismissed;
  final Function(Briefing briefing) onCardAction;

  @override
  State<BriefingCardStack> createState() => _BriefingCardStackState();
}

class _BriefingCardStackState extends State<BriefingCardStack> with TickerProviderStateMixin {
  // 顶部卡片的偏移量
  Offset _dragOffset = Offset.zero;
  AnimationController? _slideBackController;
  AnimationController? _dismissController;

  // 获取当前可见的卡片列表（过滤掉已移除的）
  List<Briefing> get _visibleBriefings => widget.briefings
      .where((b) => !widget.dismissedIds.contains(b.id))
      .toList();

  @override
  void dispose() {
    _slideBackController?.dispose();
    _dismissController?.dispose();
    super.dispose();
  }

  // 移除 didUpdateWidget - 让 _dismissedIds 保持状态，直到 widget 重新创建（key 变化）

  void _onPanStart(DragStartDetails details) {
    if (_slideBackController?.isAnimating ?? false) {
      _slideBackController!.stop();
    }
  }

  void _onPanUpdate(DragUpdateDetails details) {
    setState(() {
      _dragOffset += details.delta;
    });
  }

  void _onPanEnd(DragEndDetails details) {
    final size = MediaQuery.of(context).size;

    // 触发移除的阈值（屏幕宽度的 40%）
    if (_dragOffset.dx.abs() > size.width * 0.4) {
      _dismissCard(_dragOffset.dx > 0);
    } else {
      _slideBack();
    }
  }

  void _slideBack() {
    _slideBackController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );

    final startOffset = _dragOffset;

    final animation = Tween<Offset>(
      begin: startOffset,
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _slideBackController!,
      curve: Curves.easeOutBack,
    ));

    animation.addListener(() {
      setState(() {
        _dragOffset = animation.value;
      });
    });

    _slideBackController!.forward();
  }

  void _dismissCard(bool isRight) {
    final size = MediaQuery.of(context).size;
    final endX = isRight ? size.width * 1.5 : -size.width * 1.5;

    _dismissController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 200),
    );

    final startOffset = _dragOffset;

    final animation = Tween<Offset>(
      begin: startOffset,
      end: Offset(endX, startOffset.dy),
    ).animate(CurvedAnimation(
      parent: _dismissController!,
      curve: Curves.easeOut,
    ));

    animation.addListener(() {
      setState(() {
        _dragOffset = animation.value;
      });
    });

    animation.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        final currentTop = _visibleBriefings.first;
        widget.onCardDismissed(currentTop);

        setState(() {
          _dragOffset = Offset.zero;
        });

        _dismissController?.dispose();
        _dismissController = null;
      }
    });

    _dismissController!.forward();
  }

  @override
  Widget build(BuildContext context) {
    final visibleItems = _visibleBriefings;

    if (visibleItems.isEmpty) {
      return _buildEmptyState();
    }

    // 只渲染前3张卡片以保证性能
    final renderItems = visibleItems.take(3).toList().reversed.toList();

    return Stack(
      alignment: Alignment.center,
      children: renderItems.map((item) {
        final index = visibleItems.indexOf(item);
        return _buildCard(item, index);
      }).toList(),
    );
  }

  Widget _buildCard(Briefing item, int index) {
    final isTop = index == 0;

    double yOffset = 0;
    double scale = 1.0;

    if (!isTop) {
      yOffset = index * 15.0;
      scale = 1.0 - (index * 0.06);

      if (_dragOffset.dx != 0) {
        final progress = math.min(_dragOffset.dx.abs() / 200.0, 1.0);
        yOffset -= 15.0 * progress;
        scale += 0.06 * progress;
      }
    }

    Matrix4 transform = Matrix4.identity();
    if (isTop) {
      transform.translate(_dragOffset.dx, _dragOffset.dy);
      final rotation = _dragOffset.dx / 1000.0;
      transform.rotateZ(rotation);
    } else {
      transform.translate(0.0, yOffset);
      transform.scale(scale);
    }

    // 动态计算卡片高度：屏幕高度 - 顶部空间 - 底部按钮空间
    final screenHeight = MediaQuery.of(context).size.height;
    final topSpace = 200.0; // 顶部 Header + Avatar 区域
    final bottomSpace = 120.0; // 底部聊天栏
    final maxCardHeight = screenHeight - topSpace - bottomSpace;
    final cardHeight = math.min(480.0, maxCardHeight); // 最大 480，但不超过可用空间

    return Transform(
      transform: transform,
      alignment: Alignment.bottomCenter,
      child: GestureDetector(
        onPanStart: isTop ? _onPanStart : null,
        onPanUpdate: isTop ? _onPanUpdate : null,
        onPanEnd: isTop ? _onPanEnd : null,
        child: SizedBox(
          height: cardHeight,
          width: MediaQuery.of(context).size.width * 0.92,
          child: BriefingStackCard(
            briefing: item,
            onTap: () {
              if (isTop) {
                widget.onCardAction(item);
              }
            },
            onAction: () {
              if (isTop) {
                widget.onCardAction(item);
              }
            },
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      height: 300,
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withOpacity(0.2)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.check_circle_outline,
            size: 48,
            color: Colors.white.withOpacity(0.5),
          ),
          const SizedBox(height: 16),
          Text(
            '暂无更新',
            style: TextStyle(
              color: Colors.white.withOpacity(0.7),
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '稍后再来看看吧！',
            style: TextStyle(
              color: Colors.white.withOpacity(0.5),
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }
}
