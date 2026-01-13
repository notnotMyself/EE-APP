/// 应用配置
class AppConfig {
  // Supabase配置
  static const String supabaseUrl = 'https://dwesyojvzbltqtgtctpt.supabase.co';
  static const String supabaseAnonKey =
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY5MzA5MTQsImV4cCI6MjA4MjUwNjkxNH0.t4TBNkYp99HWBFu5kBOAgH13_7O5UADAMAptR16ENqc';

  // FastAPI后端配置
  static const String apiBaseUrl = 'http://localhost:8000';
  static const String apiPrefix = '/api/v1';

  // 获取完整API路径
  static String get apiUrl => '$apiBaseUrl$apiPrefix';
}
