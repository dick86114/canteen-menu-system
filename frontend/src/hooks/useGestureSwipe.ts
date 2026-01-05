import { useRef, useCallback } from 'react';
import type { SwipeGesture, SwipeConfig } from '../types/mobile';
import { debounce, throttle } from '../utils/animation';

/**
 * 手势识别 Hook
 * 监听触摸事件，识别滑动手势并触发相应回调
 *
 * @param config 手势识别配置
 * @returns 事件处理器和手势状态
 *
 * @example
 * const { handleTouchStart, handleTouchEnd, gestureState } = useGestureSwipe({
 *   onSwipeLeft: () => console.log('向左滑动'),
 *   onSwipeRight: () => console.log('向右滑动'),
 *   minSwipeDistance: 50,
 *   maxSwipeDuration: 500
 * })
 */
export function useGestureSwipe(config: SwipeConfig = {}) {
  const {
    minSwipeDistance = 50,
    maxSwipeDuration = 500,
    debounceDelay = 300,
    throttleDelay = 16,
    onSwipeLeft,
    onSwipeRight,
    onSwipeUp,
    onSwipeDown,
  } = config;

  // 存储触摸点信息
  const touchStartRef = useRef<{
    x: number;
    y: number;
    timestamp: number;
  } | null>(null);
  const isSwipingRef = useRef(false);

  /**
   * 计算滑动手势参数
   */
  const calculateSwipe = useCallback(
    (endX: number, endY: number, endTime: number): SwipeGesture | null => {
      if (!touchStartRef.current) return null;

      const {
        x: startX,
        y: startY,
        timestamp: startTime,
      } = touchStartRef.current;

      const deltaX = endX - startX;
      const deltaY = endY - startY;
      const deltaTime = endTime - startTime;

      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
      const velocity = distance / deltaTime;

      // 判断主要滑动方向
      let direction: 'left' | 'right' | 'up' | 'down';
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        // 水平滑动
        direction = deltaX > 0 ? 'right' : 'left';
      } else {
        // 垂直滑动
        direction = deltaY > 0 ? 'down' : 'up';
      }

      return {
        direction,
        distance,
        velocity,
        duration: deltaTime,
      };
    },
    []
  );

  /**
   * 验证手势是否有效
   */
  const isValidGesture = useCallback(
    (gesture: SwipeGesture): boolean => {
      // 滑动距离必须达到最小阈值
      if (gesture.distance < minSwipeDistance) return false;

      // 滑动时长必须在最大限制内
      if (gesture.duration > maxSwipeDuration) return false;

      // 滑动速度必须合理 (避免过慢或过快)
      if (gesture.velocity < 0.1 || gesture.velocity > 3) return false;

      return true;
    },
    [minSwipeDistance, maxSwipeDuration]
  );

  /**
   * 处理手势触发
   */
  const handleGesture = useCallback(
    (gesture: SwipeGesture) => {
      if (!isValidGesture(gesture)) return;

      // 防抖：避免快速连续触发
      const debouncedHandler = debounce(() => {
        switch (gesture.direction) {
          case 'left':
            if (onSwipeLeft) onSwipeLeft();
            break;
          case 'right':
            if (onSwipeRight) onSwipeRight();
            break;
          case 'up':
            if (onSwipeUp) onSwipeUp();
            break;
          case 'down':
            if (onSwipeDown) onSwipeDown();
            break;
        }
      }, debounceDelay);

      debouncedHandler();
    },
    [
      isValidGesture,
      onSwipeLeft,
      onSwipeRight,
      onSwipeUp,
      onSwipeDown,
      debounceDelay,
    ]
  );

  /**
   * 触摸开始
   */
  const handleTouchStart = useCallback((e: React.TouchEvent | TouchEvent) => {
    const touch = e.touches[0];
    touchStartRef.current = {
      x: touch.clientX,
      y: touch.clientY,
      timestamp: Date.now(),
    };
    isSwipingRef.current = true;
  }, []);

  /**
   * 触摸移动（使用节流优化）
   */
  const handleTouchMove = useCallback(
    throttle((e: React.TouchEvent | TouchEvent) => {
      if (!isSwipingRef.current || !touchStartRef.current) return;

      const touch = e.touches[0];
      const currentX = touch.clientX;
      const currentY = touch.clientY;
      const currentTime = Date.now();

      const gesture = calculateSwipe(currentX, currentY, currentTime);

      // 可以在这里实现实时跟随效果（可选）
      // 例如：translateX = gesture?.distance * 0.5
      void gesture; // 避免未使用变量警告
    }, throttleDelay),
    [calculateSwipe, throttleDelay]
  );

  /**
   * 触摸结束
   */
  const handleTouchEnd = useCallback(
    (e: React.TouchEvent | TouchEvent) => {
      if (!isSwipingRef.current || !touchStartRef.current) return;

      const touch = e.changedTouches[0];
      const endX = touch.clientX;
      const endY = touch.clientY;
      const endTime = Date.now();

      const gesture = calculateSwipe(endX, endY, endTime);

      if (gesture) {
        handleGesture(gesture);
      }

      // 重置状态
      touchStartRef.current = null;
      isSwipingRef.current = false;
    },
    [calculateSwipe, handleGesture]
  );

  /**
   * 触摸取消
   */
  const handleTouchCancel = useCallback(() => {
    touchStartRef.current = null;
    isSwipingRef.current = false;
  }, []);

  return {
    handleTouchStart,
    handleTouchMove,
    handleTouchEnd,
    handleTouchCancel,
    isSwiping: isSwipingRef.current,
  };
}

/**
 * 简化版手势 Hook（仅支持左右滑动）
 * 专门用于日期切换等水平滑动场景
 */
export function useHorizontalSwipe(config: {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  minSwipeDistance?: number;
  debounceDelay?: number;
}) {
  const {
    onSwipeLeft,
    onSwipeRight,
    minSwipeDistance = 50,
    debounceDelay = 300,
  } = config;

  const touchStartRef = useRef<{ x: number; timestamp: number } | null>(null);

  const handleTouchStart = useCallback((e: React.TouchEvent | TouchEvent) => {
    const touch = e.touches[0];
    touchStartRef.current = {
      x: touch.clientX,
      timestamp: Date.now(),
    };
  }, []);

  const handleTouchEnd = useCallback(
    (e: React.TouchEvent | TouchEvent) => {
      if (!touchStartRef.current) return;

      const touch = e.changedTouches[0];
      const deltaX = touch.clientX - touchStartRef.current.x;
      const deltaTime = Date.now() - touchStartRef.current.timestamp;

      // 检查是否为有效的水平滑动
      const isValidSwipe =
        Math.abs(deltaX) >= minSwipeDistance &&
        deltaTime < 500 &&
        Math.abs(deltaX) >
          Math.abs(touch.clientY - (e.touches[0]?.clientY || 0));

      if (isValidSwipe) {
        const debouncedHandler = debounce(() => {
          if (deltaX > 0) {
            onSwipeRight?.();
          } else {
            onSwipeLeft?.();
          }
        }, debounceDelay);

        debouncedHandler();
      }

      touchStartRef.current = null;
    },
    [onSwipeLeft, onSwipeRight, minSwipeDistance, debounceDelay]
  );

  return {
    handleTouchStart,
    handleTouchEnd,
  };
}
