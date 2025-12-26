import React from 'react';
import { MenuData, Meal, MenuItem } from '../types';

interface MenuDisplayProps {
  menuData: MenuData | null;
  selectedDate: string;
  loading?: boolean;
}

const MenuDisplay: React.FC<MenuDisplayProps> = ({ 
  menuData, 
  selectedDate, 
  loading = false 
}) => {
  // 格式化餐次时间显示
  const formatMealTime = (time: string): string => {
    return time;
  };

  // 获取餐次的中文名称
  const getMealTypeName = (type: string): string => {
    const mealNames = {
      breakfast: '早餐',
      lunch: '午餐',
      dinner: '晚餐'
    };
    return mealNames[type as keyof typeof mealNames] || type;
  };

  // 按餐次类型分组
  const groupByMealType = (meals: Meal[]): Meal[] => {
    const mealOrder = ['breakfast', 'lunch', 'dinner'];
    return meals.sort((a, b) => {
      const aIndex = mealOrder.indexOf(a.type);
      const bIndex = mealOrder.indexOf(b.type);
      if (aIndex !== bIndex) {
        return aIndex - bIndex;
      }
      // 如果餐次类型相同，按时间排序
      return a.time.localeCompare(b.time);
    });
  };

  // 按分类分组菜品
  const groupItemsByCategory = (items: MenuItem[]): { [category: string]: MenuItem[] } => {
    const grouped: { [category: string]: MenuItem[] } = {};
    
    items.forEach(item => {
      const category = item.category && item.category !== '<NA>' ? item.category : '其他';
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(item);
    });
    
    return grouped;
  };

  // 渲染菜品项目
  const renderMenuItem = (item: MenuItem, index: number) => (
    <div key={index} className="food-item">
      <div className="d-flex justify-content-between align-items-center">
        <span className="fw-medium">{item.name}</span>
        {item.price && (
          <span className="fw-bold text-primary">¥{item.price.toFixed(2)}</span>
        )}
      </div>
      {item.description && (
        <small className="text-muted">{item.description}</small>
      )}
    </div>
  );

  // 渲染分类区块
  const renderCategorySection = (category: string, items: MenuItem[]) => (
    <div key={category} className="food-category">
      <div className="category-title">{category}</div>
      <div className="food-items">
        {items.map((item, index) => renderMenuItem(item, index))}
      </div>
    </div>
  );

  // 渲染餐次卡片
  const renderMenuCard = (meal: Meal, index: number) => {
    const groupedItems = groupItemsByCategory(meal.items);
    const categories = Object.keys(groupedItems).sort();

    return (
      <div key={index} className="meal-card">
        <div className="meal-header">
          <h3 className="meal-title">{getMealTypeName(meal.type)}</h3>
          <div className="meal-time">{formatMealTime(meal.time)}</div>
        </div>
        
        <div className="meal-content">
          {meal.items.length > 0 ? (
            <div className="food-categories">
              {categories.map(category => 
                renderCategorySection(category, groupedItems[category])
              )}
            </div>
          ) : (
            <div className="empty-state">
              <div className="icon">🍽️</div>
              <h3>暂无菜品信息</h3>
              <p>该餐次暂时没有菜品数据</p>
            </div>
          )}
        </div>
        
        <div className="meal-stats">
          <span>
            <i className="bi bi-list-ul me-1"></i>
            共 {meal.items.length} 道菜品
          </span>
          <span>
            <i className="bi bi-grid me-1"></i>
            {categories.length} 个分类
          </span>
        </div>
      </div>
    );
  };

  // 格式化日期显示
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    };
    return date.toLocaleDateString('zh-CN', options);
  };

  // 加载状态
  if (loading) {
    return (
      <div className="menu-display">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>正在加载菜单数据...</p>
        </div>
      </div>
    );
  }

  // 无菜单数据状态
  if (!menuData || !menuData.meals || menuData.meals.length === 0) {
    // 使用本地时区格式化今天的日期，避免UTC转换问题
    const today = new Date();
    const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    const isToday = selectedDate === todayStr;
    
    return (
      <div className="menu-display">
        <div className="empty-state">
          <div className="icon">{isToday ? '🍽️' : '📋'}</div>
          <h3>{isToday ? '今天暂无菜单' : '暂无菜单数据'}</h3>
          <p className="text-muted">
            {formatDate(selectedDate)} 暂无菜单信息
          </p>
        </div>
      </div>
    );
  }

  const sortedMeals = groupByMealType(menuData.meals);

  return (
    <div className="menu-display">
      {/* 日期标题 */}
      <div className="menu-date-header">
        <h2>{formatDate(selectedDate)}</h2>
        <div className="subtitle">
          <i className="bi bi-calendar-event"></i>
          今日菜单 · 共 {sortedMeals.length} 个餐次 · {sortedMeals.reduce((total, meal) => total + meal.items.length, 0)} 道菜品
        </div>
      </div>

      {/* 菜单卡片 */}
      <div className="meals-container">
        {sortedMeals.map((meal, index) => renderMenuCard(meal, index))}
      </div>
    </div>
  );
};

export default MenuDisplay;