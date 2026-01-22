import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:uuid/uuid.dart';

import '../widgets/expanded_chat_input.dart';

/// 附件服务
/// 
/// 提供图片选择、文件选择功能
class AttachmentService {
  final ImagePicker _imagePicker = ImagePicker();
  final Uuid _uuid = const Uuid();

  /// 从相册选择图片
  Future<ChatAttachment?> pickImageFromGallery() async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 85,
      );

      if (image == null) return null;

      return ChatAttachment(
        id: _uuid.v4(),
        localPath: image.path,
        networkUrl: null,
        thumbnailUrl: null,
        mimeType: _getMimeType(image.path),
        filename: image.name,
      );
    } catch (e) {
      debugPrint('选择图片失败: $e');
      return null;
    }
  }

  /// 拍照
  Future<ChatAttachment?> takePhoto() async {
    try {
      final XFile? photo = await _imagePicker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 85,
      );

      if (photo == null) return null;

      return ChatAttachment(
        id: _uuid.v4(),
        localPath: photo.path,
        networkUrl: null,
        thumbnailUrl: null,
        mimeType: _getMimeType(photo.path),
        filename: photo.name,
      );
    } catch (e) {
      debugPrint('拍照失败: $e');
      return null;
    }
  }

  /// 选择多张图片
  Future<List<ChatAttachment>> pickMultipleImages({int maxImages = 9}) async {
    try {
      final List<XFile> images = await _imagePicker.pickMultiImage(
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 85,
      );

      // 限制最大数量
      final limitedImages = images.take(maxImages).toList();

      return limitedImages.map((image) => ChatAttachment(
        id: _uuid.v4(),
        localPath: image.path,
        networkUrl: null,
        thumbnailUrl: null,
        mimeType: _getMimeType(image.path),
        filename: image.name,
      )).toList();
    } catch (e) {
      debugPrint('选择多张图片失败: $e');
      return [];
    }
  }

  /// 选择文件（附件）
  Future<ChatAttachment?> pickFile() async {
    try {
      final FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar', 'jpg', 'jpeg', 'png', 'gif', 'webp'],
        allowMultiple: false,
      );

      if (result == null || result.files.isEmpty) return null;

      final file = result.files.first;

      return ChatAttachment(
        id: _uuid.v4(),
        localPath: file.path,
        networkUrl: null,
        thumbnailUrl: null,
        mimeType: _getMimeType(file.path ?? ''),
        filename: file.name,
      );
    } catch (e) {
      debugPrint('选择文件失败: $e');
      return null;
    }
  }

  /// 选择多个文件
  Future<List<ChatAttachment>> pickMultipleFiles({int maxFiles = 5}) async {
    try {
      final FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar', 'jpg', 'jpeg', 'png', 'gif', 'webp'],
        allowMultiple: true,
      );

      if (result == null || result.files.isEmpty) return [];

      // 限制最大数量
      final limitedFiles = result.files.take(maxFiles).toList();

      return limitedFiles.map((file) => ChatAttachment(
        id: _uuid.v4(),
        localPath: file.path,
        networkUrl: null,
        thumbnailUrl: null,
        mimeType: _getMimeType(file.path ?? ''),
        filename: file.name,
      )).toList();
    } catch (e) {
      debugPrint('选择多个文件失败: $e');
      return [];
    }
  }

  /// 获取MIME类型
  String _getMimeType(String path) {
    final ext = path.toLowerCase().split('.').last;
    const mimeTypes = {
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'gif': 'image/gif',
      'webp': 'image/webp',
      'pdf': 'application/pdf',
      'doc': 'application/msword',
      'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'xls': 'application/vnd.ms-excel',
      'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'ppt': 'application/vnd.ms-powerpoint',
      'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'txt': 'text/plain',
      'zip': 'application/zip',
      'rar': 'application/x-rar-compressed',
    };
    return mimeTypes[ext] ?? 'application/octet-stream';
  }

  /// 获取文件大小（格式化）
  String getFormattedFileSize(String? path) {
    if (path == null) return '';
    
    try {
      final file = File(path);
      final bytes = file.lengthSync();
      
      if (bytes < 1024) return '$bytes B';
      if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
      if (bytes < 1024 * 1024 * 1024) return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
      return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
    } catch (e) {
      return '';
    }
  }

  /// 获取文件扩展名
  String getFileExtension(String? path) {
    if (path == null) return '';
    final parts = path.split('.');
    return parts.isNotEmpty ? parts.last.toUpperCase() : '';
  }

  /// 判断是否为图片
  bool isImage(String? path) {
    if (path == null) return false;
    final ext = path.toLowerCase();
    return ext.endsWith('.jpg') || 
           ext.endsWith('.jpeg') || 
           ext.endsWith('.png') || 
           ext.endsWith('.gif') || 
           ext.endsWith('.webp');
  }
}

/// 附件服务 Provider
final attachmentServiceProvider = Provider<AttachmentService>((ref) {
  return AttachmentService();
});

