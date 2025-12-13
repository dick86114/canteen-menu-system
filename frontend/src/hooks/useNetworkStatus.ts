import { useState, useEffect, useCallback } from 'react';
import { checkNetworkConnection } from '../services/api';

interface NetworkStatus {
  isOnline: boolean;
  isConnected: boolean;
  lastChecked: Date | null;
  checkConnection: () => Promise<void>;
}

export const useNetworkStatus = (checkInterval: number = 30000): NetworkStatus => {
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [isConnected, setIsConnected] = useState<boolean>(true);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkConnection = useCallback(async () => {
    try {
      // 检查函数是否存在（测试环境可能没有）
      if (typeof checkNetworkConnection === 'function') {
        const connected = await checkNetworkConnection();
        setIsConnected(connected);
      } else {
        // 在测试环境中假设连接正常
        setIsConnected(true);
      }
      setLastChecked(new Date());
    } catch (error) {
      console.warn('网络连接检查失败:', error);
      setIsConnected(false);
      setLastChecked(new Date());
    }
  }, []);

  useEffect(() => {
    // 监听浏览器在线状态变化
    const handleOnline = () => {
      setIsOnline(true);
      checkConnection(); // 重新检查服务器连接
    };

    const handleOffline = () => {
      setIsOnline(false);
      setIsConnected(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // 初始检查
    checkConnection();

    // 定期检查服务器连接
    const interval = setInterval(checkConnection, checkInterval);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
    };
  }, [checkConnection, checkInterval]);

  return {
    isOnline,
    isConnected,
    lastChecked,
    checkConnection,
  };
};