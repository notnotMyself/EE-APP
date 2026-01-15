import 'dart:io';
import 'package:flutter/material.dart';
import 'package:jpush_flutter/jpush_flutter.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:logger/logger.dart';

/// 推送通知服务
///
/// 负责：
/// - 初始化 JPush 和本地通知
/// - 获取和管理 Registration ID
/// - 处理前台/后台/关闭状态的通知
/// - 实现通知点击导航
class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final JPush _jpush = JPush();
  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();
  final Logger _logger = Logger();

  /// 通知点击回调
  Function(String briefingId)? onNotificationTapped;

  /// 初始化通知服务
  Future<void> initialize({
    required String jpushAppKey,
    required BuildContext context,
  }) async {
    try {
      _logger.i('Initializing notification service...');

      // 1. 初始化 JPush
      await _initializeJPush(jpushAppKey);

      // 2. 初始化本地通知
      await _initializeLocalNotifications();

      // 3. 设置通知处理器
      _setupNotificationHandlers();

      _logger.i('Notification service initialized successfully');
    } catch (e, stackTrace) {
      _logger.e('Failed to initialize notification service', e, stackTrace);
      rethrow;
    }
  }

  /// 初始化 JPush
  Future<void> _initializeJPush(String appKey) async {
    // 配置 JPush
    _jpush.setup(
      appKey: appKey,
      channel: 'developer-default',
      production: false, // TODO: 生产环境改为 true
      debug: true,
    );

    // 请求通知权限 (iOS)
    _jpush.applyPushAuthority(NotificationSettingsIOS(
      sound: true,
      alert: true,
      badge: true,
    ));

    // 获取 Registration ID 并保存到后端
    try {
      final regId = await _jpush.getRegistrationID();
      if (regId != null && regId.isNotEmpty) {
        _logger.i('Got registration ID: $regId');
        await _saveRegistrationIdToBackend(regId);
      } else {
        _logger.w('Registration ID is null or empty');
      }
    } catch (e) {
      _logger.e('Failed to get registration ID: $e');
    }
  }

  /// 初始化本地通知
  Future<void> _initializeLocalNotifications() async {
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const settings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      settings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    // Android: 创建通知渠道
    if (Platform.isAndroid) {
      const channel = AndroidNotificationChannel(
        'briefings_channel',
        'Briefings',
        description: 'AI员工简报通知',
        importance: Importance.high,
        playSound: true,
        enableVibration: true,
      );

      await _localNotifications
          .resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>()
          ?.createNotificationChannel(channel);
    }
  }

  /// 设置 JPush 通知处理器
  void _setupNotificationHandlers() {
    // 接收通知（前台）
    _jpush.addEventHandler(
      onReceiveNotification: (Map<String, dynamic> message) async {
        _logger.i('Received notification (foreground): $message');
        await _showLocalNotification(message);
      },

      // 打开通知（用户点击）
      onOpenNotification: (Map<String, dynamic> message) {
        _logger.i('Opened notification: $message');
        _handleNotificationNavigation(message);
      },

      // 接收自定义消息
      onReceiveMessage: (Map<String, dynamic> message) {
        _logger.i('Received custom message: $message');
      },

      // Registration ID 获取回调
      onReceiveNotificationAuthorization: (Map<String, dynamic> status) {
        _logger.i('Notification authorization status: $status');
      },
    );
  }

  /// 显示本地通知
  Future<void> _showLocalNotification(Map<String, dynamic> message) async {
    try {
      final String title = message['title'] ?? 'AI员工通知';
      final String body = message['alert'] ?? message['content'] ?? '';
      final Map<String, dynamic>? extras = message['extras'];

      const androidDetails = AndroidNotificationDetails(
        'briefings_channel',
        'Briefings',
        channelDescription: 'AI员工简报通知',
        importance: Importance.high,
        priority: Priority.high,
        playSound: true,
        enableVibration: true,
      );

      const iosDetails = DarwinNotificationDetails(
        presentAlert: true,
        presentBadge: true,
        presentSound: true,
      );

      const details = NotificationDetails(
        android: androidDetails,
        iOS: iosDetails,
      );

      await _localNotifications.show(
        DateTime.now().millisecondsSinceEpoch ~/ 1000,
        title,
        body,
        details,
        payload: extras?['briefing_id'],
      );
    } catch (e) {
      _logger.e('Failed to show local notification: $e');
    }
  }

  /// 处理通知导航
  void _handleNotificationNavigation(Map<String, dynamic> message) {
    try {
      final extras = message['extras'] as Map<String, dynamic>?;
      if (extras == null) return;

      final type = extras['type'] as String?;
      final briefingId = extras['briefing_id'] as String?;

      if (type == 'briefing' && briefingId != null) {
        // 调用导航回调
        onNotificationTapped?.call(briefingId);
      }
    } catch (e) {
      _logger.e('Failed to handle notification navigation: $e');
    }
  }

  /// 通知点击回调
  void _onNotificationTapped(NotificationResponse response) {
    final payload = response.payload;
    if (payload != null) {
      _logger.i('Notification tapped with payload: $payload');
      onNotificationTapped?.call(payload);
    }
  }

  /// 保存 Registration ID 到后端
  Future<void> _saveRegistrationIdToBackend(String regId) async {
    try {
      final userId = Supabase.instance.client.auth.currentUser?.id;
      if (userId == null) {
        _logger.w('User not logged in, cannot save registration ID');
        return;
      }

      final platform = Platform.isIOS ? 'ios' : 'android';

      // 调用后端 API
      final response = await Supabase.instance.client.functions.invoke(
        'api/v1/notifications/register-device',
        body: {
          'registration_id': regId,
          'platform': platform,
          'device_name': null,
          'device_model': null,
          'os_version': Platform.operatingSystemVersion,
          'app_version': '1.0.0', // TODO: 从 package_info 获取
        },
      );

      if (response.status == 200) {
        _logger.i('Registration ID saved successfully');
      } else {
        _logger.e('Failed to save registration ID: ${response.data}');
      }
    } catch (e) {
      _logger.e('Error saving registration ID: $e');
    }
  }

  /// 请求通知权限
  Future<bool> requestPermission() async {
    try {
      if (Platform.isAndroid) {
        // Android 13+ 需要请求通知权限
        final granted = await _localNotifications
                .resolvePlatformSpecificImplementation<
                    AndroidFlutterLocalNotificationsPlugin>()
                ?.areNotificationsEnabled() ??
            true;
        return granted;
      } else if (Platform.isIOS) {
        // iOS 请求权限
        final result = await _localNotifications
            .resolvePlatformSpecificImplementation<
                IOSFlutterLocalNotificationsPlugin>()
            ?.requestPermissions(
              alert: true,
              badge: true,
              sound: true,
            );
        return result ?? false;
      }
      return true;
    } catch (e) {
      _logger.e('Failed to request notification permission: $e');
      return false;
    }
  }

  /// 获取 Registration ID
  Future<String?> getRegistrationId() async {
    try {
      return await _jpush.getRegistrationID();
    } catch (e) {
      _logger.e('Failed to get registration ID: $e');
      return null;
    }
  }

  /// 设置角标数字 (iOS)
  Future<void> setBadge(int badge) async {
    try {
      await _jpush.setBadge(badge);
    } catch (e) {
      _logger.e('Failed to set badge: $e');
    }
  }

  /// 清除所有通知
  Future<void> clearAllNotifications() async {
    try {
      await _jpush.clearAllNotifications();
      await _localNotifications.cancelAll();
    } catch (e) {
      _logger.e('Failed to clear notifications: $e');
    }
  }

  /// 注销 (用户登出时调用)
  Future<void> unregister() async {
    try {
      final regId = await getRegistrationId();
      if (regId != null) {
        // 调用后端注销设备
        final userId = Supabase.instance.client.auth.currentUser?.id;
        if (userId != null) {
          await Supabase.instance.client.functions.invoke(
            'api/v1/notifications/unregister-device',
            body: {'registration_id': regId},
          );
        }
      }

      // 清空 JPush 设置
      await _jpush.deleteAlias();
      await clearAllNotifications();

      _logger.i('Unregistered from push notifications');
    } catch (e) {
      _logger.e('Failed to unregister: $e');
    }
  }
}
