import React, { useState, useEffect, useCallback, useMemo } from 'react';
import MenuDisplay from './components/MenuDisplay';
import DateSelector from './components/DateSelector';
import ErrorBoundary from './components/ErrorBoundary';
import {
  NotificationProvider,
  useNotifications,
} from './components/NotificationSystem';
import NetworkStatusIndicator from './components/NetworkStatusIndicator';
import MobileGestureHandler from './components/MobileGestureHandler';
import {
  getMenuByDate,
  getAvailableDates,
  handleApiError,
  isNetworkError,
  isServerError,
  autoLoadMenuFiles,
} from './services/api';
import { MenuData } from './types';
import { useBreakpoint, useIsMobile } from './hooks/useMediaQuery';

// 主应用组件（内部）
const AppContent: React.FC = () => {
  // 移动端响应式断点（用于调试和未来扩展）
  const breakpoint = useBreakpoint();
  const isMobile = useIsMobile();

  // 在开发环境输出断点和设备信息
  if (process.env.NODE_ENV === 'development') {
    console.log('响应式断点:', breakpoint, '是否移动端:', isMobile);
  }

  // 手势状态
  const [gestureState, setGestureState] = useState<
    'idle' | 'swiping' | 'transition' | 'bouncing'
  >('idle');

  // 状态管理
  const [currentDate, setCurrentDate] = useState<string>('');
  const [menuData, setMenuData] = useState<MenuData | null>(null);
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [preloadedMenus, setPreloadedMenus] = useState<
    Record<string, MenuData>
  >({});

  // 计算餐次和菜品数量
  const mealCount = useMemo(() => {
    if (!menuData || !menuData.meals) return 0;
    return menuData.meals.length;
  }, [menuData]);

  const dishCount = useMemo(() => {
    if (!menuData || !menuData.meals) return 0;
    return menuData.meals.reduce((total, meal) => total + meal.items.length, 0);
  }, [menuData]);

  // 使用通知系统
  const { showError, showSuccess, showWarning } = useNotifications();

  // 获取今天的日期字符串（使用本地时间）
  const getTodayString = (): string => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // 切换到下一天（用于左滑）
  const goToNextDate = useCallback(() => {
    if (loading || gestureState !== 'idle') return;

    const currentIndex = availableDates.indexOf(currentDate);
    if (currentIndex < availableDates.length - 1) {
      setGestureState('swiping');
      const nextDate = availableDates[currentIndex + 1];
      setCurrentDate(nextDate);

      // 动画完成后重置状态
      setTimeout(() => {
        setGestureState('transition');
        setTimeout(() => {
          setGestureState('idle');
        }, 250);
      }, 50);
    } else {
      // 到达边界，显示回弹效果
      setGestureState('bouncing');
      setTimeout(() => {
        setGestureState('idle');
      }, 300);
    }
  }, [loading, gestureState, availableDates, currentDate]);

  // 切换到上一天（用于右滑）
  const goToPrevDate = useCallback(() => {
    if (loading || gestureState !== 'idle') return;

    const currentIndex = availableDates.indexOf(currentDate);
    if (currentIndex > 0) {
      setGestureState('swiping');
      const prevDate = availableDates[currentIndex - 1];
      setCurrentDate(prevDate);

      // 动画完成后重置状态
      setTimeout(() => {
        setGestureState('transition');
        setTimeout(() => {
          setGestureState('idle');
        }, 250);
      }, 50);
    } else {
      // 到达边界，显示回弹效果
      setGestureState('bouncing');
      setTimeout(() => {
        setGestureState('idle');
      }, 300);
    }
  }, [loading, gestureState, availableDates, currentDate]);

  // 获取可用日期列表
  const fetchAvailableDates = useCallback(async () => {
    try {
      const response = await getAvailableDates();
      setAvailableDates(response.dates);

      // 无论是否有菜单数据，都设置今天的日期
      const today = getTodayString();
      setCurrentDate(today);

      if (response.dates.length > 0) {
        console.log(`数据加载完成，共 ${response.dates.length} 天菜单数据`);
      } else {
        console.log('暂无菜单数据');
      }
    } catch (error) {
      console.error('获取可用日期失败:', error);
      const errorMessage = handleApiError(error);

      // 只在真正的网络错误时显示错误通知
      if (isNetworkError(error)) {
        showError('网络连接失败', '请检查网络连接后重试', true);
      } else if (isServerError(error)) {
        showError('服务器错误', '服务器暂时不可用，请稍后重试', true);
      } else {
        // 对于其他错误，只记录到控制台，不显示用户通知
        console.warn('加载可用日期时出现问题:', errorMessage);
      }

      setAvailableDates([]);
      setCurrentDate(getTodayString());
    }
  }, [showError]);

  // 预加载相邻日期的菜单数据（后台静默加载）
  const preloadAdjacentDates = useCallback(
    async (date: string) => {
      if (!date || availableDates.length === 0) return;

      const currentIndex = availableDates.indexOf(date);
      if (currentIndex === -1) return;

      try {
        // 确定需要预加载的日期（前一天和后一天）
        const datesToPreload: string[] = [];
        if (currentIndex > 0) {
          datesToPreload.push(availableDates[currentIndex - 1]);
        }
        if (currentIndex < availableDates.length - 1) {
          datesToPreload.push(availableDates[currentIndex + 1]);
        }

        // 后台静默加载，不阻塞 UI
        await Promise.allSettled(
          datesToPreload.map(async preloadDate => {
            // 如果已经预加载过，跳过
            if (preloadedMenus[preloadDate]) return;

            try {
              const response = await getMenuByDate(preloadDate);
              if (!response.fallback) {
                setPreloadedMenus(prev => ({
                  ...prev,
                  [preloadDate]: response,
                }));
              }
            } catch (err) {
              // 预加载失败静默处理，不影响用户体验
              console.warn(`预加载 ${preloadDate} 菜单失败:`, err);
            }
          })
        );
      } catch (err) {
        // 预加载整体失败也静默处理
        console.warn('预加载菜单失败:', err);
      }
    },
    [availableDates, preloadedMenus]
  );

  // 获取指定日期的菜单数据
  const fetchMenuData = useCallback(
    async (date: string) => {
      if (!date) return;

      // 优先使用预加载的数据
      if (preloadedMenus[date]) {
        setMenuData(preloadedMenus[date]);
        setError(null);
        // 触发预加载相邻日期
        preloadAdjacentDates(date);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await getMenuByDate(date);

        // 如果没有当前日期的菜单数据，设置为null显示空状态
        if (response.fallback) {
          setMenuData(null);
        } else {
          setMenuData(response);
          // 加载成功后预加载相邻日期
          preloadAdjacentDates(date);
        }
      } catch (err) {
        console.error('获取菜单数据失败:', err);
        const errorMessage = handleApiError(err);

        if (isNetworkError(err)) {
          showError('网络连接失败', '无法获取菜单数据，请检查网络连接');
        } else if (isServerError(err)) {
          showError('服务器错误', '无法获取菜单数据，服务器暂时不可用');
        } else {
          showError('加载菜单失败', errorMessage);
        }

        setMenuData(null);
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    },
    [preloadedMenus, preloadAdjacentDates, showError]
  );

  // 处理日期变化
  const handleDateChange = useCallback((date: string) => {
    setCurrentDate(date);
  }, []);

  // 手动刷新菜单数据
  const handleRefreshMenus = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const { refreshMenus } = await import('./services/api');
      const refreshResult = await refreshMenus();

      if (refreshResult.success) {
        showSuccess('菜单刷新成功', refreshResult.message);
        await fetchAvailableDates();
      } else {
        showWarning('菜单刷新', refreshResult.message);
      }
    } catch (error) {
      console.error('刷新菜单失败:', error);
      const errorMessage = handleApiError(error);
      setError(errorMessage);
      showError('刷新失败', errorMessage);
    } finally {
      setLoading(false);
    }
  }, [showSuccess, showWarning, showError, fetchAvailableDates]);

  // 重试加载（用于错误恢复）
  const handleRetry = useCallback(() => {
    if (currentDate) {
      fetchMenuData(currentDate);
    }
  }, [currentDate, fetchMenuData]);

  // 清除错误
  const handleClearError = useCallback(() => {
    setError(null);
  }, []);

  // 键盘导航支持
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 左右箭头键切换日期
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        goToPrevDate();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        goToNextDate();
      }
      // Esc 键清除错误
      else if (e.key === 'Escape' && error) {
        handleClearError();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [goToPrevDate, goToNextDate, error, handleClearError]);

  // 初始化应用 - 自动加载菜单文件
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // 首先尝试自动加载菜单文件
        const loadResult = await autoLoadMenuFiles();

        // 静默处理自动加载结果，不显示通知
        if (loadResult.success && loadResult.total_menus > 0) {
          console.log('菜单自动加载成功:', loadResult.message);
        } else if (!loadResult.success) {
          console.warn('自动加载菜单失败:', loadResult.message);
        }
      } catch (error) {
        console.warn('自动加载菜单时出错:', error);
        // 不显示错误通知，因为这可能是正常情况（没有文件等）
      }

      // 无论自动加载是否成功，都尝试获取可用日期
      await fetchAvailableDates();
    };

    initializeApp();
  }, []);

  // 当选中日期变化时，获取对应的菜单数据
  useEffect(() => {
    if (currentDate) {
      fetchMenuData(currentDate);
    }
  }, [currentDate]);

  return (
    <div
      className="min-vh-100"
      role="application"
      aria-label="食堂菜单系统"
    >
      {/* 导航栏 */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
        <div className="container">
          <a className="navbar-brand fw-bold" href="#">
            <i className="bi bi-calendar-week me-2"></i>
            食堂菜单系统
          </a>

          <div className="navbar-nav ms-auto d-flex flex-row gap-2">
            <button
              className="btn btn-outline-light btn-sm"
              onClick={handleRefreshMenus}
              disabled={loading}
              title="重新扫描menu目录下的菜单文件（支持Excel、WPS表格、CSV格式）"
            >
              <i
                className={`bi ${loading ? 'bi-arrow-clockwise' : 'bi-arrow-clockwise'} me-1 ${loading ? 'spin' : ''}`}
              ></i>
              刷新菜单
            </button>
          </div>
        </div>
      </nav>

      {/* 主要内容区域 */}
      <main className="container py-4" role="main" aria-label="菜单内容区域">
        {/* 网络状态指示器 */}
        <NetworkStatusIndicator />

        {/* 日期选择器 */}
        {availableDates.length > 0 && (
          <div className="mb-4" role="region" aria-label="日期选择">
            <DateSelector
              selectedDate={currentDate}
              onDateChange={handleDateChange}
              availableDates={availableDates}
              loading={loading}
              mealCount={mealCount}
              dishCount={dishCount}
            />
          </div>
        )}

        {/* 错误提示组件 */}
        {error && (
          <div
            className="mb-4"
            role="alert"
            aria-live="assertive"
            aria-atomic="true"
          >
            <div
              className="alert alert-danger alert-dismissible fade show"
              role="alert"
            >
              <i className="bi bi-exclamation-triangle-fill me-2"></i>
              <strong>加载失败：</strong> {error}
              <button
                type="button"
                className="btn-close"
                onClick={handleClearError}
                aria-label="关闭错误提示"
              ></button>
            </div>
            <button
              className="btn btn-outline-danger"
              onClick={handleRetry}
              aria-label="重试加载菜单"
            >
              <i className="bi bi-arrow-clockwise me-2"></i>
              重试
            </button>
          </div>
        )}

        {/* 根据是否有可用日期显示不同内容 */}
        {availableDates.length > 0 ? (
          /* 有菜单数据时显示菜单，包装手势处理器 */
          <div role="region" aria-label="菜单展示区域" aria-live="polite">
            <MobileGestureHandler
              onSwipeLeft={goToNextDate}
              onSwipeRight={goToPrevDate}
              disabled={loading || gestureState !== 'idle'}
              enableBounceEffect={true}
              config={{
                minSwipeDistance: 50,
                maxSwipeDuration: 500,
                debounceDelay: 300,
              }}
            >
              <MenuDisplay
                menuData={menuData}
                selectedDate={currentDate}
                loading={loading}
              />
            </MobileGestureHandler>
          </div>
        ) : (
          /* 无数据时的提示 */
          <div className="text-center py-5" role="status" aria-live="polite">
            <div className="mb-4">
              <i className="bi bi-inbox display-1 text-muted"></i>
            </div>
            <h3 className="text-muted mb-3">暂无菜单数据</h3>
            <p className="text-muted mb-4">
              系统中暂时没有菜单信息，请联系管理员添加菜单数据
            </p>
          </div>
        )}
      </main>

      {/* 页脚 */}
      <footer className="bg-dark text-light py-4 mt-auto">
        <div className="container">
          <div className="row">
            <div className="col-md-6">
              <h6 className="fw-bold">食堂菜单系统</h6>
              <p className="mb-0 small text-muted">
                简单易用的菜单管理和展示系统
              </p>
            </div>
            <div className="col-md-6 text-md-end">
              <small className="text-muted">
                <i className="bi bi-file-earmark-spreadsheet me-1"></i>
                支持Excel、WPS表格(.et)、CSV格式
              </small>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

// 主应用组件（带错误边界和通知系统）
const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <NotificationProvider>
        <AppContent />
      </NotificationProvider>
    </ErrorBoundary>
  );
};

export default App;
