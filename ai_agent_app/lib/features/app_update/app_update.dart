/// 应用更新功能
///
/// 提供完整的 APP 在线更新能力：
/// - 版本检查
/// - APK 下载
/// - 自动安装
/// - 多下载源支持
///
/// 使用方式：
/// ```dart
/// // 1. 在应用启动时检查更新
/// await AppUpdateService.checkUpdateOnStartup(context, ref, silent: true);
///
/// // 2. 手动检查更新（从设置页面）
/// await AppUpdateService.checkUpdateManually(context, ref);
/// ```
library app_update;

// 数据模型
export 'data/models/app_version.dart';

// 数据仓库
export 'data/repositories/update_repository.dart';

// 控制器
export 'presentation/controllers/update_controller.dart';

// UI 组件
export 'presentation/widgets/update_dialog.dart';

// 服务
export 'services/app_update_service.dart';
