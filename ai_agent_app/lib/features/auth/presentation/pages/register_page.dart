import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../controllers/auth_controller.dart';

/// OPPO Sans 字体家族名称
const String _oppoSansFamily = 'OPPO Sans';

/// 统一设计主题颜色
class _AppDesign {
  static const Color backgroundColor = Color(0xFFE9EAF0);
  static const Color titleColor = Color(0xFF0E162B);
  static const Color subtitleColor = Color(0xFF61738D);
  static const Color buttonColor = Colors.black;
}

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
          SnackBar(
            content: Text(
              '注册成功！请登录',
              style: const TextStyle(fontFamily: _oppoSansFamily),
            ),
            backgroundColor: Colors.green,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        );
        context.go('/login');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              '注册失败: ${e.toString()}',
              style: const TextStyle(fontFamily: _oppoSansFamily),
            ),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _AppDesign.backgroundColor,
      appBar: AppBar(
        backgroundColor: _AppDesign.backgroundColor,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(
            Icons.arrow_back_ios_new,
            color: _AppDesign.titleColor,
          ),
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
                Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    color: _AppDesign.subtitleColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(28),
                  ),
                  child: Icon(
                    Icons.info_outline_rounded,
                    size: 56,
                    color: _AppDesign.subtitleColor,
                  ),
                ),
                const SizedBox(height: 32),

                // 标题
                Text(
                  '注册暂未开放',
                  style: TextStyle(
                    fontFamily: _oppoSansFamily,
                    fontSize: 26,
                    fontWeight: FontWeight.w600,
                    color: _AppDesign.titleColor,
                    height: 1.25,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),

                // 说明文字
                Text(
                  '本系统暂不开放公开注册。\n如需使用，请联系系统管理员申请账号。',
                  style: TextStyle(
                    fontFamily: _oppoSansFamily,
                    fontSize: 14,
                    fontWeight: FontWeight.w400,
                    color: _AppDesign.subtitleColor,
                    height: 1.6,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 48),

                // 返回登录按钮
                Container(
                  height: 56,
                  decoration: ShapeDecoration(
                    color: _AppDesign.buttonColor,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(40),
                    ),
                    shadows: const [
                      BoxShadow(
                        color: Color(0x23000000),
                        blurRadius: 54,
                        offset: Offset(0, 6),
                        spreadRadius: 0,
                      ),
                    ],
                  ),
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      onTap: () => context.go('/login'),
                      borderRadius: BorderRadius.circular(40),
                      child: Center(
                        child: Text(
                          '返回登录',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontFamily: _oppoSansFamily,
                            fontWeight: FontWeight.w600,
                            height: 1.50,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
