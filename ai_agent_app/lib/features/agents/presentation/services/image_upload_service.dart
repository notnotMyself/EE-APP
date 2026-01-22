import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:uuid/uuid.dart';
import 'package:path/path.dart' as path;

import '../widgets/expanded_chat_input.dart';

/// 图片上传服务
///
/// 负责将本地附件上传到 Supabase Storage
class ImageUploadService {
  final _uuid = const Uuid();
  static const String _bucketName = 'attachments';

  /// 上传单个附件到 Supabase Storage
  ///
  /// [attachment] 要上传的附件
  ///
  /// 返回更新后的附件（包含 networkUrl）
  Future<ChatAttachment> uploadAttachment(ChatAttachment attachment) async {
    if (attachment.localPath == null) {
      return attachment.copyWith(status: AttachmentStatus.error);
    }

    try {
      final file = File(attachment.localPath!);
      if (!await file.exists()) {
        debugPrint('文件不存在: ${attachment.localPath}');
        return attachment.copyWith(status: AttachmentStatus.error);
      }

      // 生成唯一文件名
      final extension = path.extension(attachment.localPath!).toLowerCase();
      final fileName = '${_uuid.v4()}$extension';
      final storagePath = 'chat-attachments/$fileName';

      final supabase = Supabase.instance.client;

      // 上传到 Supabase Storage
      await supabase.storage
          .from(_bucketName)
          .upload(storagePath, file);

      // 获取公开 URL
      final publicUrl = supabase.storage
          .from(_bucketName)
          .getPublicUrl(storagePath);

      debugPrint('附件上传成功: $publicUrl');

      return attachment.copyWith(
        networkUrl: publicUrl,
        status: AttachmentStatus.uploaded,
      );
    } catch (e) {
      debugPrint('附件上传失败: $e');
      return attachment.copyWith(status: AttachmentStatus.error);
    }
  }

  /// 批量上传附件
  ///
  /// [attachments] 要上传的附件列表
  /// [onProgress] 进度回调（当前索引，总数）
  ///
  /// 返回更新后的附件列表
  Future<List<ChatAttachment>> uploadAttachments(
    List<ChatAttachment> attachments, {
    void Function(int current, int total)? onProgress,
  }) async {
    final results = <ChatAttachment>[];

    for (var i = 0; i < attachments.length; i++) {
      final attachment = attachments[i];

      // 如果已经上传过，跳过
      if (attachment.isUploaded) {
        results.add(attachment);
        continue;
      }

      onProgress?.call(i + 1, attachments.length);

      final uploaded = await uploadAttachment(attachment);
      results.add(uploaded);
    }

    return results;
  }

  /// 获取 MIME 类型
  String getMimeType(String? filePath) {
    if (filePath == null) return 'application/octet-stream';

    final ext = path.extension(filePath).toLowerCase();
    switch (ext) {
      case '.jpg':
      case '.jpeg':
        return 'image/jpeg';
      case '.png':
        return 'image/png';
      case '.gif':
        return 'image/gif';
      case '.webp':
        return 'image/webp';
      case '.pdf':
        return 'application/pdf';
      case '.doc':
        return 'application/msword';
      case '.docx':
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      case '.xls':
        return 'application/vnd.ms-excel';
      case '.xlsx':
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      case '.txt':
        return 'text/plain';
      default:
        return 'application/octet-stream';
    }
  }

  /// 判断是否为支持的图片类型
  bool isImageFile(String? filePath) {
    if (filePath == null) return false;
    final ext = path.extension(filePath).toLowerCase();
    return ['.jpg', '.jpeg', '.png', '.gif', '.webp'].contains(ext);
  }
}

/// ImageUploadService Provider
final imageUploadServiceProvider = Provider<ImageUploadService>((ref) {
  return ImageUploadService();
});
