import axios, { AxiosError } from 'axios';
import { UploadResponse, MenuResponse, DatesResponse } from '../types';

// API 基础配置
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'http://localhost:5000/api'  // 生产环境使用绝对URL
  : '/api';  // 开发环境使用相对路径，利用Vite代理

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30秒超时
});

// 重试配置
interface RetryConfig {
  retries: number;
  retryDelay: number;
  retryCondition?: (error: AxiosError) => boolean;
}

const defaultRetryConfig: RetryConfig = {
  retries: 3,
  retryDelay: 1000, // 1秒
  retryCondition: (error: AxiosError) => {
    // 只对网络错误和5xx服务器错误重试
    return !error.response || (error.response.status >= 500);
  }
};

// 带重试机制的请求函数
const requestWithRetry = async <T>(
  requestFn: () => Promise<T>,
  config: RetryConfig = defaultRetryConfig
): Promise<T> => {
  let lastError: AxiosError;
  
  for (let attempt = 0; attempt <= config.retries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error as AxiosError;
      
      // 如果是最后一次尝试，或者不满足重试条件，直接抛出错误
      if (attempt === config.retries || !config.retryCondition?.(lastError)) {
        throw lastError;
      }
      
      // 等待后重试
      await new Promise(resolve => setTimeout(resolve, config.retryDelay * (attempt + 1)));
    }
  }
  
  throw lastError!;
};

// 请求拦截器 - 添加请求日志
api.interceptors.request.use(
  (config) => {
    console.log(`API请求: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器 - 统一错误处理和日志
api.interceptors.response.use(
  (response) => {
    console.log(`API响应: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('API响应错误:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// 文件上传 API - 带重试和进度回调
export const uploadMenuFile = async (
  file: File,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  return requestWithRetry(async () => {
    const response = await api.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  }, {
    retries: 2, // 文件上传重试次数较少
    retryDelay: 2000,
    retryCondition: (error: AxiosError) => {
      // 文件上传只对网络错误重试，不对4xx错误重试
      return !error.response || error.response.status >= 500;
    }
  });
};

// 获取指定日期的菜单 - 带重试
export const getMenuByDate = async (date: string): Promise<MenuResponse> => {
  return requestWithRetry(async () => {
    const response = await api.get<MenuResponse>(`/menu?date=${date}`);
    return response.data;
  });
};

// 获取可用日期列表 - 带重试
export const getAvailableDates = async (): Promise<DatesResponse> => {
  return requestWithRetry(async () => {
    const response = await api.get<DatesResponse>('/dates');
    return response.data;
  });
};

// 自动扫描并加载菜单文件 - 新增
export const autoLoadMenuFiles = async (): Promise<{
  success: boolean;
  message: string;
  loaded_files: any[];
  failed_files: any[];
  total_menus: number;
}> => {
  return requestWithRetry(async () => {
    const response = await api.get('/scanner/auto-load');
    return response.data;
  });
};

// 手动扫描菜单文件 - 新增
export const scanMenuFiles = async (): Promise<{
  success: boolean;
  message: string;
  loaded_files: any[];
  failed_files: any[];
  total_menus: number;
}> => {
  return requestWithRetry(async () => {
    const response = await api.post('/scanner/scan');
    return response.data;
  });
};

// 清除缓存 - 新增
export const clearMenuCache = async (): Promise<{
  success: boolean;
  message: string;
}> => {
  return requestWithRetry(async () => {
    const response = await api.post('/scanner/clear-cache');
    return response.data;
  });
};

// 刷新菜单（清除缓存并重新扫描）- 新增
export const refreshMenus = async (): Promise<{
  success: boolean;
  message: string;
  loaded_files: any[];
  failed_files: any[];
  total_menus: number;
}> => {
  return requestWithRetry(async () => {
    const response = await api.post('/scanner/refresh');
    return response.data;
  });
};

// 获取扫描状态 - 新增
export const getScanStatus = async (): Promise<{
  menu_directory: string;
  directory_exists: boolean;
  excel_files_count: number;
  excel_files: string[];
  loaded_menus_count: number;
  available_dates: string[];
}> => {
  return requestWithRetry(async () => {
    const response = await api.get('/scanner/status');
    return response.data;
  });
};

// 网络连接检查
export const checkNetworkConnection = async (): Promise<boolean> => {
  try {
    await pingServer();
    return true;
  } catch (error) {
    return false;
  }
};

// 健康检查
export const healthCheck = async (): Promise<{ status: string; timestamp: string }> => {
  try {
    const response = await api.get('/health', { timeout: 5000 });
    return response.data;
  } catch (error) {
    throw new Error('服务器健康检查失败');
  }
};

// 简单的ping检查
export const pingServer = async (): Promise<{ message: string; timestamp: string }> => {
  try {
    const response = await api.get('/ping', { timeout: 3000 });
    return response.data;
  } catch (error) {
    throw new Error('服务器ping失败');
  }
};

// 增强的错误处理工具函数
export const handleApiError = (error: any): string => {
  if (error.response) {
    // 服务器返回错误状态码
    const status = error.response.status;
    const message = error.response.data?.message;
    
    switch (status) {
      case 400:
        return message || '请求参数错误';
      case 401:
        return '未授权访问';
      case 403:
        return '访问被禁止';
      case 404:
        return '请求的资源不存在';
      case 413:
        return message || '文件大小超出限制';
      case 422:
        return message || '文件格式或内容错误';
      case 429:
        return '请求过于频繁，请稍后重试';
      case 500:
        return '服务器内部错误';
      case 502:
        return '网关错误';
      case 503:
        return '服务暂时不可用';
      case 504:
        return '请求超时';
      default:
        return message || `服务器错误 (${status})`;
    }
  } else if (error.request) {
    // 请求发送但没有收到响应
    if (error.code === 'ECONNABORTED') {
      return '请求超时，请检查网络连接';
    } else if (error.code === 'NETWORK_ERROR') {
      return '网络连接失败，请检查网络设置';
    } else {
      return '网络连接失败，请检查网络连接或稍后重试';
    }
  } else {
    // 其他错误
    return error.message || '未知错误，请稍后重试';
  }
};

// 错误类型判断工具函数
export const isNetworkError = (error: any): boolean => {
  return !error.response && error.request;
};

export const isServerError = (error: any): boolean => {
  return error.response && error.response.status >= 500;
};

export const isClientError = (error: any): boolean => {
  return error.response && error.response.status >= 400 && error.response.status < 500;
};