import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:timeago/timeago.dart' as timeago;
import 'core/config/app_config.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'core/error/error_handler.dart';
import 'features/app_update/services/app_update_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 初始化全局错误处理
  GlobalErrorHandler.initialize();

  // 初始化 timeago 中文语言
  timeago.setLocaleMessages('zh', timeago.ZhMessages());

  // 初始化Supabase
  await Supabase.initialize(
    url: AppConfig.supabaseUrl,
    anonKey: AppConfig.supabaseAnonKey,
  );

  // 监听 Auth 状态变化，自动处理 Refresh Token 错误
  Supabase.instance.client.auth.onAuthStateChange.listen((data) {
    final event = data.event;

    // 打印认证事件（调试用）
    debugPrint('Supabase Auth Event: $event');

    // 当检测到 Token 刷新失败时，自动登出
    if (event == AuthChangeEvent.tokenRefreshed) {
      debugPrint('Token refreshed successfully');
    }
  });

  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}

class MyApp extends ConsumerStatefulWidget {
  const MyApp({super.key});

  @override
  ConsumerState<MyApp> createState() => _MyAppState();
}

class _MyAppState extends ConsumerState<MyApp> {
  @override
  void initState() {
    super.initState();
    // 延迟执行更新检查，避免在 build 阶段调用
    // 这样无论用户是否登录，都会在启动时检查更新
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        AppUpdateService.checkUpdateOnStartup(context, ref, silent: true);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: 'AI数字员工平台',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      routerConfig: router,
    );
  }
}
