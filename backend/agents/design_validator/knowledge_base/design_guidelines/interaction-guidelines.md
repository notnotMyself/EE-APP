# 交互设计规范

## 触摸目标尺寸

### 最小尺寸要求

- **iOS**: 44x44 points (根据Apple Human Interface Guidelines)
- **Android**: 48x48 dp (根据Material Design)
- **通用建议**: 48x48 points/dp

### 间距要求

- 相邻可点击元素之间至少保持 8pt 间距
- 高优先级操作按钮至少 56x56 pt

## 输入框设计

### 标签和提示

- 使用浮动标签（Float Label）提升空间利用
- 占位符文字与输入文字颜色对比度 >= 4.5:1
- 错误提示应紧邻输入框下方，红色文字

### 密码输入

- 必须提供"显示/隐藏密码"切换按钮
- 图标通常为眼睛图标（👁️）
- 位置：输入框右侧内部

## 反馈机制

### 加载状态

- 操作超过1秒应显示加载指示器
- 全屏加载使用中心Spinner
- 局部加载使用Skeleton Screen或Progress Bar

### 成功/错误反馈

- 成功：绿色Toast/Snackbar，3秒自动消失
- 错误：红色Toast/Snackbar，需要用户主动关闭
- 警告：橙色Toast/Snackbar，5秒自动消失

## 导航模式

### 返回操作

- iOS: 左上角返回按钮 + 手势滑动
- Android: 系统返回键 + 左上角返回按钮
- 深层页面应提供面包屑导航

### Tab Bar

- 图标+文字标签
- 最多5个Tab
- 当前Tab高亮显示
- 未读数字角标位于图标右上角

## 可访问性

### 颜色对比度

- 正文文字: >= 4.5:1 (WCAG AA)
- 大字体(18pt+): >= 3:1
- 交互元素: >= 3:1

### 屏幕阅读器

- 所有交互元素必须有contentDescription/accessibilityLabel
- 图片必须有alt text
- 复杂组件提供accessibility hints

## 错误预防

### 确认对话框

- 破坏性操作（删除、清空）必须二次确认
- 确认按钮用红色强调
- 提供撤销选项（如果可能）

### 输入验证

- 实时验证（输入时或失焦时）
- 明确告知错误原因
- 提供修正建议

## 平台惯例

### iOS

- 使用系统标准控件（UIKit/SwiftUI）
- 遵循Apple HIG
- 大标题导航栏
- 卡片式Sheet呈现

### Android

- 使用Material Components
- Floating Action Button用于主要操作
- Bottom Sheet用于次要操作集合
- Snackbar用于轻量级反馈

## 手势

### 常用手势

- 点击: 选择/激活
- 长按: 显示上下文菜单
- 滑动: 列表滚动、页面切换
- 捏合: 缩放（地图、图片）
- 下拉: 刷新列表

### 手势冲突

- 避免在同一区域定义冲突的手势
- 优先保留系统手势（如返回滑动）
