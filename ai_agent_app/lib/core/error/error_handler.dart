import 'dart:async';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

/// 全局错误处理器
///
/// 负责捕获并处理所有应用内的错误和异常
class GlobalErrorHandler {
  /// 初始化全局错误处理
  static void initialize() {
    // 捕获Flutter框架错误
    FlutterError.onError = (FlutterErrorDetails details) {
      FlutterError.presentError(details);
      _logError('Flutter Error', details.exception, details.stack);
    };

    // 捕获异步错误
    PlatformDispatcher.instance.onError = (error, stack) {
      _logError('Async Error', error, stack);
      return true; // 返回true表示已处理
    };

    debugPrint('✅ Global error handler initialized');
  }

  /// 记录错误日志
  static void _logError(String source, Object error, StackTrace? stack) {
    if (kDebugMode) {
      debugPrint('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      debugPrint('❌ [$source] ${error.runtimeType}: $error');
      if (stack != null) {
        debugPrint('Stack trace:\n$stack');
      }
      debugPrint('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    } else {
      // 生产环境：可以发送到错误监控服务（如Sentry）
      // TODO: 集成Sentry错误上报
      debugPrint('❌ Error: ${error.runtimeType}');
    }
  }

  /// 处理API错误并显示友好提示
  static String handleApiError(dynamic error) {
    if (error is DioException) {
      return _handleDioError(error);
    } else if (error is SocketException) {
      return '网络连接失败，请检查您的网络设置';
    } else if (error is TimeoutException) {
      return '请求超时，请稍后重试';
    } else if (error is FormatException) {
      return '数据格式错误，请联系技术支持';
    } else {
      return error.toString().replaceFirst('Exception: ', '');
    }
  }

  /// 处理Dio错误
  static String _handleDioError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return '连接超时，请检查网络后重试';

      case DioExceptionType.badResponse:
        return _handleResponseError(error);

      case DioExceptionType.cancel:
        return '请求已取消';

      case DioExceptionType.connectionError:
        return '网络连接失败，请检查您的网络设置';

      case DioExceptionType.unknown:
        if (error.error is SocketException) {
          return '无法连接到服务器，请检查网络';
        }
        return '未知错误，请稍后重试';

      default:
        return '网络请求失败，请稍后重试';
    }
  }

  /// 处理HTTP响应错误
  static String _handleResponseError(DioException error) {
    final statusCode = error.response?.statusCode;
    final responseData = error.response?.data;

    // 尝试解析后端标准错误格式
    if (responseData is Map<String, dynamic>) {
      final errorInfo = responseData['error'];
      if (errorInfo is Map<String, dynamic>) {
        final message = errorInfo['message'];
        if (message is String && message.isNotEmpty) {
          return message;
        }
      }
    }

    // Fallback: 根据状态码返回默认错误
    switch (statusCode) {
      case 400:
        return '请求参数错误，请检查输入';
      case 401:
        return '身份验证失败，请重新登录';
      case 403:
        return '权限不足，无法访问该资源';
      case 404:
        return '请求的资源不存在';
      case 422:
        return '请求数据验证失败，请检查输入';
      case 429:
        return '请求过于频繁，请稍后再试';
      case 500:
        return '服务器内部错误，请稍后重试';
      case 502:
      case 503:
        return '服务暂时不可用，请稍后重试';
      case 504:
        return '服务器响应超时，请稍后重试';
      default:
        return '网络请求失败 (${statusCode ?? "未知"}), 请稍后重试';
    }
  }

  /// 显示错误提示（SnackBar）
  static void showErrorSnackBar(
    BuildContext context,
    dynamic error, {
    Duration duration = const Duration(seconds: 3),
  }) {
    final errorMessage = handleApiError(error);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(errorMessage),
        backgroundColor: Colors.red,
        duration: duration,
        behavior: SnackBarBehavior.floating,
        action: SnackBarAction(
          label: '关闭',
          textColor: Colors.white,
          onPressed: () {
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
          },
        ),
      ),
    );
  }
}

/// 应用错误码枚举
enum AppErrorCode {
  /// 网络错误
  networkError,

  /// 认证错误
  authError,

  /// 权限错误
  permissionError,

  /// 数据验证错误
  validationError,

  /// 业务逻辑错误
  businessError,

  /// 服务器错误
  serverError,

  /// 未知错误
  unknownError,
}

/// 应用错误模型
class AppError {
  final AppErrorCode code;
  final String message;
  final dynamic originalError;
  final StackTrace? stackTrace;

  AppError({
    required this.code,
    required this.message,
    this.originalError,
    this.stackTrace,
  });

  factory AppError.fromException(dynamic error, [StackTrace? stackTrace]) {
    if (error is SocketException) {
      return AppError(
        code: AppErrorCode.networkError,
        message: '网络连接失败',
        originalError: error,
        stackTrace: stackTrace,
      );
    } else if (error is DioException) {
      return _fromDioException(error, stackTrace);
    } else {
      return AppError(
        code: AppErrorCode.unknownError,
        message: GlobalErrorHandler.handleApiError(error),
        originalError: error,
        stackTrace: stackTrace,
      );
    }
  }

  static AppError _fromDioException(DioException error, StackTrace? stackTrace) {
    final statusCode = error.response?.statusCode;

    AppErrorCode code;
    if (statusCode == 401) {
      code = AppErrorCode.authError;
    } else if (statusCode == 403) {
      code = AppErrorCode.permissionError;
    } else if (statusCode == 422) {
      code = AppErrorCode.validationError;
    } else if (statusCode != null && statusCode >= 500) {
      code = AppErrorCode.serverError;
    } else {
      code = AppErrorCode.networkError;
    }

    return AppError(
      code: code,
      message: GlobalErrorHandler.handleApiError(error),
      originalError: error,
      stackTrace: stackTrace,
    );
  }

  @override
  String toString() => 'AppError(code: $code, message: $message)';
}
