import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/conversation_repository.dart';
import '../../domain/models/conversation.dart';
import '../../../agents/domain/models/agent.dart';
import '../../../auth/presentation/controllers/auth_controller.dart';

/// Conversation Repository Provider
final conversationRepositoryProvider = Provider<ConversationRepository>((ref) {
  return ConversationRepository();
});

/// 特定对话的Provider
final conversationProvider =
    FutureProvider.family<Conversation, String>((ref, conversationId) async {
  final repository = ref.watch(conversationRepositoryProvider);
  return repository.getConversation(conversationId);
});

/// 对话消息列表Provider
final conversationMessagesProvider =
    FutureProvider.family<List<Message>, String>((ref, conversationId) async {
  final repository = ref.watch(conversationRepositoryProvider);
  return repository.getMessages(conversationId);
});

/// 用户所有对话列表Provider
final userConversationsProvider = FutureProvider<List<Conversation>>((ref) async {
  final currentUser = ref.watch(currentUserProvider);
  if (currentUser == null) {
    return [];
  }

  final repository = ref.watch(conversationRepositoryProvider);
  return repository.getUserConversations(currentUser.id);
});

/// 特定Agent的对话列表Provider（多会话模式）
final agentConversationsProvider =
    FutureProvider.family<List<Conversation>, String>((ref, agentId) async {
  final repository = ref.watch(conversationRepositoryProvider);
  return repository.getAgentConversations(
    agentId: agentId,
    limit: 50,
    status: 'active',
  );
});

/// Conversation Controller
class ConversationController extends StateNotifier<AsyncValue<void>> {
  ConversationController(this.ref) : super(const AsyncValue.data(null));

  final Ref ref;

  /// 创建新对话
  Future<Conversation?> createConversation(String agentId) async {
    final currentUser = ref.read(currentUserProvider);
    if (currentUser == null) {
      print('createConversation: currentUser is null');
      state = AsyncValue.error('请先登录', StackTrace.current);
      return null;
    }

    print('createConversation: userId=${currentUser.id}, agentId=$agentId');
    state = const AsyncValue.loading();
    try {
      final repository = ref.read(conversationRepositoryProvider);
      final conversation = await repository.createConversation(
        userId: currentUser.id,
        agentId: agentId,
      );

      print('createConversation: success, conversationId=${conversation.id}');
      state = const AsyncValue.data(null);

      // 刷新对话列表
      ref.invalidate(userConversationsProvider);

      return conversation;
    } catch (e, stack) {
      print('createConversation: error=$e');
      print('createConversation: stack=$stack');
      state = AsyncValue.error(e, stack);
      return null;
    }
  }

  /// 保存用户消息
  Future<Message?> saveUserMessage({
    required String conversationId,
    required String content,
  }) async {
    try {
      final repository = ref.read(conversationRepositoryProvider);
      final message = await repository.saveMessage(
        conversationId: conversationId,
        role: 'user',
        content: content,
      );

      // 刷新消息列表
      ref.invalidate(conversationMessagesProvider(conversationId));

      return message;
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
      return null;
    }
  }

  /// 保存AI响应消息
  Future<Message?> saveAssistantMessage({
    required String conversationId,
    required String content,
  }) async {
    try {
      final repository = ref.read(conversationRepositoryProvider);
      final message = await repository.saveMessage(
        conversationId: conversationId,
        role: 'assistant',
        content: content,
      );

      // 刷新消息列表
      ref.invalidate(conversationMessagesProvider(conversationId));

      return message;
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
      return null;
    }
  }

  /// 更新会话标题
  Future<Conversation?> updateConversationTitle({
    required String conversationId,
    required String title,
  }) async {
    state = const AsyncValue.loading();
    try {
      final repository = ref.read(conversationRepositoryProvider);
      final conversation = await repository.updateConversationTitle(
        conversationId: conversationId,
        title: title,
      );

      state = const AsyncValue.data(null);

      // 刷新对话相关的所有providers
      ref.invalidate(conversationProvider(conversationId));
      ref.invalidate(userConversationsProvider);

      return conversation;
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
      return null;
    }
  }

  /// 获取特定Agent的所有对话
  Future<List<Conversation>> getAgentConversations(String agentId) async {
    try {
      final repository = ref.read(conversationRepositoryProvider);
      return await repository.getAgentConversations(
        agentId: agentId,
        limit: 50,
        status: 'active',
      );
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
      return [];
    }
  }
}

/// Conversation Controller Provider
final conversationControllerProvider =
    StateNotifierProvider<ConversationController, AsyncValue<void>>((ref) {
  return ConversationController(ref);
});
