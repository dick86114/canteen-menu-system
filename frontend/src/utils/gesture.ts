/**
 * 手势工具函数
 * 用于手势识别和验证
 */

import { SwipeGesture, SwipeConfig } from '../types/mobile';

/**
 * 验证滑动是否有效
 * @param gesture 手势对象
 * @param config 配置对象
 * @returns 是否为有效滑动
 */
export function isValidSwipe(
  gesture: SwipeGesture,
  config: SwipeConfig
): boolean {
  const {
    minSwipeDistance = 50,
    maxSwipeDuration = 500,
    threshold = 30,
  } = config;

  // 滑动距离必须达到阈值
  if (Math.abs(gesture.distance) < minSwipeDistance) return false;

  // 滑动时长必须在限制内
  if (gesture.duration > maxSwipeDuration) return false;

  // 滑动方向必须明确
  if (Math.abs(gesture.distance) < threshold) return false;

  return true;
}

/**
 * 验证日期是否在有效范围内
 * @param current 当前日期
 * @param target 目标日期
 * @param availableDates 可用日期列表
 * @returns 是否为有效日期转换
 */
export function isValidDateTransition(
  current: string,
  target: string,
  availableDates: string[]
): boolean {
  const currentIndex = availableDates.indexOf(current);
  const targetIndex = availableDates.indexOf(target);

  // 只允许切换到相邻日期
  return Math.abs(targetIndex - currentIndex) === 1;
}

/**
 * 计算滑动距离
 * @param startX 起始 X 坐标
 * @param startY 起始 Y 坐标
 * @param endX 结束 X 坐标
 * @param endY 结束 Y 坐标
 * @returns 滑动距离和方向
 */
export function calculateSwipeDistance(
  startX: number,
  startY: number,
  endX: number,
  endY: number
): {
  deltaX: number;
  deltaY: number;
  distance: number;
  direction: 'horizontal' | 'vertical' | null;
} {
  const deltaX = endX - startX;
  const deltaY = endY - startY;
  const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

  // 判断主要滑动方向
  let direction: 'horizontal' | 'vertical' | null = null;
  if (Math.abs(deltaX) > Math.abs(deltaY)) {
    direction = 'horizontal';
  } else if (Math.abs(deltaY) > Math.abs(deltaX)) {
    direction = 'vertical';
  }

  return { deltaX, deltaY, distance, direction };
}
