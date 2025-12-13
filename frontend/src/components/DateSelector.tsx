import React, { useState } from 'react';

interface DateSelectorProps {
  selectedDate: string;
  onDateChange: (date: string) => void;
  availableDates: string[];
  loading?: boolean;
}

interface CalendarViewProps {
  selectedDate: string;
  availableDates: string[];
  onDateSelect: (date: string) => void;
  onClose: () => void;
}

// 月历组件
const CalendarView: React.FC<CalendarViewProps> = ({
  selectedDate,
  availableDates,
  onDateSelect,
  onClose
}) => {
  const [currentMonth, setCurrentMonth] = useState(() => {
    // 默认显示选中日期所在的月份
    return selectedDate ? new Date(selectedDate + 'T00:00:00') : new Date();
  });

  // 获取月份的所有日期
  const getMonthDates = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    
    // 获取当月第一天
    const firstDay = new Date(year, month, 1);
    
    // 获取第一周的开始日期（周一）
    const startDate = new Date(firstDay);
    const dayOfWeek = firstDay.getDay();
    const daysToSubtract = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // 周一为0
    startDate.setDate(firstDay.getDate() - daysToSubtract);
    
    // 生成6周的日期
    const dates = [];
    const current = new Date(startDate);
    
    for (let week = 0; week < 6; week++) {
      const weekDates = [];
      for (let day = 0; day < 7; day++) {
        weekDates.push(new Date(current));
        current.setDate(current.getDate() + 1);
      }
      dates.push(weekDates);
    }
    
    return dates;
  };

  // 格式化日期为字符串
  const formatDateString = (date: Date): string => {
    return date.toISOString().split('T')[0];
  };

  // 检查日期是否有菜单
  const hasMenu = (date: Date): boolean => {
    return availableDates.includes(formatDateString(date));
  };

  // 检查是否是今天
  const isToday = (date: Date): boolean => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  // 检查是否是选中的日期
  const isSelected = (date: Date): boolean => {
    return formatDateString(date) === selectedDate;
  };

  // 检查是否是当前月份
  const isCurrentMonth = (date: Date): boolean => {
    return date.getMonth() === currentMonth.getMonth() && 
           date.getFullYear() === currentMonth.getFullYear();
  };

  // 切换到上个月
  const previousMonth = () => {
    setCurrentMonth(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
  };

  // 切换到下个月
  const nextMonth = () => {
    setCurrentMonth(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
  };

  // 处理日期点击
  const handleDateClick = (date: Date) => {
    onDateSelect(formatDateString(date));
  };

  const monthDates = getMonthDates(currentMonth);
  const monthName = currentMonth.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long' 
  });

  return (
    <div className="calendar-view">
      {/* 月份导航 */}
      <div className="calendar-header">
        <button 
          className="calendar-nav-btn"
          onClick={previousMonth}
          title="上个月"
        >
          <i className="bi bi-chevron-left"></i>
        </button>
        <h4 className="calendar-title">{monthName}</h4>
        <button 
          className="calendar-nav-btn"
          onClick={nextMonth}
          title="下个月"
        >
          <i className="bi bi-chevron-right"></i>
        </button>
      </div>

      {/* 星期标题 */}
      <div className="calendar-weekdays">
        {['一', '二', '三', '四', '五', '六', '日'].map(day => (
          <div key={day} className="calendar-weekday">{day}</div>
        ))}
      </div>

      {/* 日期网格 */}
      <div className="calendar-grid">
        {monthDates.map((week, weekIndex) => (
          <div key={weekIndex} className="calendar-week">
            {week.map((date, dayIndex) => {
              const dateStr = formatDateString(date);
              const hasMenuData = hasMenu(date);
              const isTodayDate = isToday(date);
              const isSelectedDate = isSelected(date);
              const isCurrentMonthDate = isCurrentMonth(date);

              return (
                <button
                  key={dayIndex}
                  className={`calendar-day ${
                    isSelectedDate ? 'selected' : ''
                  } ${
                    hasMenuData ? 'has-menu' : ''
                  } ${
                    isTodayDate ? 'today' : ''
                  } ${
                    !isCurrentMonthDate ? 'other-month' : ''
                  }`}
                  onClick={() => handleDateClick(date)}
                  title={`${dateStr}${hasMenuData ? ' (有菜单)' : ''}${isTodayDate ? ' (今天)' : ''}`}
                >
                  <span className="calendar-day-number">{date.getDate()}</span>
                  {hasMenuData && <span className="calendar-day-indicator">●</span>}
                </button>
              );
            })}
          </div>
        ))}
      </div>

      {/* 底部操作 */}
      <div className="calendar-footer">
        <div className="calendar-legend">
          <span className="legend-item">
            <span className="legend-dot has-menu">●</span>
            有菜单
          </span>
          <span className="legend-item">
            <span className="legend-dot today">●</span>
            今天
          </span>
        </div>
        <button className="btn btn-secondary" onClick={onClose}>
          关闭
        </button>
      </div>
    </div>
  );
};

const DateSelector: React.FC<DateSelectorProps> = ({
  selectedDate,
  onDateChange,
  availableDates,
  loading = false
}) => {
  const [showDateList, setShowDateList] = useState<boolean>(false);

  // 将字符串日期转换为 Date 对象 - 使用本地时区
  const parseDate = (dateStr: string): Date => {
    const [year, month, day] = dateStr.split('-').map(Number);
    return new Date(year, month - 1, day); // 月份从0开始
  };

  // 获取日期范围信息
  const getDateRangeInfo = () => {
    if (availableDates.length === 0) return null;
    
    const sortedDates = [...availableDates].sort();
    const startDate = parseDate(sortedDates[0]);
    const endDate = parseDate(sortedDates[sortedDates.length - 1]);
    
    return {
      start: startDate,
      end: endDate,
      count: availableDates.length
    };
  };

  // 处理日期选择
  const handleDateSelect = (dateStr: string) => {
    onDateChange(dateStr);
    setShowDateList(false);
  };

  // 格式化日期为字符串 - 使用本地时区
  const formatDate = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // 导航到前一天 - 按照常规日历逻辑
  const navigateToPrevious = () => {
    const currentDate = parseDate(selectedDate);
    const previousDate = new Date(currentDate);
    previousDate.setDate(previousDate.getDate() - 1);
    
    const previousDateStr = formatDate(previousDate);
    onDateChange(previousDateStr);
  };

  // 导航到后一天 - 按照常规日历逻辑
  const navigateToNext = () => {
    const currentDate = parseDate(selectedDate);
    const nextDate = new Date(currentDate);
    nextDate.setDate(nextDate.getDate() + 1);
    
    const nextDateStr = formatDate(nextDate);
    onDateChange(nextDateStr);
  };

  // 跳转到今天（真正的今天，不管是否有菜单）
  const navigateToToday = () => {
    const today = formatDate(new Date());
    onDateChange(today); // 直接跳转到今天，不管是否有菜单数据
  };

  // 跳转到第一天
  const navigateToFirst = () => {
    if (availableDates.length > 0) {
      const sortedDates = [...availableDates].sort();
      onDateChange(sortedDates[0]);
    }
  };

  // 跳转到最后一天
  const navigateToLast = () => {
    if (availableDates.length > 0) {
      const sortedDates = [...availableDates].sort();
      onDateChange(sortedDates[sortedDates.length - 1]);
    }
  };

  // 格式化显示日期
  const formatDisplayDate = (dateStr: string): string => {
    const date = parseDate(dateStr);
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    };
    return date.toLocaleDateString('zh-CN', options);
  };

  // 格式化简短日期
  const formatShortDate = (dateStr: string): string => {
    const date = parseDate(dateStr);
    const options: Intl.DateTimeFormatOptions = {
      month: 'short',
      day: 'numeric',
      weekday: 'short'
    };
    return date.toLocaleDateString('zh-CN', options);
  };

  // 获取当前日期在可用日期中的位置
  const getCurrentDateIndex = (): number => {
    return availableDates.indexOf(selectedDate);
  };

  // 判断是否可以导航到前一天 - 设置合理的日期边界
  const canNavigatePrevious = (): boolean => {
    const currentDate = parseDate(selectedDate);
    // 设置一个合理的最早日期边界，比如2020年1月1日
    const minDate = new Date('2020-01-01');
    return currentDate > minDate;
  };

  // 判断是否可以导航到后一天 - 设置合理的日期边界
  const canNavigateNext = (): boolean => {
    const currentDate = parseDate(selectedDate);
    // 设置一个合理的最晚日期边界，比如当前日期后1年
    const maxDate = new Date();
    maxDate.setFullYear(maxDate.getFullYear() + 1);
    return currentDate < maxDate;
  };

  const currentIndex = getCurrentDateIndex();
  const hasPrevious = canNavigatePrevious();
  const hasNext = canNavigateNext();
  const dateRangeInfo = getDateRangeInfo();

  if (loading) {
    return (
      <div className="date-selector">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>正在加载日期...</p>
        </div>
      </div>
    );
  }

  if (availableDates.length === 0) {
    return (
      <div className="date-selector">
        <div className="empty-state">
          <div className="icon">📅</div>
          <h3>暂无可用日期</h3>
          <p>请先上传菜单文件或刷新菜单数据</p>
        </div>
      </div>
    );
  }

  return (
    <div className="date-selector">
      {/* 日期导航 */}
      <div className="date-navigation">
        <button
          className="date-nav-btn"
          onClick={navigateToPrevious}
          disabled={!hasPrevious}
          title="前一天"
        >
          <i className="bi bi-chevron-left"></i>
        </button>

        <div className="current-date">
          <h3>{formatDisplayDate(selectedDate)}</h3>
          <div className="date-meta">
            {currentIndex >= 0 ? (
              `第 ${currentIndex + 1} 天 / 共 ${availableDates.length} 天`
            ) : (
              `共 ${availableDates.length} 天菜单数据`
            )}
          </div>
        </div>

        <button
          className="date-nav-btn"
          onClick={navigateToNext}
          disabled={!hasNext}
          title="后一天"
        >
          <i className="bi bi-chevron-right"></i>
        </button>
      </div>

      {/* 快捷操作 */}
      <div className="date-actions">
        <button
          className="date-quick-btn"
          onClick={navigateToFirst}
          title="第一天"
        >
          <i className="bi bi-skip-start me-1"></i>
          第一天
        </button>
        
        <button
          className="date-quick-btn"
          onClick={navigateToToday}
          title="今天或最近"
        >
          <i className="bi bi-house me-1"></i>
          今天
        </button>
        
        <button
          className="date-quick-btn"
          onClick={() => setShowDateList(!showDateList)}
          title="打开月历选择日期"
        >
          <i className="bi bi-calendar3 me-1"></i>
          月历
        </button>
        
        <button
          className="date-quick-btn"
          onClick={navigateToLast}
          title="最后一天"
        >
          <i className="bi bi-skip-end me-1"></i>
          最后一天
        </button>
      </div>

      {/* 月历选择器 */}
      {showDateList && (
        <div className="date-list-container">
          <CalendarView 
            selectedDate={selectedDate}
            availableDates={availableDates}
            onDateSelect={handleDateSelect}
            onClose={() => setShowDateList(false)}
          />
        </div>
      )}

      {/* 日期范围信息 */}
      {dateRangeInfo && (
        <div className="date-range-info">
          <i className="bi bi-info-circle me-2"></i>
          可用日期：{formatShortDate(dateRangeInfo.start.toISOString().split('T')[0])} 至 {formatShortDate(dateRangeInfo.end.toISOString().split('T')[0])} 
          （共 {dateRangeInfo.count} 天）
        </div>
      )}
    </div>
  );
};

export default DateSelector;