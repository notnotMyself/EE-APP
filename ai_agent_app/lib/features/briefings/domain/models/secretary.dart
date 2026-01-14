class Secretary {
  final String id;
  final String name;
  final String title;
  final String avatar;
  final String? animatedAvatar;
  final String description;

  const Secretary({
    required this.id,
    required this.name,
    required this.title,
    required this.avatar,
    this.animatedAvatar,
    required this.description,
  });
}
