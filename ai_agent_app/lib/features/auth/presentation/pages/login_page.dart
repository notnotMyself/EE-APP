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
  final _usernameController = TextEditingController();
  bool _obscurePassword = true;
  bool _isRegistering = false; // 切换登录/注册模式
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
    _usernameController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      if (_isRegistering) {
        // 注册逻辑
        await ref.read(authControllerProvider.notifier).signUpWithUsername(
              email: _emailController.text.trim(),
              username: _usernameController.text.trim(),
              password: _passwordController.text,
            );

        // 检查是否有错误
        final authState = ref.read(authControllerProvider);
        if (authState.hasError) {
          throw authState.error!;
        }

        // 注册成功提示
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: const Text(
                '注册成功！请在手机上打开邮箱，点击验证链接完成注册',
                style: TextStyle(fontFamily: _oppoSansFamily),
              ),
              backgroundColor: Colors.green,
              behavior: SnackBarBehavior.floating,
              duration: const Duration(seconds: 5),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          );
          // 切换回登录模式
          setState(() {
            _isRegistering = false;
          });
        }
      } else {
        // 登录逻辑
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
          context.go('/home');
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              '${_isRegistering ? "注册" : "登录"}失败: ${e.toString()}',
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

                  // 中间插图区域（Chris Chen 头像）
                  Positioned(
                    left: 0,
                    right: 0,
                    top: 140,
                    child: Center(
                      child: Container(
                        width: 280,
                        height: 280,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.08),
                              blurRadius: 40,
                              offset: const Offset(0, 12),
                              spreadRadius: 0,
                            ),
                          ],
                          image: const DecorationImage(
                            image: AssetImage('assets/images/chris_chen_avatar.jpeg'),
                            fit: BoxFit.cover,
                          ),
                        ),
                      ),
                    ),
                  ),

                  // 底部输入区域
                  Positioned(
                    left: 17,
                    right: 17,
                    bottom: 164, // 调整位置，给按钮区域留出足够间距
                    child: _buildInputSection(isLoading),
                  ),

                  // 底部按钮区域（登录按钮 + 切换链接）
                  Positioned(
                    left: 17,
                    right: 17,
                    bottom: 24,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // 登录按钮
                        _buildLoginButton(isLoading),
                        const SizedBox(height: 12),
                        // 登录/注册切换链接
                        _buildToggleLink(),
                      ],
                    ),
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
          '让每个人都组建AI团队',
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
            // 注册模式下检查邮箱后缀
            if (_isRegistering && !value.trim().toLowerCase().endsWith('@oppo.com')) {
              return '只允许使用@oppo.com邮箱注册';
            }
            return null;
          },
        ),
        const SizedBox(height: 10),
        // 用户名输入框（仅注册模式显示）
        if (_isRegistering) ...[
          _buildInputField(
            controller: _usernameController,
            hintText: '用户名',
            icon: Icons.badge_outlined,
            enabled: !isLoading,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return '请输入用户名';
              }
              if (value.length < 2) {
                return '用户名至少2个字符';
              }
              return null;
            },
          ),
          const SizedBox(height: 10),
        ],
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
                        _isRegistering ? '注册' : '开始',
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

  /// 登录/注册切换链接
  Widget _buildToggleLink() {
    return GestureDetector(
      onTap: () {
        setState(() {
          _isRegistering = !_isRegistering;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              _isRegistering ? '已有账号？' : '没有账号？',
              style: TextStyle(
                fontSize: 14,
                fontFamily: _oppoSansFamily,
                fontWeight: FontWeight.w400,
                color: _AppDesign.subtitleColor,
                height: 1.5,
              ),
            ),
            Text(
              _isRegistering ? '返回登录' : '立即注册',
              style: TextStyle(
                fontSize: 14,
                fontFamily: _oppoSansFamily,
                fontWeight: FontWeight.w600,
                color: Colors.blue.shade600,
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
