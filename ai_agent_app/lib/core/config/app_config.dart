/// 应用配置
class AppConfig {
  // 环境配置 - 通过编译时环境变量设置
  // 使用方式: flutter run --dart-define=ENV=prod
  static const String environment = String.fromEnvironment('ENV', defaultValue: 'dev');

  // Supabase配置
  static const String supabaseUrl = 'https://dwesyojvzbltqtgtctpt.supabase.co';
  static const String supabaseAnonKey =
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY5MzA5MTQsImV4cCI6MjA4MjUwNjkxNH0.t4TBNkYp99HWBFu5kBOAgH13_7O5UADAMAptR16ENqc';

  // FastAPI后端配置 - 根据环境返回不同的URL
  // 本地开发时的Mac IP地址（用于真机调试）
  static const String localDevIp = '10.101.138.205';
  
  static String get apiBaseUrl {
    switch (environment) {
      case 'prod':
        // TODO: 替换为生产环境的实际URL
        return 'https://api.ee.production.com';
      case 'test':
        // TODO: 替换为测试环境的实际URL
        return 'https://api.ee.test.com';
      case 'mobile':
        // 真机调试使用电脑IP
        return 'http://$localDevIp:8000';
      case 'dev':
      default:
        return 'http://localhost:8000';
    }
  }

  static const String apiPrefix = '/api/v1';

  // 获取完整API路径
  static String get apiUrl => '$apiBaseUrl$apiPrefix';

  // 是否为生产环境
  static bool get isProduction => environment == 'prod';

  // 是否为开发环境
  static bool get isDevelopment => environment == 'dev';
}
