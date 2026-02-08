import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../layout/main_scaffold.dart';
import '../../features/auth/presentation/pages/login_page.dart';
import '../../features/auth/presentation/pages/register_page.dart';
import '../../features/auth/presentation/pages/terms_agreement_page.dart';
import '../../features/auth/presentation/controllers/auth_controller.dart';
import '../../features/home/presentation/pages/home_page.dart';
import '../../features/home/presentation/pages/home_chat_page.dart';
import '../../features/design/presentation/design_feed_page.dart';
import '../../features/library/presentation/pages/library_page.dart';
import '../../features/profile/presentation/pages/profile_page.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final supabase = Supabase.instance.client;
  final authController = ref.read(authControllerProvider.notifier);

  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) async {
      final isAuthenticated = supabase.auth.currentUser != null;
      final location = state.matchedLocation;
      final isAuthPage = location == '/login' || location == '/register';
      final isWelcomePage = location == '/welcome';
      final isTermsPage = location == '/terms';

      // 未登录且不在登录/注册页，跳转到登录页
      if (!isAuthenticated && !isAuthPage) {
        return '/login';
      }

      // 已登录但在登录/注册页，跳转到主页
      if (isAuthenticated && isAuthPage) {
        // TODO: 暂时隐藏隐私策略确认，等有必要时再启用
        return '/home';
      }

      return null;
    },
    routes: [
      // Auth routes (without bottom navigation)
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterPage(),
      ),
      GoRoute(
        path: '/terms',
        builder: (context, state) => const TermsAgreementPage(),
      ),
      GoRoute(
        path: '/welcome',
        builder: (context, state) => const HomePage(),
      ),

      // Main app routes (with bottom navigation)
      ShellRoute(
        builder: (context, state, child) {
          return MainScaffold(
            location: state.matchedLocation,
            child: child,
          );
        },
        routes: [
          GoRoute(
            path: '/home',
            builder: (context, state) => const HomeChatPage(),
          ),
          GoRoute(
            path: '/inspiration',
            builder: (context, state) => const DesignFeedPage(),
          ),
          GoRoute(
            path: '/library',
            builder: (context, state) => const LibraryPage(),
          ),
          GoRoute(
            path: '/profile',
            builder: (context, state) => const ProfilePage(),
          ),
        ],
      ),
    ],
  );
});
