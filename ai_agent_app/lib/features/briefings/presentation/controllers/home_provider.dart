import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/secretaries_data.dart';

enum ViewMode { cards, grid }

final homeViewModeProvider = StateProvider<ViewMode>((ref) => ViewMode.cards);

final activeSecretaryIndexProvider = StateProvider<int>((ref) => 0);

final activeSecretaryProvider = Provider((ref) {
  final index = ref.watch(activeSecretaryIndexProvider);
  return secretariesData[index];
});
