import '../domain/models/secretary.dart';

const List<Secretary> secretariesData = [
  Secretary(
    id: 'general',
    name: '小智',
    title: '通用秘书',
    avatar: 'assets/images/secretary-boy-avatar.png',
    animatedAvatar: 'assets/images/secretary-boy-animated.gif',
    description: '猜你喜欢，智能推荐',
  ),
  Secretary(
    id: 'dev',
    name: '码码',
    title: '研发秘书',
    avatar: 'assets/images/secretary-girl-avatar.png',
    animatedAvatar: 'assets/images/secretary-girl-animated.gif',
    description: '技术资讯，代码助手',
  ),
  Secretary(
    id: 'business',
    name: '商商',
    title: '商务秘书',
    avatar: 'assets/images/secretary-woman-avatar.png',
    animatedAvatar: 'assets/images/secretary-woman-animated.gif',
    description: '商业洞察，市场分析',
  ),
];
