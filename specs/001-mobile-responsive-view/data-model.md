# Data Model: 移动端响应式菜单视图与手势操作

**Feature**: 移动端响应式菜单视图与手势操作
**Date**: 2026-01-05
**Phase**: Phase 1 - Design & Contracts

## 概述

本功能**不涉及后端数据模型变更**，完全复用现有菜单数据结构。所有新增类型定义位于前端 TypeScript 层，用于支持移动端交互逻辑。

---

## 后端数据模型（无变更）

### 现有模型（复用）

#### MenuItem
**文件**: `backend/app/models/menu.py`

```python
@dataclass
class MenuItem:
    name: str
    description: Optional[str]
    category: Optional[str]      # 档口分类
    price: Optional[float]
    order: int                   # 菜品排序
    category_order: int          # 分类排序
```

**验证规则**:
- `name`: 必填，非空字符串
- `price`: 非负数（如果提供）
- `order`, `category_order`: 非负整数

#### Meal
**文件**: `backend/app/models/menu.py`

```python
@dataclass
class Meal:
    type: str                    # 'breakfast' | 'lunch' | 'dinner'
    time: str                    # HH:MM 格式
    items: List[MenuItem]
```

**验证规则**:
- `type`: 必须为 'breakfast', 'lunch', 'dinner' 之一
- `time`: 必须符合 HH:MM 格式
- `items`: 所有 MenuItem 必须通过验证

#### MenuData
**文件**: `backend/app/models/menu.py`

```python
@dataclass
class MenuData:
    date: str                    # YYYY-MM-DD 格式
    meals: List[Meal]
```

**验证规则**:
- `date`: 必须符合 YYYY-MM-DD 格式
- `meals`: 所有 Meal 必须通过验证，按时间排序

**存储**: 内存单例（`backend/app/models/storage.py`）

---

## 前端类型定义（新增）

### 移动端专用类型

#### SwipeGesture
**文件**: `frontend/src/types/mobile.ts`

```typescript
/**
 * 手势识别结果
 */
interface SwipeGesture {
  direction: 'left' | 'right' | 'up' | 'down';
  distance: number;      // 滑动距离（像素）
  velocity: number;      // 滑动速度（像素/毫秒）
  duration: number;      // 滑动时长（毫秒）
}
```

#### SwipeConfig
**文件**: `frontend/src/types/mobile.ts`

```typescript
/**
 * 手势识别配置
 */
interface SwipeConfig {
  minSwipeDistance?: number;   // 最小滑动距离（默认 50px）
  maxSwipeDuration?: number;   // 最大滑动时长（默认 500ms）
  threshold?: number;          // 触发阈值（默认 30px）
  debounceDelay?: number;      // 防抖延迟（默认 300ms）
  throttleDelay?: number;      // 节流延迟（默认 16ms）
}
```

#### TouchPoint
**文件**: `frontend/src/types/mobile.ts`

```typescript
/**
 * 触摸点坐标
 */
interface TouchPoint {
  x: number;
  y: number;
  timestamp: number;  // 时间戳（毫秒）
}
```

#### AnimationState
**文件**: `frontend/src/types/mobile.ts`

```typescript
/**
 * 动画状态
 */
type AnimationState =
  | 'idle'        // 空闲
  | 'swiping'     // 滑动中
  | 'transition'  // 过渡中
  | 'bouncing';   // 边界回弹
```

#### ModalState
**文件**: `frontend/src/types/mobile.ts`

```typescript
/**
 * 模态框状态
 */
interface ModalState<T = any> {
  isOpen: boolean;
  data?: T;
  animation: 'enter' | 'exit' | null;
}
```

#### QuickAction
**文件**: `frontend/src/types/mobile.ts`

```typescript
/**
 * 快捷操作类型
 */
type QuickActionType =
  | 'favorite'  // 收藏
  | 'share'     // 分享
  | 'note'      // 备注
  | 'report';   // 举报

/**
 * 快捷操作配置
 */
interface QuickAction {
  type: QuickActionType;
  label: string;
  icon: string;
  handler: () => void | Promise<void>;
}
```

#### MediaQueryBreakpoint
**文件**: `frontend/src/types/mobile.ts`

```typescript
/**
 * 媒体查询断点
 */
type Breakpoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

interface MediaQueryConfig {
  breakpoint: Breakpoint;
  minWidth: number;
  maxWidth?: number;
  orientation?: 'portrait' | 'landscape';
}
```

---

### 扩展现有类型

#### MenuItem 扩展
**文件**: `frontend/src/types/mobile.ts`

```typescript
import { MenuItem } from './index';

/**
 * 移动端增强的菜单项
 */
interface MobileMenuItem extends MenuItem {
  isSpecial?: boolean;        // 是否为档口特色（档口特色标记功能）
  StallLocation?: string;     // 档口位置
  nutritionInfo?: {           // 营养信息（P3 功能）
    calories?: number;
    protein?: number;
    carbs?: number;
    fat?: number;
  };
}
```

#### MenuResponse 扩展
**文件**: `frontend/src/types/mobile.ts`

```typescript
import { MenuResponse } from './index';

/**
 * 移动端菜单响应（扩展）
 */
interface MobileMenuResponse extends MenuResponse {
  metadata?: {
    preload?: {              // 预加载元数据
      prevDate?: string;     // 前一天日期
      nextDate?: string;     // 后一天日期
    };
  };
}
```

---

## 状态管理模型

### React State 组织

#### MobileMenuState
**文件**: `frontend/src/hooks/useMobileMenuState.ts`

```typescript
/**
 * 移动端菜单状态
 */
interface MobileMenuState {
  // 日期导航
  currentDate: string;
  availableDates: string[];

  // 加载状态
  isLoading: boolean;
  isPreloading: boolean;      // 预加载中
  error: string | null;

  // 手势状态
  gestureState: AnimationState;
  isSwiping: boolean;

  // 模态框状态
  modalState: ModalState<MobileMenuItem>;
  quickActionMenu: ModalState<{
    item: MobileMenuItem;
    position: { x: number; y: number };
  }>;

  // 媒体查询
  breakpoint: Breakpoint;
  isPortrait: boolean;
}
```

#### MobileMenuActions
**文件**: `frontend/src/hooks/useMobileMenuState.ts`

```typescript
/**
 * 移动端菜单操作
 */
interface MobileMenuActions {
  // 日期操作
  goToNextDate: () => void;
  goToPrevDate: () => void;
  goToDate: (date: string) => void;
  preloadAdjacentDates: () => Promise<void>;

  // 手势操作
  handleSwipeLeft: () => void;
  handleSwipeRight: () => void;
  handleDoubleTap: (item: MobileMenuItem) => void;
  handleLongPress: (item: MobileMenuItem, position: { x: number; y: number }) => void;

  // 模态框操作
  openModal: (item: MobileMenuItem) => void;
  closeModal: () => void;
  openQuickActionMenu: (item: MobileMenuItem, position: { x: number; y: number }) => void;
  closeQuickActionMenu: () => void;

  // 快捷操作
  handleQuickAction: (action: QuickActionType, item: MobileMenuItem) => Promise<void>;

  // 加载操作
  retryLoad: () => void;
  clearError: () => void;
}
```

---

## 数据流图

### 组件数据流

```
┌─────────────────────────────────────────────────────────────────┐
│                         App.tsx                                  │
│  (管理全局状态: currentDate, breakpoint, modalState)            │
└──────┬────────────────────────────────────────────────┬─────────┘
       │                                                │
       │                                                │
       ▼                                                ▼
┌──────────────────────┐                    ┌──────────────────────┐
│  DateSelector.tsx    │                    │  MenuDisplay.tsx     │
│  (日期选择器)         │                    │  (菜单展示)           │
│  - 响应式样式         │                    │  - 响应式布局         │
│  - 移动端友好模式     │                    │  - 手势监听           │
└──────────────────────┘                    └──────────┬───────────┘
                                                       │
                                       ┌───────────────┼───────────────┐
                                       │               │               │
                                       ▼               ▼               ▼
                            ┌─────────────────┐ ┌──────────┐ ┌─────────────────┐
                            │MenuItemModal.tsx│ │QuickAction│ │MobileGesture    │
                            │(菜品详情模态框) │ │Menu.tsx  │ │Handler.tsx      │
                            │- 双击触发       │ │(长按菜单) │ │(手势识别组件)    │
                            │- 动画效果       │ │- 操作选项 │ │- 滑动识别       │
                            └─────────────────┘ └──────────┘ └─────────────────┘
```

### 数据获取流程

```
用户操作 (滑动/点击)
    ↓
手势识别 (useGestureSwipe)
    ↓
触发 Action (goToNextDate / goToPrevDate)
    ↓
调用 API (api.getMenuByDate)
    ↓
更新状态 (MobileMenuState)
    ↓
组件重渲染 (MenuDisplay, MenuItemModal)
    ↓
动画过渡 (CSS Animations)
```

---

## 验证规则

### 前端验证

#### 手势输入验证
```typescript
// 验证滑动是否有效
function isValidSwipe(gesture: SwipeGesture, config: SwipeConfig): boolean {
  const {
    minSwipeDistance = 50,
    maxSwipeDuration = 500,
    threshold = 30
  } = config;

  // 滑动距离必须达到阈值
  if (gesture.distance < minSwipeDistance) return false;

  // 滑动时长必须在限制内
  if (gesture.duration > maxSwipeDuration) return false;

  // 滑动方向必须明确
  if (Math.abs(gesture.distance) < threshold) return false;

  return true;
}
```

#### 日期边界验证
```typescript
// 验证日期是否在有效范围内
function isValidDateTransition(
  current: string,
  target: string,
  availableDates: string[]
): boolean {
  const currentIndex = availableDates.indexOf(current);
  const targetIndex = availableDates.indexOf(target);

  // 只允许切换到相邻日期
  return Math.abs(targetIndex - currentIndex) === 1;
}
```

#### 触摸目标验证
```scss
// 触摸目标尺寸验证（WCAG 2.1 AAA）
.touch-target {
  min-width: 44px;   // iOS 标准
  min-height: 44px;
  padding: 12px;     // 确保间距
}
```

---

## 持久化策略

### 无持久化需求

本功能不涉及数据持久化，所有状态均为运行时状态：
- 日期选择状态: 存储在 React State 中
- 模态框状态: 存储在 React State 中
- 手势状态: 存储在 React State 中

**注意**: 如果未来需要记住用户最后查看的日期，可使用 `localStorage`:
```typescript
// 可选功能（不在本次实现范围）
localStorage.setItem('lastViewedDate', currentDate);
```

---

## 性能优化数据结构

### 预加载缓存

```typescript
/**
 * 预加载缓存（LRU Cache）
 */
interface PreloadCache {
  current: string;           // 当前日期
  prev: MenuResponse | null; // 前一天缓存
  next: MenuResponse | null; // 后一天缓存
  maxSize: 2;                // 最多缓存 2 个相邻日期
}
```

### 防抖/节流队列

```typescript
/**
 * 手势事件队列（防止快速滑动）
 */
interface GestureEventQueue {
  pending: SwipeGesture[];
  processing: boolean;
  lastProcessed: number;     // 上次处理时间戳
  debounceDelay: number;     // 防抖延迟
}
```

---

## 数据模型总结

### 后端变更
- ✅ **无变更** - 完全复用现有 `MenuItem`, `Meal`, `MenuData` 模型

### 前端新增类型
- ✅ SwipeGesture, SwipeConfig, TouchPoint - 手势识别
- ✅ AnimationState, ModalState - 交互状态
- ✅ QuickAction, QuickActionType - 快捷操作
- ✅ MediaQueryBreakpoint - 响应式断点
- ✅ MobileMenuItem, MobileMenuResponse - 移动端扩展

### 状态管理
- ✅ MobileMenuState - 全局状态接口
- ✅ MobileMenuActions - 操作接口
- ✅ 预加载缓存、防抖队列 - 性能优化

### 验证规则
- ✅ 手势输入验证 - 滑动距离、时长、方向
- ✅ 日期边界验证 - 相邻日期切换
- ✅ 触摸目标验证 - WCAG 2.1 AAA 标准

**数据模型设计完成** - 可进入 API 契约设计阶段。
