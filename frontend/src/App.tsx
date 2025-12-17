import React, { useState, useEffect } from 'react';
import MenuDisplay from './components/MenuDisplay';
import DateSelector from './components/DateSelector';
import ErrorBoundary from './components/ErrorBoundary';
import { NotificationProvider, useNotifications } from './components/NotificationSystem';
import NetworkStatusIndicator from './components/NetworkStatusIndicator';
import { getMenuByDate, getAvailableDates, handleApiError, isNetworkError, isServerError, autoLoadMenuFiles } from './services/api';
import { MenuData } from './types';

// 主应用组件（内部）
const AppContent: React.FC = () => {
  // 状态管理
  const [currentDate, setCurrentDate] = useState<string>('');
  const [menuData, setMenuData] = useState<MenuData | null>(null);
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  
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

  // 获取可用日期列表
  const fetchAvailableDates = async () => {
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
  };

  // 获取指定日期的菜单数据
  const fetchMenuData = async (date: string) => {
    if (!date) return;

    setLoading(true);

    try {
      const response = await getMenuByDate(date);
      
      // 如果没有当前日期的菜单数据，设置为null显示空状态
      if (response.fallback) {
        setMenuData(null);
      } else {
        setMenuData(response);
      }
    } catch (error) {
      console.error('获取菜单数据失败:', error);
      const errorMessage = handleApiError(error);
      
      if (isNetworkError(error)) {
        showError('网络连接失败', '无法获取菜单数据，请检查网络连接');
      } else if (isServerError(error)) {
        showError('服务器错误', '无法获取菜单数据，服务器暂时不可用');
      } else {
        showError('加载菜单失败', errorMessage);
      }
      
      setMenuData(null);
    } finally {
      setLoading(false);
    }
  };

  // 处理日期变化
  const handleDateChange = (date: string) => {
    setCurrentDate(date);
  };

  // 手动刷新菜单数据
  const handleRefreshMenus = async () => {
    try {
      setLoading(true);
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
      showError('刷新失败', errorMessage);
    } finally {
      setLoading(false);
    }
  };

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
    <div className="min-vh-100 bg-light">
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
              <i className={`bi ${loading ? 'bi-arrow-clockwise' : 'bi-arrow-clockwise'} me-1 ${loading ? 'spin' : ''}`}></i>
              刷新菜单
            </button>
          </div>
        </div>
      </nav>

      {/* 主要内容区域 */}
      <main className="container py-4">
        {/* 网络状态指示器 */}
        <NetworkStatusIndicator />

        {/* 日期选择器 */}
        {availableDates.length > 0 && (
          <div className="mb-4">
            <DateSelector
              selectedDate={currentDate}
              onDateChange={handleDateChange}
              availableDates={availableDates}
              loading={loading}
            />
          </div>
        )}

        {/* 根据是否有可用日期显示不同内容 */}
        {availableDates.length > 0 ? (
          /* 有菜单数据时显示菜单 */
          <MenuDisplay
            menuData={menuData}
            selectedDate={currentDate}
            loading={loading}
          />
        ) : (
          /* 无数据时的提示 */
          <div className="text-center py-5">
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