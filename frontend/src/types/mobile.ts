/**
 * 移动端类型定义
 * 用于支持移动端响应式菜单视图和手势操作功能
 */

import { MenuItem } from './index';

/**
 * 手势识别结果
 */
export interface SwipeGesture {
  direction: 'left' | 'right' | 'up' | 'down';
  distance: number; // 滑动距离（像素）
  velocity: number; // 滑动速度（像素/毫秒）
  duration: number; // 滑动时长（毫秒）
}

/**
 * 手势识别配置
 */
export interface SwipeConfig {
  minSwipeDistance?: number; // 最小滑动距离（默认 50px）
  maxSwipeDuration?: number; // 最大滑动时长（默认 500ms）
  threshold?: number; // 触发阈值（默认 30px）
  debounceDelay?: number; // 防抖延迟（默认 300ms）
  throttleDelay?: number; // 节流延迟（默认 16ms）
  onSwipeLeft?: () => void; // 左滑回调
  onSwipeRight?: () => void; // 右滑回调
  onSwipeUp?: () => void; // 上滑回调
  onSwipeDown?: () => void; // 下滑回调
}

/**
 * 触摸点坐标
 */
export interface TouchPoint {
  x: number;
  y: number;
  timestamp: number; // 时间戳（毫秒）
}

/**
 * 动画状态
 */
export type AnimationState =
  | 'idle' // 空闲
  | 'swiping' // 滑动中
  | 'transition' // 过渡中
  | 'bouncing'; // 边界回弹

/**
 * 模态框状态
 */
export interface ModalState<T = any> {
  isOpen: boolean;
  data?: T;
  animation: 'enter' | 'exit' | null;
}

/**
 * 快捷操作类型
 */
export type QuickActionType =
  | 'favorite' // 收藏
  | 'share' // 分享
  | 'note' // 备注
  | 'report'; // 举报

/**
 * 快捷操作配置
 */
export interface QuickAction {
  type: QuickActionType;
  label: string;
  icon: string;
  handler: () => void | Promise<void>;
}

/**
 * 媒体查询断点
 */
export type Breakpoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

/**
 * 媒体查询配置
 */
export interface MediaQueryConfig {
  breakpoint: Breakpoint;
  minWidth: number;
  maxWidth?: number;
  orientation?: 'portrait' | 'landscape';
}

/**
 * 移动端增强的菜单项
 */
export interface MobileMenuItem extends MenuItem {
  isSpecial?: boolean; // 是否为档口特色
  StallLocation?: string; // 档口位置
  nutritionInfo?: {
    // 营养信息
    calories?: number;
    protein?: number;
    carbs?: number;
    fat?: number;
  };
}

/**
 * 移动端菜单状态
 */
export interface MobileMenuState {
  // 日期导航
  currentDate: string;
  availableDates: string[];

  // 加载状态
  isLoading: boolean;
  isPreloading: boolean;
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

/**
 * 移动端菜单操作
 */
export interface MobileMenuActions {
  // 日期操作
  goToNextDate: () => void;
  goToPrevDate: () => void;
  goToDate: (date: string) => void;
  preloadAdjacentDates: () => Promise<void>;

  // 手势操作
  handleSwipeLeft: () => void;
  handleSwipeRight: () => void;
  handleDoubleTap: (item: MobileMenuItem) => void;
  handleLongPress: (
    item: MobileMenuItem,
    position: { x: number; y: number }
  ) => void;

  // 模态框操作
  openModal: (item: MobileMenuItem) => void;
  closeModal: () => void;
  openQuickActionMenu: (
    item: MobileMenuItem,
    position: { x: number; y: number }
  ) => void;
  closeQuickActionMenu: () => void;

  // 快捷操作
  handleQuickAction: (
    action: QuickActionType,
    item: MobileMenuItem
  ) => Promise<void>;

  // 加载操作
  retryLoad: () => void;
  clearError: () => void;
}
