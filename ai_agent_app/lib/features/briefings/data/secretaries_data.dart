import '../domain/models/secretary.dart';

const List<Secretary> secretariesData = [
  // 小智：始终显示，不映射任何Agent
  Secretary(
    id: 'general',
    name: '小智',
    title: '通用秘书',
    avatar: 'assets/images/secretary-boy-avatar.png',
    animatedAvatar: 'assets/images/secretary-boy-animated.gif',
    description: '猜你喜欢，智能推荐',
    mappedAgentRole: null,
    requiresSubscription: false,
  ),

  // 码码：映射到 AI资讯追踪官
  Secretary(
    id: 'dev',
    name: '码码',
    title: '研发秘书',
    avatar: 'assets/images/secretary-girl-avatar.png',
    animatedAvatar: 'assets/images/secretary-girl-animated.gif',
    description: 'AI资讯，技术前沿',
    mappedAgentRole: 'ai_news_crawler',
    requiresSubscription: true,
  ),

  // 商商：映射到 研发效能分析官
  Secretary(
    id: 'business',
    name: '商商',
    title: '商务秘书',
    avatar: 'assets/images/secretary-woman-avatar.png',
    animatedAvatar: 'assets/images/secretary-woman-animated.gif',
    description: '研发效能，团队协作',
    mappedAgentRole: 'dev_efficiency_analyst',
    requiresSubscription: true,
  ),

  // Chris Chen：新增第四个人物
  Secretary(
    id: 'chris_chen',
    name: 'Chris Chen',
    title: '设计评审官',
    avatar: 'assets/images/chris_chen_avatar.jpeg',
    animatedAvatar: null,  // 无动画GIF
    description: '设计验证，交互评审',
    mappedAgentRole: 'design_validator',
    requiresSubscription: true,
  ),
];
