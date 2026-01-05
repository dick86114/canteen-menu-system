import React, { useState } from 'react';
import { useGestureSwipe } from '../hooks/useGestureSwipe';
import type { SwipeConfig } from '../types/mobile';
import './MobileGestureHandler.css';

interface MobileGestureHandlerProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  config?: SwipeConfig;
  className?: string;
  disabled?: boolean;
  enableBounceEffect?: boolean;
}

/**
 * 移动端手势识别组件
 * 包装子组件，为其添加滑动手势识别功能
 *
 * @example
 * <MobileGestureHandler
 *   onSwipeLeft={() => goToNextDate()}
 *   onSwipeRight={() => goToPrevDate()}
 *   enableBounceEffect={true}
 * >
 *   <MenuDisplay menuData={menuData} />
 * </MobileGestureHandler>
 */
export const MobileGestureHandler: React.FC<MobileGestureHandlerProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  config = {},
  className = '',
  disabled = false,
  enableBounceEffect = true,
}) => {
  const [animationState, setAnimationState] = useState<
    'idle' | 'slide-left' | 'slide-right' | 'bounce'
  >('idle');

  const handleSwipeLeft = () => {
    if (disabled) return;

    setAnimationState('slide-left');
    onSwipeLeft?.();

    // 动画结束后重置状态
    setTimeout(() => {
      setAnimationState('idle');
    }, 300);
  };

  const handleSwipeRight = () => {
    if (disabled) return;

    setAnimationState('slide-right');
    onSwipeRight?.();

    // 动画结束后重置状态
    setTimeout(() => {
      setAnimationState('idle');
    }, 300);
  };

  const handleSwipeWithBounce = (
    _direction: 'left' | 'right',
    handler: () => void
  ) => {
    if (disabled || !enableBounceEffect) {
      handler();
      return;
    }

    // 先执行切换
    handler();

    // 检测是否到达边界（这里简化处理，实际应该从 props 传入）
    // 如果到达边界，显示回弹动画
    setAnimationState('bounce');
    setTimeout(() => {
      setAnimationState('idle');
    }, 300);
  };

  const {
    handleTouchStart,
    handleTouchMove,
    handleTouchEnd,
    handleTouchCancel,
  } = useGestureSwipe({
    ...config,
    onSwipeLeft: () => handleSwipeWithBounce('left', handleSwipeLeft),
    onSwipeRight: () => handleSwipeWithBounce('right', handleSwipeRight),
    onSwipeUp,
    onSwipeDown,
  });

  const getAnimationClass = () => {
    switch (animationState) {
      case 'slide-left':
        return 'menu-slide-enter';
      case 'slide-right':
        return 'menu-slide-exit';
      case 'bounce':
        return 'bounce-back';
      default:
        return '';
    }
  };

  return (
    <div
      className={`gesture-handler ${getAnimationClass()} ${className}`}
      onTouchStart={disabled ? undefined : handleTouchStart}
      onTouchMove={disabled ? undefined : handleTouchMove}
      onTouchEnd={disabled ? undefined : handleTouchEnd}
      onTouchCancel={disabled ? undefined : handleTouchCancel}
      style={{
        touchAction: 'pan-y', // 允许垂直滚动，阻止水平默认行为
        WebkitTouchCallout: 'none', // 禁止 iOS 长按菜单
        userSelect: 'none', // 禁止选中文本
      }}
    >
      {children}
    </div>
  );
};

export default MobileGestureHandler;
