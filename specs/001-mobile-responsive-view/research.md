# Research: 移动端响应式菜单视图与手势操作

**Feature**: 移动端响应式菜单视图与手势操作
**Date**: 2026-01-05
**Phase**: Phase 0 - Outline & Research

## 研究目标

为移动端响应式菜单视图和手势操作功能确定最佳技术实现方案，解决以下关键技术问题：
1. 响应式布局实现策略
2. 手势识别最佳实践
3. 动画效果实现方式
4. 性能优化方案
5. 可访问性保障

---

## 决策 1: 响应式布局实现

### 选项评估

| 选项 | 技术方案 | 优点 | 缺点 |
|------|---------|------|------|
| A | Bootstrap 5 媒体查询 | 项目已使用，学习成本低，Grid 系统成熟 | 定制化受限，需额外 CSS |
| B | CSS-in-JS (styled-components) | 完全定制化，主题切换方便 | 需要新增依赖，增加包大小 |
| C | 原生 CSS 媒体查询 + SCSS | 性能最优，无运行时开销，编译时优化 | 需要维护 SCSS 文件 |

### 最终决策: **选项 C - 原生 CSS 媒体查询 + SCSS**

**理由**:
1. **性能优势**: 编译时生成 CSS，无运行时开销，符合宪章性能要求（FCP <3s）
2. **项目一致性**: 现有项目已配置 Vite，原生支持 SCSS，无需新增配置
3. **Bootstrap 兼容**: 可以继续使用 Bootstrap 5 组件，通过 SCSS 覆盖样式实现定制
4. **维护性**: SCSS 变量和混合宏支持样式复用，易于维护
5. **包大小**: 不增加客户端 JavaScript 负载，符合移动端性能要求

**实现方案**:
- 使用 SCSS 变量定义断点（320px, 375px, 768px, 1024px, 1440px）
- 创建 `frontend/src/styles/responsive.scss` 统一管理响应式样式
- 利用 Bootstrap 5 的 `@include media-breakpoint-*()` 混合宏
- 移动优先策略（Mobile First），从最小屏幕开始向上适配

**技术细节**:
```scss
// 定义断点
$breakpoints: (
  'xs': 320px,   // 小屏手机
  'sm': 375px,   // 中大屏手机
  'md': 768px,   // 平板
  'lg': 1024px,  // 桌面
  'xl': 1440px   // 大屏桌面
);

// 媒体查询混合宏
@mixin respond-to($breakpoint) {
  @if map-has-key($breakpoints, $breakpoint) {
    @media (min-width: map-get($breakpoints, $breakpoint)) {
      @content;
    }
  }
}
```

---

## 决策 2: 手势识别实现

### 选项评估

| 选项 | 技术方案 | 优点 | 缺点 |
|------|---------|------|------|
| A | react-swipeable 库 | 开箱即用，API 简单 | 新增 5KB+ 依赖，功能受限 |
| B | react-use-useGesture 库 | 功能强大，支持所有手势 | 库体积大 (20KB+)，过度设计 |
| C | 原生 Touch Events API | 零依赖，完全控制，性能最优 | 需要自己实现手势逻辑 |

### 最终决策: **选项 C - 原生 Touch Events API**

**理由**:
1. **零依赖**: 不增加第三方库，符合宪章"简单性优于灵活性"原则
2. **性能最优**: 直接操作原生事件，无中间层开销，手势响应 <100ms
3. **功能需求匹配**: 仅需实现左右滑动、双击、长按，不需要复杂手势库
4. **学习价值**: 原生 API 知识可复用，不依赖特定库
5. **包大小**: 不增加客户端负载，符合移动端性能要求

**实现方案**:
- 创建自定义 React Hook `useGestureSwipe` 封装 Touch Events API
- 创建自定义 React Hook `useMediaQuery` 封装媒体查询逻辑
- 创建工具函数 `gesture.ts` 提供手势识别核心算法
- 支持 `touchstart`, `touchmove`, `touchend` 事件监听
- 实现防抖（debounce）和节流（throttle）机制避免快速滑动导致请求混乱

**技术细节**:
```typescript
// 手势识别参数
interface SwipeGesture {
  direction: 'left' | 'right' | 'up' | 'down';
  distance: number;      // 滑动距离（像素）
  velocity: number;      // 滑动速度（像素/毫秒）
  duration: number;      // 滑动时长（毫秒）
}

// 配置参数
interface SwipeConfig {
  minSwipeDistance: number;  // 最小滑动距离（默认 50px）
  maxSwipeDuration: number;  // 最大滑动时长（默认 500ms）
  threshold: number;         // 触发阈值（默认 30px）
}

// 防抖配置
interface DebounceConfig {
  delay: number;  // 延迟时间（默认 300ms）
}
```

---

## 决策 3: 动画效果实现

### 选项评估

| 选项 | 技术方案 | 优点 | 缺点 |
|------|---------|------|------|
| A | CSS Transitions | 简单易用，性能好 | 仅支持简单过渡 |
| B | CSS Animations (@keyframes) | 支持复杂动画序列 | 难以动态控制 |
| C | React Transition Group | React 生态集成好 | 新增依赖，性能稍差 |
| D | Framer Motion | 功能强大，声明式 | 库体积大 (40KB+)，过度设计 |

### 最终决策: **选项 A + B 混合 - CSS Transitions + CSS Animations**

**理由**:
1. **性能最优**: 利用 GPU 加速，60fps 动画流畅度
2. **零依赖**: 不增加第三方库，使用原生 CSS 特性
3. **需求匹配**: 滑动切换、模态框弹出、菜单显示等场景 CSS 足够
4. **轻量级**: 不增加 JavaScript 负载，动画逻辑由浏览器引擎处理
5. **可控性**: 通过 CSS 类名控制动画状态，React 管理状态切换

**实现方案**:
- 创建 `frontend/src/styles/animations.scss` 统一管理动画
- 使用 CSS Transitions 实现简单过渡（hover、focus、模态框淡入淡出）
- 使用 CSS Animations 实现复杂序列（滑动切换、弹性回弹）
- 通过 React 状态切换 CSS 类名触发动画
- 使用 `will-change` 属性优化性能

**技术细节**:
```scss
// 滑动切换动画（200-300ms）
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideInLeft {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

// 弹性回弹动画（边界反馈）
@keyframes bounceBack {
  0% { transform: translateX(0); }
  30% { transform: translateX(-20px); }
  50% { transform: translateX(10px); }
  70% { transform: translateX(-5px); }
  100% { transform: translateX(0); }
}

// 模态框淡入淡出
.modal-enter {
  opacity: 0;
  transform: scale(0.9);
}

.modal-enter-active {
  opacity: 1;
  transform: scale(1);
  transition: opacity 200ms ease-out, transform 200ms ease-out;
}

.modal-exit {
  opacity: 1;
  transform: scale(1);
}

.modal-exit-active {
  opacity: 0;
  transform: scale(0.9);
  transition: opacity 150ms ease-in, transform 150ms ease-in;
}
```

---

## 决策 4: 性能优化策略

### 关键性能指标 (KPI)

根据规格说明的成功标准：
- 手势响应时间: < 100ms
- 首屏内容绘制 (FCP): < 3s (4G 网络)
- 动画帧率: 60fps
- 触摸目标尺寸: ≥ 44x44px

### 优化方案

#### 4.1 手势性能优化

| 优化项 | 技术方案 | 预期效果 |
|--------|---------|---------|
| 事件监听优化 | 使用 `passive: true` 事件监听器 | 滚动和触摸响应提升 30% |
| 防抖节流 | 快速滑动时使用 debounce (300ms) | 避免多余请求，减少 80% API 调用 |
| requestAnimationFrame | 动画帧使用 rAF 调度 | 保证 60fps 流畅度 |
| 节流更新 | 使用 throttle (16ms) 限制状态更新 | 减少 90% 不必要渲染 |

#### 4.2 渲染性能优化

| 优化项 | 技术方案 | 预期效果 |
|--------|---------|---------|
| React.memo | 包装纯组件避免重渲染 | 减少 50% 组件渲染 |
| useMemo | 缓存计算结果（日期列表、菜单数据） | 减少 70% 计算开销 |
| useCallback | 稳定事件处理器引用 | 减少子组件不必要更新 |
| 懒加载 | React.lazy() 按需加载模态框组件 | 初始包大小减少 30% |

#### 4.3 加载性能优化

| 优化项 | 技术方案 | 预期效果 |
|--------|---------|---------|
| 骨架屏 | 数据加载时显示占位符 | 用户感知加载时间减少 50% |
| 预加载 | 预加载相邻日期菜单数据 | 滑动切换无延迟 |
| 代码分割 | 路由级别代码分割 (Vite 自动) | 初始 JS 减少 40% |
| 图片优化 | 使用 WebP 格式，lazy loading | 带宽节省 60% |

#### 4.4 样式性能优化

| 优化项 | 技术方案 | 预期效果 |
|--------|---------|---------|
| will-change | 提示浏览器优化动画元素 | 动画流畅度提升 20% |
| transform | 使用 transform 而非 left/top | 启用 GPU 加速 |
| 避免布局抖动 | 使用 CSS Containment | 减少重排重绘 |

---

## 决策 5: 可访问性 (A11y) 保障

### 需求分析

规格说明 FR-015: "手势操作不得影响屏幕阅读器等辅助功能的可用性"

### 实现方案

#### 5.1 键盘导航支持

| 场景 | 键盘操作 | 实现方式 |
|------|---------|---------|
| 切换日期 | 左/右箭头键 | 监听 `keydown` 事件 |
| 打开详情 | Enter/Space 键 | 添加 `role="button"` |
| 关闭模态框 | Esc 键 | 监听 `keydown` 事件 |
| 焦点陷阱 | Tab/Shift+Tab | 使用 React FocusTrap |

#### 5.2 屏幕阅读器支持

| 元素 | ARIA 属性 | 实现方式 |
|------|-----------|---------|
| 手势区域 | `role="region"`, `aria-label="滑动切换日期"` | 语义化标签 |
| 模态框 | `role="dialog"`, `aria-modal="true"` | ARIA 规范 |
| 加载状态 | `aria-busy="true"`, `aria-live="polite"` | 实时通知 |
| 错误提示 | `role="alert"`, `aria-live="assertive"` | 错误通知 |

#### 5.3 触摸目标优化

根据 WCAG 2.1 AAA 标准：
- 最小触摸目标: 44x44px (iOS), 48x48dp (Android)
- 目标间距: 至少 8px
- 对比度: 至少 4.5:1 (正常文本), 3:1 (大文本)

**实现方案**:
```scss
// 增大触摸目标
.touch-target {
  min-width: 44px;
  min-height: 44px;
  padding: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
```

---

## 技术风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| iOS Safari 滚动冲突 | 中 | 使用 `touch-action` CSS 属性控制触摸行为 |
| Android 浏览器兼容性 | 低 | 目标 Android 8+ (Chrome 85+)，Modern APIs 支持良好 |
| 快速滑动导致性能问题 | 中 | Debounce/Throttle 机制 + requestAnimationFrame |
| 横竖屏切换布局错乱 | 低 | 使用 CSS 媒体查询 `orientation` 检测 |
| 手势误触 | 中 | 设置合理的滑动距离阈值 (50px) 和速度阈值 (0.3px/ms) |

---

## 替代方案考虑

### 手势库替代方案

**未选择**: `react-swipeable`, `react-use-gesture`

**原因**:
1. 功能需求简单（仅需滑动、双击、长按），不需要复杂手势库
2. 增加依赖违反"简单性优于灵活性"原则
3. 原生 API 性能更优，包大小更小

### CSS-in-JS 替代方案

**未选择**: `styled-components`, `emotion`

**原因**:
1. 运行时样式生成增加性能开销
2. 项目已有 Bootstrap 5，SCSS 方案更兼容
3. 增加包大小（styled-components ~13KB）

---

## 最佳实践参考

### 响应式设计

- **Mobile First**: 从最小屏幕开始设计，逐步增强到桌面端
- **流体网格**: 使用百分比和 `fr` 单位而非固定像素
- **弹性图片**: `max-width: 100%`, `object-fit: cover`

### 手势交互

- **反馈及时**: 视觉反馈应在 100ms 内出现
- **可撤销**: 误操作可快速撤销（如模态框关闭）
- **一致性**: 遵循平台约定（iOS vs Android 手势差异）

### 性能优化

- **测量优先**: 使用 Lighthouse, Chrome DevTools 测量性能
- **渐进增强**: 基础功能优先，动画为增强体验
- **代码分割**: 按路由和功能分割代码块

---

## 技术栈确认

### 前端核心依赖（无变更）

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.2.2",
  "bootstrap": "^5.3.2",
  "axios": "^1.6.0",
  "vite": "^4.5.0"
}
```

### 新增开发依赖

```json
{
  "sass": "^1.69.0"  // SCSS 编译器（Vite 原生支持，无需配置）
}
```

**注意**: 无需新增运行时依赖！

---

## 研究结论

所有关键技术决策已完成，确定了：
1. ✅ 响应式布局: SCSS + Bootstrap 5 媒体查询
2. ✅ 手势识别: 原生 Touch Events API + 自定义 Hooks
3. ✅ 动画效果: CSS Transitions + Animations
4. ✅ 性能优化: 防抖节流 + React 性能优化 + 懒加载
5. ✅ 可访问性: 键盘导航 + ARIA 属性 + 触摸目标优化

**无 NEEDS CLARIFICATION 项** - 所有技术决策已明确，可进入 Phase 1 设计阶段。
