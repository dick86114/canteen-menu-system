import { useState, useEffect, useCallback } from 'react';
import { getMenuByDate, getAvailableDates } from '../services/api';
import { handleApiError } from '../services/api';
import type {
  MobileMenuState,
  MobileMenuActions,
  ModalState,
  Breakpoint,
} from '../types/mobile';

/**
 * 移动端菜单状态管理 Hook
 * 管理日期导航、加载状态、错误处理、模态框状态等核心逻辑
 */
export function useMobileMenuState(
  initialDate?: string
): [MobileMenuState, MobileMenuActions] {
  // 日期导航状态
  const [currentDate, setCurrentDate] = useState<string>(
    initialDate || new Date().toISOString().split('T')[0]
  );
  const [availableDates, setAvailableDates] = useState<string[]>([]);

  // 加载状态
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isPreloading, setIsPreloading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // 手势状态（暂时未使用，为 US2 预留）
  const [gestureState] = useState<
    'idle' | 'swiping' | 'transition' | 'bouncing'
  >('idle');
  const [isSwiping] = useState<boolean>(false);

  // 模态框状态（为 US3 预留）
  const [modalState, setModalState] = useState<ModalState>({
    isOpen: false,
    data: undefined,
    animation: null,
  });

  const [quickActionMenu, setQuickActionMenu] = useState<
    ModalState<{
      item: any;
      position: { x: number; y: number };
    }>
  >({
    isOpen: false,
    data: undefined,
    animation: null,
  });

  // 媒体查询状态
  const [breakpoint, setBreakpoint] = useState<Breakpoint>('md');
  const [isPortrait, setIsPortrait] = useState<boolean>(true);

  /**
   * 加载指定日期的菜单数据
   */
  const loadMenu = useCallback(async (date: string) => {
    setIsLoading(true);
    setError(null);

    try {
      await getMenuByDate(date);
      setCurrentDate(date);
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error('加载菜单失败:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * 切换到指定日期
   */
  const goToDate = useCallback(
    (date: string) => {
      if (date === currentDate) return;
      loadMenu(date);
    },
    [currentDate, loadMenu]
  );

  /**
   * 切换到下一天（US2 功能预留）
   */
  const goToNextDate = useCallback(() => {
    const currentIndex = availableDates.indexOf(currentDate);
    if (currentIndex < availableDates.length - 1) {
      const nextDate = availableDates[currentIndex + 1];
      loadMenu(nextDate);
    }
  }, [availableDates, currentDate, loadMenu]);

  /**
   * 切换到上一天（US2 功能预留）
   */
  const goToPrevDate = useCallback(() => {
    const currentIndex = availableDates.indexOf(currentDate);
    if (currentIndex > 0) {
      const prevDate = availableDates[currentIndex - 1];
      loadMenu(prevDate);
    }
  }, [availableDates, currentDate, loadMenu]);

  /**
   * 预加载相邻日期（性能优化）
   */
  const preloadAdjacentDates = useCallback(async () => {
    const currentIndex = availableDates.indexOf(currentDate);
    if (currentIndex === -1) return;

    setIsPreloading(true);

    try {
      // 后台静默加载前一天和后一天的数据
      const datesToPreload = [];
      if (currentIndex > 0) {
        datesToPreload.push(availableDates[currentIndex - 1]);
      }
      if (currentIndex < availableDates.length - 1) {
        datesToPreload.push(availableDates[currentIndex + 1]);
      }

      // 并行预加载
      await Promise.allSettled(datesToPreload.map(date => getMenuByDate(date)));
    } catch (err) {
      // 预加载失败不影响主流程，静默处理
      console.warn('预加载菜单失败:', err);
    } finally {
      setIsPreloading(false);
    }
  }, [availableDates, currentDate]);

  /**
   * 手势操作处理器（US2 功能预留）
   */
  const handleSwipeLeft = useCallback(() => {
    goToNextDate();
  }, [goToNextDate]);

  const handleSwipeRight = useCallback(() => {
    goToPrevDate();
  }, [goToPrevDate]);

  /**
   * 双击和长按处理器（US3 功能预留）
   */
  const handleDoubleTap = useCallback((item: any) => {
    setModalState({
      isOpen: true,
      data: item,
      animation: 'enter',
    });
  }, []);

  const handleLongPress = useCallback(
    (item: any, position: { x: number; y: number }) => {
      setQuickActionMenu({
        isOpen: true,
        data: { item, position },
        animation: 'enter',
      });
    },
    []
  );

  /**
   * 模态框操作
   */
  const openModal = useCallback((item: any) => {
    setModalState({
      isOpen: true,
      data: item,
      animation: 'enter',
    });
  }, []);

  const closeModal = useCallback(() => {
    setModalState(prev => ({ ...prev, animation: 'exit' }));
    // 动画结束后关闭
    setTimeout(() => {
      setModalState({
        isOpen: false,
        data: undefined,
        animation: null,
      });
    }, 200);
  }, []);

  const openQuickActionMenu = useCallback(
    (item: any, position: { x: number; y: number }) => {
      setQuickActionMenu({
        isOpen: true,
        data: { item, position },
        animation: 'enter',
      });
    },
    []
  );

  const closeQuickActionMenu = useCallback(() => {
    setQuickActionMenu(prev => ({ ...prev, animation: 'exit' }));
    // 动画结束后关闭
    setTimeout(() => {
      setQuickActionMenu({
        isOpen: false,
        data: undefined,
        animation: null,
      });
    }, 200);
  }, []);

  /**
   * 快捷操作处理器（US3 功能预留）
   */
  const handleQuickAction = useCallback(
    async (action: string, item: any) => {
      // 当前仅 UI 演示，未来可实现实际功能
      console.log(`快捷操作: ${action}`, item);

      switch (action) {
        case 'favorite':
          // TODO: 实现收藏功能
          console.log('收藏菜品:', item.name);
          break;
        case 'share':
          // TODO: 实现分享功能
          console.log('分享菜品:', item.name);
          break;
        case 'note':
          // TODO: 实现备注功能
          console.log('添加备注:', item.name);
          break;
        case 'report':
          // TODO: 实现举报功能
          console.log('举报菜品:', item.name);
          break;
      }

      closeQuickActionMenu();
    },
    [closeQuickActionMenu]
  );

  /**
   * 重试加载
   */
  const retryLoad = useCallback(() => {
    setError(null);
    loadMenu(currentDate);
  }, [currentDate, loadMenu]);

  /**
   * 清除错误
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * 初始化：加载可用日期列表
   */
  useEffect(() => {
    const initDates = async () => {
      try {
        const response = await getAvailableDates();
        setAvailableDates(response.dates);

        // 如果 initialDate 不在可用日期中，使用第一个可用日期
        if (
          !availableDates.includes(currentDate) &&
          response.dates.length > 0
        ) {
          setCurrentDate(response.dates[0]);
        }
      } catch (err) {
        const errorMessage = handleApiError(err);
        setError(errorMessage);
        console.error('加载日期列表失败:', err);
      }
    };

    initDates();
  }, []);

  /**
   * 响应断点变化
   */
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      let newBreakpoint: Breakpoint;

      if (width < 375) {
        newBreakpoint = 'xs';
      } else if (width < 768) {
        newBreakpoint = 'sm';
      } else if (width < 1024) {
        newBreakpoint = 'md';
      } else if (width < 1440) {
        newBreakpoint = 'lg';
      } else {
        newBreakpoint = 'xl';
      }

      setBreakpoint(newBreakpoint);
      setIsPortrait(window.innerHeight > window.innerWidth);
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  /**
   * 监听屏幕方向变化
   */
  useEffect(() => {
    const handleOrientationChange = () => {
      setIsPortrait(window.innerHeight > window.innerWidth);
    };

    window.addEventListener('resize', handleOrientationChange);
    return () => window.removeEventListener('resize', handleOrientationChange);
  }, []);

  /**
   * 当前日期变化时，预加载相邻日期
   */
  useEffect(() => {
    if (availableDates.length > 0) {
      preloadAdjacentDates();
    }
  }, [currentDate, availableDates, preloadAdjacentDates]);

  // 组合状态和操作
  const state: MobileMenuState = {
    currentDate,
    availableDates,
    isLoading,
    isPreloading,
    error,
    gestureState,
    isSwiping,
    modalState,
    quickActionMenu,
    breakpoint,
    isPortrait,
  };

  const actions: MobileMenuActions = {
    goToNextDate,
    goToPrevDate,
    goToDate,
    preloadAdjacentDates,
    handleSwipeLeft,
    handleSwipeRight,
    handleDoubleTap,
    handleLongPress,
    openModal,
    closeModal,
    openQuickActionMenu,
    closeQuickActionMenu,
    handleQuickAction,
    retryLoad,
    clearError,
  };

  return [state, actions];
}
