import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../controllers/auth_controller.dart';

/// OPPO Sans 字体家族名称
const String _oppoSansFamily = 'PingFang SC';

/// 统一设计主题颜色（基于 Figma）
class _AppDesign {
  static const Color backgroundColor = Color(0xFFE9EAF0);
  static const Color titleColor = Color(0xFF0E162B);
  static const Color subtitleColor = Color(0xFF61738D);
  static const Color labelColor = Color(0xFF8696BB);
  static const Color inputBackground = Color(0xFFF8FAFC);
  static const Color inputBorder = Color(0xFFE1E8F0);
  static const Color buttonColor = Colors.black;
  static const Color errorRed = Color(0xFFEF4444);
}

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage>
    with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOut),
    );
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.2),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOut),
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      await ref.read(authControllerProvider.notifier).signIn(
            email: _emailController.text.trim(),
            password: _passwordController.text,
          );

      // 检查是否有错误
      final authState = ref.read(authControllerProvider);
      if (authState.hasError) {
        throw authState.error!;
      }

      // 登录成功，跳转到信息流页面
      if (mounted) {
        context.go('/feed');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              '登录失败: ${e.toString()}',
              style: const TextStyle(fontFamily: _oppoSansFamily),
            ),
            backgroundColor: _AppDesign.errorRed,
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
    final authState = ref.watch(authControllerProvider);
    final isLoading = authState.isLoading;

    return Scaffold(
      backgroundColor: _AppDesign.backgroundColor,
      body: SafeArea(
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: SlideTransition(
            position: _slideAnimation,
            child: Form(
              key: _formKey,
              child: Stack(
                children: [
                  // 顶部标题区域
                  Positioned(
                    left: 17,
                    top: 56,
                    child: _buildHeader(),
                  ),

                  // 中间插图区域（品牌插图）
                  Positioned(
                    left: 5,
                    top: 122,
                    child: Container(
                      width: MediaQuery.of(context).size.width - 10,
                      height: 400,
                      decoration: const BoxDecoration(
                        image: DecorationImage(
                          image: AssetImage('assets/images/Saly-11.png'),
                          fit: BoxFit.contain,
                        ),
                      ),
                    ),
                  ),

                  // 底部输入区域
                  Positioned(
                    left: 17,
                    right: 17,
                    bottom: 100,
                    child: _buildInputSection(isLoading),
                  ),

                  // 登录按钮
                  Positioned(
                    left: 17,
                    right: 17,
                    bottom: 30,
                    child: _buildLoginButton(isLoading),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// 顶部标题区域（基于 Figma 设计）
  Widget _buildHeader() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 主标题
        Text(
          'AI数字员工',
          style: TextStyle(
            color: _AppDesign.titleColor,
            fontSize: 30,
            fontFamily: _oppoSansFamily,
            fontWeight: FontWeight.w600,
            height: 1.25,
            letterSpacing: -0.35,
          ),
        ),
        const SizedBox(height: 8),
        // 副标题
        Text(
          '让每个人都能雇得起员工',
          style: TextStyle(
            color: _AppDesign.subtitleColor,
            fontSize: 14,
            fontFamily: _oppoSansFamily,
            fontWeight: FontWeight.w400,
            height: 1.43,
            letterSpacing: -0.15,
          ),
        ),
      ],
    );
  }

  /// 输入框区域（基于 Figma 设计）
  Widget _buildInputSection(bool isLoading) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 账号输入框
        _buildInputField(
          controller: _emailController,
          hintText: '账号',
          icon: Icons.person_outline,
          keyboardType: TextInputType.emailAddress,
          enabled: !isLoading,
          validator: (value) {
            if (value == null || value.isEmpty) {
              return '请输入账号';
            }
            if (!value.contains('@')) {
              return '请输入有效的邮箱地址';
            }
            return null;
          },
        ),
        const SizedBox(height: 10),
        // 密码输入框
        _buildInputField(
          controller: _passwordController,
          hintText: '请输入密码',
          icon: Icons.lock_outline,
          obscureText: _obscurePassword,
          enabled: !isLoading,
          suffixIcon: IconButton(
            icon: Icon(
              _obscurePassword
                  ? Icons.visibility_outlined
                  : Icons.visibility_off_outlined,
              color: Colors.black.withOpacity(0.54),
              size: 20,
            ),
            onPressed: () {
              setState(() {
                _obscurePassword = !_obscurePassword;
              });
            },
          ),
          validator: (value) {
            if (value == null || value.isEmpty) {
              return '请输入密码';
            }
            return null;
          },
        ),
      ],
    );
  }

  /// 输入框组件（基于 Figma 设计）
  Widget _buildInputField({
    required TextEditingController controller,
    required String hintText,
    required IconData icon,
    TextInputType? keyboardType,
    bool obscureText = false,
    bool enabled = true,
    Widget? suffixIcon,
    String? Function(String?)? validator,
  }) {
    return Container(
      height: 56,
      decoration: ShapeDecoration(
        color: _AppDesign.inputBackground,
        shape: RoundedRectangleBorder(
          side: BorderSide(
            width: 0.62,
            color: _AppDesign.inputBorder,
          ),
          borderRadius: BorderRadius.circular(16),
        ),
      ),
      child: TextFormField(
        controller: controller,
        keyboardType: keyboardType,
        obscureText: obscureText,
        enabled: enabled,
        validator: validator,
        style: TextStyle(
          fontFamily: _oppoSansFamily,
          fontSize: 14,
          color: Colors.black.withOpacity(0.9),
        ),
        decoration: InputDecoration(
          hintText: hintText,
          hintStyle: TextStyle(
            fontFamily: _oppoSansFamily,
            fontSize: 14,
            fontWeight: FontWeight.w400,
            color: Colors.black.withOpacity(0.54),
            height: 1.43,
          ),
          prefixIcon: Padding(
            padding: const EdgeInsets.only(left: 16, right: 12),
            child: Icon(
              icon,
              color: Colors.black.withOpacity(0.54),
              size: 20,
            ),
          ),
          prefixIconConstraints: const BoxConstraints(
            minWidth: 48,
            minHeight: 20,
          ),
          suffixIcon: suffixIcon,
          border: InputBorder.none,
          enabledBorder: InputBorder.none,
          focusedBorder: InputBorder.none,
          errorBorder: InputBorder.none,
          focusedErrorBorder: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 18,
          ),
          errorStyle: TextStyle(
            fontFamily: _oppoSansFamily,
            fontSize: 12,
            color: _AppDesign.errorRed,
          ),
        ),
      ),
    );
  }

  /// 登录按钮（基于 Figma 设计）
  Widget _buildLoginButton(bool isLoading) {
    return Container(
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
          onTap: isLoading ? null : _handleLogin,
          borderRadius: BorderRadius.circular(40),
          child: Center(
            child: isLoading
                ? const SizedBox(
                    height: 24,
                    width: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 2.5,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '开始',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontFamily: _oppoSansFamily,
                          fontWeight: FontWeight.w600,
                          height: 1.50,
                          letterSpacing: -0.31,
                        ),
                      ),
                      const SizedBox(width: 8),
                      const Icon(
                        Icons.arrow_forward_rounded,
                        color: Colors.white,
                        size: 20,
                      ),
                    ],
                  ),
          ),
        ),
      ),
    );
  }
}
