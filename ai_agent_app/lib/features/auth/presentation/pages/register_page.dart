import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../controllers/auth_controller.dart';

class RegisterPage extends ConsumerStatefulWidget {
  const RegisterPage({super.key});

  @override
  ConsumerState<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends ConsumerState<RegisterPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      await ref.read(authControllerProvider.notifier).signUp(
            email: _emailController.text.trim(),
            password: _passwordController.text,
          );

      // 检查是否有错误
      final authState = ref.read(authControllerProvider);
      if (authState.hasError) {
        throw authState.error!;
      }

      // 注册成功，跳转到登录页
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('注册成功！请登录'),
            backgroundColor: Colors.green,
          ),
        );
        context.go('/login');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('注册失败: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/login'),
        ),
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 信息图标
                Icon(
                  Icons.info_outline,
                  size: 80,
                  color: Theme.of(context).primaryColor,
                ),
                const SizedBox(height: 24),

                // 标题
                Text(
                  '注册暂未开放',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),

                // 说明文字
                Text(
                  '本系统暂不开放公开注册。\n如需使用，请联系系统管理员申请账号。',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: Colors.grey[700],
                        height: 1.6,
                      ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),

                // 返回登录按钮
                ElevatedButton(
                  onPressed: () => context.go('/login'),
                  child: const Text('返回登录'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
