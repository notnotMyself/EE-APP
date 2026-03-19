import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import '../controllers/auth_controller.dart';

/// OPPO Sans 字体家族名称（Figma: OPPO Sans 4.0）
const String _oppoSansFamily = 'OPPO Sans 4.0';

/// 统一设计主题颜色（严格对照 Figma node 1914:9215）
class _AppDesign {
  static const Color backgroundColor = Color(0xFFF0F1F2); // 中性色/背景色/BG Gray
  static const Color titleColor = Color(0xFF101828);
  static const Color subtitleColor = Color(0xFF62748E);
  static const Color inputBackground = Colors.white; // 中性色/填充色/Card #FFFFFF
  static const Color buttonColor = Color(0xE5000000); // rgba(0,0,0,0.9) Primary
  static const Color secondaryIcon = Color(0x8A000000); // rgba(0,0,0,0.54) Secondary
  static const Color primaryIcon = Color(0xE5000000); // rgba(0,0,0,0.9) Primary
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
  final _scrollController = ScrollController();
  bool _obscurePassword = true;
  bool _isRegistering = false;
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
    _scrollController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  /// 键盘收起时，恢复到顶部
  void _scrollToTop() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Future.delayed(const Duration(milliseconds: 100), () {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            0,
            duration: const Duration(milliseconds: 250),
            curve: Curves.easeOut,
          );
        }
      });
    });
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      if (_isRegistering) {
        await ref.read(authControllerProvider.notifier).signUpWithUsername(
              email: _emailController.text.trim(),
              username: _usernameController.text.trim(),
              password: _passwordController.text,
            );

        final authState = ref.read(authControllerProvider);
        if (authState.hasError) {
          throw authState.error!;
        }

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
          setState(() {
            _isRegistering = false;
          });
        }
      } else {
        await ref.read(authControllerProvider.notifier).signIn(
              email: _emailController.text.trim(),
              password: _passwordController.text,
            );

        final authState = ref.read(authControllerProvider);
        if (authState.hasError) {
          throw authState.error!;
        }

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
    final screenWidth = MediaQuery.of(context).size.width;
    // Figma 设计基于 360px 宽屏幕，内容区域宽 296px (左右各 32px)
    final contentWidth = screenWidth * (296 / 360);
    final horizontalPadding = (screenWidth - contentWidth) / 2;

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle.dark,
      child: Scaffold(
        backgroundColor: _AppDesign.backgroundColor,
        resizeToAvoidBottomInset: true,
        body: GestureDetector(
          // 点击空白区域收起键盘
          onTap: () => FocusScope.of(context).unfocus(),
          child: FadeTransition(
            opacity: _fadeAnimation,
            child: SlideTransition(
              position: _slideAnimation,
              child: Form(
                key: _formKey,
                child: SafeArea(
                  child: SingleChildScrollView(
                    controller: _scrollController,
                    physics: const ClampingScrollPhysics(),
                    padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
                    child: Column(
                      children: [
                        // 顶部间距
                        const SizedBox(height: 80),

                        // 标题区域 - Figma: column, center aligned, gap 4px
                        Text(
                          '你的方案验证官',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: _AppDesign.titleColor,
                            fontSize: 24,
                            fontFamily: _oppoSansFamily,
                            fontWeight: FontWeight.w700,
                            height: 1.33,
                            letterSpacing: -0.53,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '让每一个像素都经得起推敲',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: _AppDesign.subtitleColor,
                            fontSize: 14,
                            fontFamily: _oppoSansFamily,
                            fontWeight: FontWeight.w400,
                            height: 1.43,
                            letterSpacing: -0.15,
                          ),
                        ),

                        const SizedBox(height: 24),

                        // 头像 - 增大为 160x160
                        Container(
                          width: 160,
                          height: 160,
                          decoration: BoxDecoration(
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x1A000000),
                                blurRadius: 32,
                                offset: Offset(0, 6),
                              ),
                            ],
                            borderRadius: BorderRadius.circular(80),
                          ),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(80),
                            child: Image.asset(
                              'assets/images/profile_image.png',
                              width: 160,
                              height: 160,
                              fit: BoxFit.cover,
                            ),
                          ),
                        ),

                        const SizedBox(height: 48),

                        // 输入框组 - 失焦时回到顶部
                        Focus(
                          onFocusChange: (hasFocus) {
                            if (!hasFocus) _scrollToTop();
                          },
                          child: _buildInputSection(isLoading, contentWidth),
                        ),
                        const SizedBox(height: 80),
                        _buildLoginButton(isLoading, contentWidth),
                        const SizedBox(height: 12),
                        _buildToggleLink(),

                        // 底部留白
                        const SizedBox(height: 40),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// 输入框区域
  /// Figma: layout_34U80Y - column, gap 16px, fill width
  Widget _buildInputSection(bool isLoading, double contentWidth) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 账号输入框 - Figma: 手机图标, hint "账号"
        _buildInputField(
          controller: _emailController,
          hintText: 'OPPO邮箱',
          svgIcon: 'assets/icons/phone_icon.svg',
          keyboardType: TextInputType.emailAddress,
          enabled: !isLoading,
          width: contentWidth,
          validator: (value) {
            if (value == null || value.isEmpty) {
              return '请输入OPPO邮箱';
            }
            if (!value.contains('@')) {
              return '请输入有效的邮箱地址';
            }
            if (_isRegistering && !value.trim().toLowerCase().endsWith('@oppo.com')) {
              return '只允许使用@oppo.com邮箱注册';
            }
            return null;
          },
        ),
        const SizedBox(height: 16), // Figma: gap 16px
        // 用户名输入框（仅注册模式显示）
        if (_isRegistering) ...[
          _buildInputField(
            controller: _usernameController,
            hintText: '用户名',
            svgIcon: 'assets/icons/phone_icon.svg',
            enabled: !isLoading,
            width: contentWidth,
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
          const SizedBox(height: 16),
        ],
        // 密码输入框 - Figma: Lock 锁图标, hint "请输入密码", trailing 可见(eye icon 22x22)
        _buildInputField(
          controller: _passwordController,
          hintText: '请输入密码',
          svgIcon: 'assets/icons/lock_icon.svg',
          obscureText: _obscurePassword,
          enabled: !isLoading,
          width: contentWidth,
          suffixIcon: IconButton(
            icon: Icon(
              _obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
              size: 22, // Figma: 附加操作 Trailing 可见 22x22
              color: _AppDesign.secondaryIcon,
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

  /// 输入框组件（严格对照 Figma 卡片列表输入框 COUICardSingleInputView）
  /// Figma layout_9WL6U6: row, gap 16px, padding 2px 16px, width 296px, borderRadius 20px, white bg
  /// Text style Body/L · Regular: OPPO Sans 4.0, w400, fontSize 16, lineHeight 1.375
  Widget _buildInputField({
    required TextEditingController controller,
    required String hintText,
    required String svgIcon,
    TextInputType? keyboardType,
    bool obscureText = false,
    bool enabled = true,
    Widget? suffixIcon,
    String? Function(String?)? validator,
    required double width,
  }) {
    return Container(
      width: width,
      decoration: BoxDecoration(
        color: _AppDesign.inputBackground,
        borderRadius: BorderRadius.circular(20), // Figma: borderRadius 20px
      ),
      // Figma: padding 2px 16px (top/bottom 2px, left/right 16px)
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Figma: .图标 Icon 24 - 24x24, vertically centered
          SvgPicture.asset(
            svgIcon,
            width: 24, // Figma: 24x24
            height: 24,
          ),
          const SizedBox(width: 16), // Figma: gap 16px
          // Figma: .输入框 Text field - fill width, padding 10px 0px
          Expanded(
            child: TextFormField(
              controller: controller,
              keyboardType: keyboardType,
              obscureText: obscureText,
              enabled: enabled,
              validator: validator,
              style: const TextStyle(
                fontFamily: _oppoSansFamily,
                fontSize: 16, // Figma: Body/L · Regular fontSize 16
                fontWeight: FontWeight.w400,
                height: 1.375, // Figma: lineHeight 1.375em
                color: Color(0xE5000000), // 中性色/90 Primary
              ),
              decoration: InputDecoration(
                hintText: hintText,
                hintStyle: const TextStyle(
                  fontFamily: _oppoSansFamily,
                  fontSize: 16, // Figma: Body/L · Regular fontSize 16
                  fontWeight: FontWeight.w400,
                  height: 1.375, // Figma: lineHeight 1.375em
                  color: Color(0x8A000000), // 中性色/54 Secondary
                ),
                // Figma: .输入框 padding 10px 0px (top/bottom)
                contentPadding: const EdgeInsets.symmetric(vertical: 10),
                // 显式覆盖全局 InputDecorationTheme 的 filled 属性
                filled: false,
                border: InputBorder.none,
                enabledBorder: InputBorder.none,
                focusedBorder: InputBorder.none,
                errorBorder: InputBorder.none,
                focusedErrorBorder: InputBorder.none,
                isDense: true,
                suffixIcon: suffixIcon,
                suffixIconConstraints: suffixIcon != null
                    ? const BoxConstraints(minWidth: 22, minHeight: 22)
                    : null,
                errorStyle: TextStyle(
                  fontFamily: _oppoSansFamily,
                  fontSize: 12,
                  color: _AppDesign.errorRed,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 登录按钮（严格对照 Figma 填充按钮_大 COUIButton）
  /// Figma: width 296px, borderRadius 36px outer
  /// .Button bg1: 296x44, borderRadius 100px, rgba(0,0,0,0.9), 质感样式 inset shadows
  /// Text: "开始", Button/L · Medium (OPPO Sans 4.0, w500, 16px, lineHeight 1.5), white
  Widget _buildLoginButton(bool isLoading, double contentWidth) {
    return Container(
      width: contentWidth,
      height: 44, // Figma: .Button bg1 height 44
      decoration: BoxDecoration(
        color: _AppDesign.buttonColor,
        borderRadius: BorderRadius.circular(100), // Figma: .Button bg1 borderRadius 100px
        boxShadow: const [
          // Figma: 质感样式/按钮/主题色（亮色） - inset shadows (approximated)
          BoxShadow(
            color: Color(0x24000000),
            blurRadius: 54,
            offset: Offset(0, 6),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: isLoading ? null : _handleLogin,
          borderRadius: BorderRadius.circular(100),
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
                : Text(
                    _isRegistering ? '注册' : '开始',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16, // Figma: Button/L · Medium fontSize 16
                      fontFamily: _oppoSansFamily,
                      fontWeight: FontWeight.w500, // Figma: Medium
                      height: 1.5, // Figma: lineHeight 1.5em
                    ),
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
