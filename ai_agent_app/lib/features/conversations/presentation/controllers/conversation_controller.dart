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
}

/// Conversation Controller Provider
final conversationControllerProvider =
    StateNotifierProvider<ConversationController, AsyncValue<void>>((ref) {
  return ConversationController(ref);
});
