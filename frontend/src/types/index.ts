// 菜单系统的类型定义

export interface MenuItem {
  name: string;
  description?: string;
  category?: string;
  price?: number;
}

export interface Meal {
  type: 'breakfast' | 'lunch' | 'dinner';
  time: string; // HH:MM 格式
  items: MenuItem[];
}

export interface MenuData {
  date: string; // ISO 日期格式 YYYY-MM-DD
  meals: Meal[];
}

export interface MenuResponse {
  date: string;
  meals: Meal[];
  fallback?: boolean;
  message?: string;
}

export interface DatesResponse {
  dates: string[];
  dateRange: {
    start: string;
    end: string;
  };
}