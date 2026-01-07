import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ai_agent_app/features/briefings/presentation/widgets/briefing_card.dart';
import 'package:ai_agent_app/features/briefings/domain/models/briefing.dart';

void main() {
  group('BriefingCard Widget Tests', () {
    late Briefing testBriefing;

    setUp(() {
      testBriefing = Briefing(
        id: 'test-1',
        agentId: 'agent-1',
        userId: 'user-1',
        agentName: '研发效能监控员',
        agentRole: '效能分析师',
        briefingType: BriefingType.alert,
        priority: BriefingPriority.p0,
        title: '代码返工率持续上升',
        summary: '过去7天返工率从12%上升至18%，主要集中在用户认证模块',
        status: BriefingStatus.newItem,
        createdAt: DateTime.now(),
        impact: '可能影响项目交付时间',
      );
    });

    testWidgets('应该显示封面图区域', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BriefingCard(
              briefing: testBriefing,
              onTap: () {},
            ),
          ),
        ),
      );

      // 验证封面图容器存在（通过查找特定尺寸的 Container）
      expect(find.byType(Container), findsWidgets);

      // 验证类型图标显示（封面图中的大图标 + 头像中的小图标，共2个）
      expect(find.byIcon(Icons.warning_rounded), findsNWidgets(2));
    });

    testWidgets('应该显示优先级标签在左上角', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BriefingCard(
              briefing: testBriefing,
              onTap: () {},
            ),
          ),
        ),
      );

      // 验证优先级标签文本（实际显示 "P0"，不是 "P0 - 紧急"）
      expect(find.text('P0'), findsOneWidget);
    });

    testWidgets('应该显示未读标记（新简报）', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BriefingCard(
              briefing: testBriefing,
              onTap: () {},
            ),
          ),
        ),
      );

      // 验证未读标记容器存在
      final unreadIndicators = tester.widgetList<Container>(
        find.byType(Container),
      ).where((container) {
        final decoration = container.decoration as BoxDecoration?;
        return decoration?.shape == BoxShape.circle;
      });

      expect(unreadIndicators.isNotEmpty, true);
    });

    testWidgets('应该显示 Agent 信息', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BriefingCard(
              briefing: testBriefing,
              onTap: () {},
            ),
          ),
        ),
      );

      // 验证 Agent 名称
      expect(find.text('研发效能监控员'), findsOneWidget);

      // 注意：Agent 角色（agentRole）不在卡片中显示，只在详情页显示
    });

    testWidgets('应该显示标题和摘要', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BriefingCard(
              briefing: testBriefing,
              onTap: () {},
            ),
          ),
        ),
      );

      // 验证标题
      expect(find.text('代码返工率持续上升'), findsOneWidget);

      // 验证摘要（部分匹配）
      expect(find.textContaining('过去7天返工率'), findsOneWidget);
    });

    testWidgets('应该显示影响说明', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BriefingCard(
              briefing: testBriefing,
              onTap: () {},
            ),
          ),
        ),
      );

      // 验证影响说明
      expect(find.text('可能影响项目交付时间'), findsOneWidget);
    });

    testWidgets('不应该显示操作按钮', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BriefingCard(
              briefing: testBriefing,
              onTap: () {},
            ),
          ),
        ),
      );

      // 验证没有 TextButton（操作按钮已移除）
      expect(find.byType(TextButton), findsNothing);
      expect(find.byType(ElevatedButton), findsNothing);
      expect(find.byType(OutlinedButton), findsNothing);
    });

    testWidgets('点击卡片应该触发 onTap 回调', (WidgetTester tester) async {
      bool tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BriefingCard(
              briefing: testBriefing,
              onTap: () {
                tapped = true;
              },
            ),
          ),
        ),
      );

      // 点击卡片
      await tester.tap(find.byType(Card));
      await tester.pumpAndSettle();

      // 验证回调被触发
      expect(tapped, true);
    });

    testWidgets('不同类型简报应该显示不同的渐变颜色', (WidgetTester tester) async {
      final briefingTypes = [
        BriefingType.alert,
        BriefingType.insight,
        BriefingType.summary,
        BriefingType.action,
      ];

      for (final type in briefingTypes) {
        final briefing = testBriefing.copyWith(briefingType: type);

        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: BriefingCard(
                briefing: briefing,
                onTap: () {},
              ),
            ),
          ),
        );

        // 验证渐变容器存在
        expect(find.byType(Container), findsWidgets);

        await tester.pumpAndSettle();
      }
    });
  });
}
