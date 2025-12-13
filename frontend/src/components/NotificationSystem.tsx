import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

// 通知类型定义
export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id'>) => string;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
  showSuccess: (title: string, message?: string, duration?: number) => string;
  showError: (title: string, message?: string, persistent?: boolean) => string;
  showWarning: (title: string, message?: string, duration?: number) => string;
  showInfo: (title: string, message?: string, duration?: number) => string;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback((notification: Omit<Notification, 'id'>) => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
    const newNotification: Notification = {
      ...notification,
      id,
      duration: notification.duration ?? 5000, // 默认5秒
    };

    setNotifications(prev => [...prev, newNotification]);

    // 自动移除通知（除非是持久化的）
    if (!newNotification.persistent && newNotification.duration && newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }

    return id;
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const showSuccess = useCallback((title: string, message?: string, duration?: number) => {
    return addNotification({ type: 'success', title, message, duration });
  }, [addNotification]);

  const showError = useCallback((title: string, message?: string, persistent?: boolean) => {
    return addNotification({ 
      type: 'error', 
      title, 
      message, 
      persistent,
      duration: persistent ? 0 : 8000 // 错误消息显示更长时间
    });
  }, [addNotification]);

  const showWarning = useCallback((title: string, message?: string, duration?: number) => {
    return addNotification({ type: 'warning', title, message, duration });
  }, [addNotification]);

  const showInfo = useCallback((title: string, message?: string, duration?: number) => {
    return addNotification({ type: 'info', title, message, duration });
  }, [addNotification]);

  const value: NotificationContextType = {
    notifications,
    addNotification,
    removeNotification,
    clearAllNotifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <NotificationContainer />
    </NotificationContext.Provider>
  );
};

// 通知容器组件
const NotificationContainer: React.FC = () => {
  const { notifications, removeNotification } = useNotifications();

  const getNotificationIcon = (type: NotificationType): string => {
    switch (type) {
      case 'success':
        return 'bi-check-circle';
      case 'error':
        return 'bi-exclamation-triangle';
      case 'warning':
        return 'bi-exclamation-circle';
      case 'info':
        return 'bi-info-circle';
      default:
        return 'bi-info-circle';
    }
  };

  const getNotificationClass = (type: NotificationType): string => {
    switch (type) {
      case 'success':
        return 'alert-success';
      case 'error':
        return 'alert-danger';
      case 'warning':
        return 'alert-warning';
      case 'info':
        return 'alert-info';
      default:
        return 'alert-info';
    }
  };

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div className="notification-container position-fixed top-0 end-0 p-3" style={{ zIndex: 1050 }}>
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`alert ${getNotificationClass(notification.type)} alert-dismissible fade show mb-2`}
          role="alert"
          style={{ minWidth: '300px', maxWidth: '400px' }}
        >
          <div className="d-flex align-items-start">
            <i className={`bi ${getNotificationIcon(notification.type)} me-2 mt-1`}></i>
            <div className="flex-grow-1">
              <div className="fw-bold">{notification.title}</div>
              {notification.message && (
                <div className="small mt-1">{notification.message}</div>
              )}
              {notification.action && (
                <div className="mt-2">
                  <button
                    className="btn btn-sm btn-outline-secondary"
                    onClick={notification.action.onClick}
                  >
                    {notification.action.label}
                  </button>
                </div>
              )}
            </div>
            <button
              type="button"
              className="btn-close"
              onClick={() => removeNotification(notification.id)}
              aria-label="关闭"
            ></button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default NotificationProvider;