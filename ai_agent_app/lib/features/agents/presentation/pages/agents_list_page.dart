import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../controllers/agent_controller.dart';
import '../../domain/models/agent.dart';
import '../../../conversations/presentation/pages/conversation_page.dart';

class AgentsListPage extends ConsumerWidget {
  const AgentsListPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final agentsAsync = ref.watch(activeAgentsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI员工市场'),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_outlined),
            onPressed: () {
              // TODO: Navigate to my agents
            },
          ),
        ],
      ),
      body: agentsAsync.when(
        data: (agents) {
          if (agents.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.psychology_outlined,
                    size: 80,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '暂无可用的AI员工',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: agents.length,
            itemBuilder: (context, index) {
              final agent = agents[index];
              return AgentCard(agent: agent);
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.error_outline,
                size: 80,
                color: Colors.red[300],
              ),
              const SizedBox(height: 16),
              Text(
                '加载失败: $error',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () => ref.invalidate(activeAgentsProvider),
                icon: const Icon(Icons.refresh),
                label: const Text('重试'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class AgentCard extends ConsumerWidget {
  const AgentCard({
    super.key,
    required this.agent,
  });

  final Agent agent;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isSubscribedAsync = ref.watch(isAgentSubscribedProvider(agent.id));

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Avatar
                CircleAvatar(
                  radius: 24,
                  backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                  child: agent.avatarUrl != null
                      ? Image.network(agent.avatarUrl!)
                      : Icon(
                          Icons.psychology,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                ),
                const SizedBox(width: 12),

                // Name and Role
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        agent.name,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        agent.role,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey[600],
                            ),
                      ),
                    ],
                  ),
                ),

                // Subscribe Button
                isSubscribedAsync.when(
                  data: (isSubscribed) {
                    return FilledButton.tonal(
                      onPressed: () async {
                        if (isSubscribed) {
                          await ref
                              .read(agentControllerProvider.notifier)
                              .unsubscribe(agent.id);
                        } else {
                          await ref
                              .read(agentControllerProvider.notifier)
                              .subscribe(agent.id);
                        }

                        // Show feedback
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(
                                isSubscribed ? '已取消订阅' : '订阅成功',
                              ),
                              duration: const Duration(seconds: 2),
                            ),
                          );
                        }
                      },
                      child: Text(isSubscribed ? '已订阅' : '订阅'),
                    );
                  },
                  loading: () => const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  error: (_, __) => const Icon(Icons.error_outline),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Description
            Text(
              agent.description,
              style: Theme.of(context).textTheme.bodyMedium,
            ),

            // Data Sources (if available)
            if (agent.dataSources != null && agent.dataSources!.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: agent.dataSources!.keys
                    .map((source) => Chip(
                          label: Text(
                            source,
                            style: const TextStyle(fontSize: 12),
                          ),
                          visualDensity: VisualDensity.compact,
                        ))
                    .toList(),
              ),
            ],

            // Start Conversation Button
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (context) => ConversationPage(agent: agent),
                    ),
                  );
                },
                icon: const Icon(Icons.chat_outlined),
                label: const Text('开始对话'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
