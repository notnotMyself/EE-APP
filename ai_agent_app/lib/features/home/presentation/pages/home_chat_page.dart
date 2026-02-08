import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../agents/domain/models/agent.dart';
import '../../../agents/data/agent_repository.dart';
import '../../../agents/presentation/pages/agent_profile_page.dart';
import '../../../agents/presentation/theme/agent_profile_theme.dart';

/// 首页 - Chris Chen AI评审官对话页面
///
/// 使用 ConsumerStatefulWidget 在本地缓存 Agent，避免 Provider 刷新
/// 导致 AgentProfilePage 被反复销毁重建。
class HomeChatPage extends ConsumerStatefulWidget {
  const HomeChatPage({super.key});

  @override
  ConsumerState<HomeChatPage> createState() => _HomeChatPageState();
}

class _HomeChatPageState extends ConsumerState<HomeChatPage> {
  Agent? _agent;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAgent();
  }

  Future<void> _loadAgent() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final repository = AgentRepository();
      final agents = await repository.getActiveAgents();
      final designValidator = agents
          .where((a) => a.role == 'design_validator')
          .toList();

      if (!mounted) return;

      if (designValidator.isNotEmpty) {
        setState(() {
          _agent = designValidator.first;
          _isLoading = false;
        });
      } else {
        setState(() {
          _agent = null;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return _buildLoading(context);
    }

    if (_error != null) {
      return _buildError(context, _error!);
    }

    if (_agent == null) {
      return _buildAgentNotFound(context);
    }

    // 关键：Agent 加载完成后，直接展示 AgentProfilePage
    // 使用稳定的 Key 确保不会被销毁重建
    return AgentProfilePage(
      key: ValueKey('home-chat-${_agent!.id}'),
      agent: _agent!,
      showBackButton: false,
    );
  }

  Widget _buildLoading(BuildContext context) {
    return Scaffold(
      backgroundColor: AgentProfileTheme.backgroundColor,
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 48,
              height: 48,
              child: CircularProgressIndicator(
                strokeWidth: 3,
                color: AgentProfileTheme.accentBlue,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              '正在加载 AI 评审官...',
              style: TextStyle(
                color: AgentProfileTheme.labelColor,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAgentNotFound(BuildContext context) {
    return Scaffold(
      backgroundColor: AgentProfileTheme.backgroundColor,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.person_search_rounded,
                size: 64,
                color: AgentProfileTheme.labelColor,
              ),
              const SizedBox(height: 16),
              Text(
                'AI 评审官尚未配置',
                style: TextStyle(
                  color: AgentProfileTheme.titleColor,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '请联系管理员添加 Chris Chen 评审官',
                style: TextStyle(
                  color: AgentProfileTheme.labelColor,
                  fontSize: 14,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              TextButton.icon(
                onPressed: _loadAgent,
                icon: const Icon(Icons.refresh),
                label: const Text('重试'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildError(BuildContext context, String error) {
    return Scaffold(
      backgroundColor: AgentProfileTheme.backgroundColor,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.error_outline_rounded,
                size: 64,
                color: Colors.red[300],
              ),
              const SizedBox(height: 16),
              Text(
                '加载失败',
                style: TextStyle(
                  color: AgentProfileTheme.titleColor,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                error,
                style: TextStyle(
                  color: AgentProfileTheme.labelColor,
                  fontSize: 13,
                ),
                textAlign: TextAlign.center,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 24),
              TextButton.icon(
                onPressed: _loadAgent,
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
