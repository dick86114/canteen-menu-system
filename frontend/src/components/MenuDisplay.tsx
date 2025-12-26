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

  // 获取菜品图标
  const getFoodIcon = (foodName: string, category: string): string => {
    // 根据菜品名称和分类返回合适的图标
    const name = foodName.toLowerCase();
    const cat = category?.toLowerCase() || '';
    
    // 档口特色
    if (category === '档口特色') return '🌟';
    
    // 根据菜品名称匹配图标
    if (name.includes('鸡') || name.includes('鸭') || name.includes('鹅')) return '🐔';
    if (name.includes('猪') || name.includes('肉') || name.includes('排骨')) return '🥩';
    if (name.includes('牛')) return '🐄';
    if (name.includes('鱼') || name.includes('虾') || name.includes('蟹') || name.includes('扇贝')) return '🐟';
    if (name.includes('蛋')) return '🥚';
    if (name.includes('豆腐') || name.includes('豆')) return '🫘';
    if (name.includes('面') || name.includes('粉') || name.includes('饺子')) return '🍜';
    if (name.includes('饭') || name.includes('粥')) return '🍚';
    if (name.includes('汤')) return '🍲';
    if (name.includes('青菜') || name.includes('白菜') || name.includes('菠菜')) return '🥬';
    if (name.includes('萝卜') || name.includes('胡萝卜')) return '🥕';
    if (name.includes('土豆') || name.includes('马铃薯')) return '🥔';
    if (name.includes('茄子')) return '🍆';
    if (name.includes('番茄') || name.includes('西红柿')) return '🍅';
    if (name.includes('玉米')) return '🌽';
    if (name.includes('蘑菇') || name.includes('菌')) return '🍄';
    if (name.includes('辣椒')) return '🌶️';
    if (name.includes('包子') || name.includes('馒头')) return '🥟';
    if (name.includes('饼') || name.includes('烧饼')) return '🫓';
    if (name.includes('粽子')) return '🫔';
    if (name.includes('水果') || name.includes('苹果')) return '🍎';
    if (name.includes('香蕉')) return '🍌';
    if (name.includes('橙') || name.includes('柑')) return '🍊';
    if (name.includes('牛奶') || name.includes('酸奶')) return '🥛';
    if (name.includes('咖啡')) return '☕';
    if (name.includes('茶')) return '🍵';
    
    // 根据分类匹配图标
    if (cat.includes('汤') || cat.includes('例汤')) return '🍲';
    if (cat.includes('主食') || cat.includes('面点')) return '🍚';
    if (cat.includes('蔬菜') || cat.includes('时蔬')) return '🥬';
    if (cat.includes('荤') || cat.includes('肉')) return '🥩';
    if (cat.includes('饮品') || cat.includes('奶')) return '🥛';
    if (cat.includes('包点')) return '🥟';
    if (cat.includes('水果')) return '🍎';
    if (cat.includes('炖罐')) return '🫖';
    
    // 默认图标
    return '🍽️';
  };
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

  // 检查是否有档口特色菜品
  const hasSpecialtyDishes = (menuData: MenuData | null): boolean => {
    if (!menuData || !menuData.meals) return false;
    
    return menuData.meals.some(meal => 
      meal.items.some(item => item.category === '档口特色')
    );
  };

  // 获取所有档口特色菜品
  const getSpecialtyDishes = (menuData: MenuData | null): MenuItem[] => {
    if (!menuData || !menuData.meals) return [];
    
    const specialtyItems: MenuItem[] = [];
    menuData.meals.forEach(meal => {
      meal.items.forEach(item => {
        if (item.category === '档口特色') {
          specialtyItems.push(item);
        }
      });
    });
    
    return specialtyItems;
  };

  // 渲染菜品项目
  const renderMenuItem = (item: MenuItem, index: number) => (
    <div key={index} className="food-item">
      <div className="food-item-content">
        <div className="food-item-main">
          <span className="food-icon">{getFoodIcon(item.name, item.category || '')}</span>
          <div className="food-info">
            <span className="food-name">{item.name}</span>
            {item.description && (
              <small className="food-description">{item.description}</small>
            )}
          </div>
        </div>
        {item.price && (
          <span className="food-price">¥{item.price.toFixed(2)}</span>
        )}
      </div>
    </div>
  );

  // 渲染分类区块
  const renderCategorySection = (category: string, items: MenuItem[]) => {
    const isSpecialty = category === '档口特色';
    
    return (
      <div key={category} className={`food-category ${isSpecialty ? 'specialty-category' : ''}`}>
        <div className={`category-title ${isSpecialty ? 'specialty-title' : ''}`}>
          {isSpecialty && <i className="bi bi-star-fill me-2"></i>}
          {category}
          {isSpecialty && <i className="bi bi-star-fill ms-2"></i>}
        </div>
        <div className="food-items">
          {items.map((item, index) => renderMenuItem(item, index))}
        </div>
      </div>
    );
  };

  // 渲染档口特色横幅
  const renderSpecialtyBanner = () => {
    const specialtyItems = getSpecialtyDishes(menuData);
    
    if (specialtyItems.length === 0) return null;

    return (
      <div className="specialty-banner">
        <div className="specialty-banner-content">
          <div className="specialty-banner-header">
            <i className="bi bi-star-fill"></i>
            <h3>今日大菜推荐</h3>
            <i className="bi bi-star-fill"></i>
          </div>
          <div className="specialty-banner-subtitle">
            档口特色菜品 · 限量供应 · 不容错过
          </div>
          <div className="specialty-dishes-list">
            {specialtyItems.map((item, index) => (
              <div key={index} className="specialty-dish-item">
                <i className="bi bi-gem me-2"></i>
                <span>{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // 渲染餐次卡片
  const renderMenuCard = (meal: Meal, index: number) => {
    const groupedItems = groupItemsByCategory(meal.items);
    
    // 将档口特色排在最前面，其他分类按原顺序排列
    const categories = Object.keys(groupedItems).sort((a, b) => {
      if (a === '档口特色') return -1;
      if (b === '档口特色') return 1;
      return 0;
    });

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
  const hasSpecialty = hasSpecialtyDishes(menuData);

  return (
    <div className="menu-display">
      {/* 档口特色横幅 */}
      {hasSpecialty && renderSpecialtyBanner()}

      {/* 日期标题 */}
      <div className="menu-date-header">
        <h2>{formatDate(selectedDate)}</h2>
        <div className="subtitle">
          <i className="bi bi-calendar-event"></i>
          今日菜单 · 共 {sortedMeals.length} 个餐次 · {sortedMeals.reduce((total, meal) => total + meal.items.length, 0)} 道菜品
          {hasSpecialty && (
            <>
              <i className="bi bi-star-fill text-warning ms-2"></i>
              <span className="text-warning fw-bold">含特色大菜</span>
            </>
          )}
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