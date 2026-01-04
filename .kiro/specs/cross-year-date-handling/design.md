# 跨年日期处理设计文档

## 概述

本文档描述了食堂菜单系统跨年日期处理的技术设计方案。主要目标是实现智能的年份推断机制，确保12月菜单正确识别为上一年，1月菜单正确识别为当前年，提供无缝的跨年用户体验。

## 当前问题分析

### 问题根因

**当前实现问题：**
```python
# backend/app/services/excel_parser.py
from ..utils.timezone import current_year
current_year_val = current_year()  # 总是返回2026

# 所有月份都使用相同年份
date_obj = datetime(current_year_val, month, day)  # 12月也变成2026年
```

**具体影响：**
1. 12月菜单被错误标记为2026年12月
2. 用户看到未来的菜单日期
3. 日期导航和搜索功能混乱
4. 月历显示错误的日期标记

### 现有文件分析

**当前menu目录文件：**
```
menu/省投食堂菜单；12月8-12.et     -> 应该是2025-12-08到2025-12-12
menu/省投食堂菜单；12月15-19.et    -> 应该是2025-12-15到2025-12-19  
menu/省投食堂菜单；12月22-26.et    -> 应该是2025-12-22到2025-12-26
menu/省投食堂菜单；12月29-31.et    -> 应该是2025-12-29到2025-12-31
menu/省投食堂菜单：1月4日-9日.xlsx  -> 应该是2026-01-04到2026-01-09
```

## 技术设计方案

### 1. 智能年份推断算法

**核心策略：基于月份和当前时间的智能推断**

```python
def infer_year_for_month(month: int, current_date: datetime = None) -> int:
    """
    根据月份和当前时间智能推断年份
    
    策略：
    - 当前时间1-6月：12月文件 = 上一年，1-6月文件 = 当前年
    - 当前时间7-12月：1-6月文件 = 下一年，7-12月文件 = 当前年
    
    Args:
        month: 目标月份 (1-12)
        current_date: 当前日期，默认使用系统当前时间
        
    Returns:
        推断的年份
    """
    if current_date is None:
        from ..utils.timezone import now
        current_date = now()
    
    current_month = current_date.month
    current_year = current_date.year
    
    # 策略1：基于时间窗口的推断
    if current_month <= 6:  # 当前是上半年
        if month >= 7:  # 目标是下半年 -> 上一年
            return current_year - 1
        else:  # 目标是上半年 -> 当前年
            return current_year
    else:  # 当前是下半年
        if month <= 6:  # 目标是上半年 -> 下一年
            return current_year + 1
        else:  # 目标是下半年 -> 当前年
            return current_year
```

**增强策略：考虑月份距离**

```python
def infer_year_with_distance(month: int, current_date: datetime = None) -> int:
    """
    基于月份距离的年份推断（更精确的策略）
    
    策略：选择距离当前时间最近的年份
    """
    if current_date is None:
        from ..utils.timezone import now
        current_date = now()
    
    current_year = current_date.year
    current_month = current_date.month
    
    # 计算三个可能年份的距离
    candidates = [
        (current_year - 1, abs((current_year - 1) * 12 + month - current_year * 12 - current_month)),
        (current_year, abs(current_year * 12 + month - current_year * 12 - current_month)),
        (current_year + 1, abs((current_year + 1) * 12 + month - current_year * 12 - current_month))
    ]
    
    # 选择距离最小的年份，但排除超过6个月的未来日期
    valid_candidates = []
    for year, distance in candidates:
        if year * 12 + month <= current_year * 12 + current_month + 6:  # 不超过6个月的未来
            valid_candidates.append((year, distance))
    
    if valid_candidates:
        return min(valid_candidates, key=lambda x: x[1])[0]
    else:
        return current_year  # 回退到当前年份
```

### 2. 文件名解析增强

**当前实现问题：**
```python
# 当前只提取月日，年份统一使用current_year
match = re.search(r'(\d{1,2})月(\d{1,2})', filename)
if match:
    month = int(match.group(1))
    day = int(match.group(2))
    # 问题：年份总是使用current_year
    date_obj = datetime(current_year_val, month, day)
```

**改进方案：**
```python
class EnhancedDateExtractor:
    """增强的日期提取器，支持智能年份推断"""
    
    def __init__(self):
        self.year_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})',     # 2025年12月8日
            r'(\d{4})-(\d{1,2})-(\d{1,2})',      # 2025-12-8
            r'(\d{4})/(\d{1,2})/(\d{1,2})',      # 2025/12/8
        ]
        
        self.month_day_patterns = [
            r'(\d{1,2})月(\d{1,2})日?',           # 12月8日
            r'(\d{1,2})-(\d{1,2})',              # 12-8
            r'(\d{1,2})/(\d{1,2})',              # 12/8
        ]
    
    def extract_dates_from_filename(self, filename: str) -> List[date]:
        """从文件名提取日期，支持智能年份推断"""
        
        # 1. 尝试提取完整日期（包含年份）
        for pattern in self.year_patterns:
            matches = re.findall(pattern, filename)
            if matches:
                dates = []
                for match in matches:
                    try:
                        year, month, day = map(int, match)
                        dates.append(date(year, month, day))
                    except ValueError:
                        continue
                if dates:
                    return dates
        
        # 2. 提取月日，智能推断年份
        for pattern in self.month_day_patterns:
            matches = re.findall(pattern, filename)
            if matches:
                dates = []
                for match in matches:
                    try:
                        month, day = map(int, match)
                        # 智能推断年份
                        year = infer_year_for_month(month)
                        dates.append(date(year, month, day))
                    except ValueError:
                        continue
                if dates:
                    return dates
        
        # 3. 处理日期范围（如：12月8-12）
        range_pattern = r'(\d{1,2})月(\d{1,2})[日-]?[至到-]?(\d{1,2})日?'
        match = re.search(range_pattern, filename)
        if match:
            month = int(match.group(1))
            start_day = int(match.group(2))
            end_day = int(match.group(3))
            
            year = infer_year_for_month(month)
            dates = []
            
            try:
                for day in range(start_day, end_day + 1):
                    dates.append(date(year, month, day))
                return dates
            except ValueError:
                pass
        
        return []
```

### 3. 跨年日期范围处理

**特殊情况：跨年日期范围**
```python
def handle_cross_year_range(start_month: int, start_day: int, 
                           end_month: int, end_day: int) -> List[date]:
    """
    处理跨年的日期范围，如：12月29日-1月2日
    """
    dates = []
    
    # 推断起始年份
    start_year = infer_year_for_month(start_month)
    
    if start_month > end_month:  # 跨年情况
        # 12月29-31日
        for day in range(start_day, 32):  # 12月最多31天
            try:
                dates.append(date(start_year, start_month, day))
            except ValueError:
                break
        
        # 1月1日-end_day日
        end_year = start_year + 1
        for day in range(1, end_day + 1):
            try:
                dates.append(date(end_year, end_month, day))
            except ValueError:
                break
    else:
        # 同年情况
        year = start_year
        for month in range(start_month, end_month + 1):
            if month == start_month:
                start = start_day
            else:
                start = 1
            
            if month == end_month:
                end = end_day
            else:
                end = 31  # 会被ValueError限制
            
            for day in range(start, end + 1):
                try:
                    dates.append(date(year, month, day))
                except ValueError:
                    break
    
    return dates
```

### 4. 数据存储和检索优化

**存储结构优化：**
```python
class CrossYearMenuStorage:
    """支持跨年的菜单存储"""
    
    def __init__(self):
        # 按年份分组存储
        self.menu_data_by_year: Dict[int, Dict[str, List[Meal]]] = {}
        self.date_index: Dict[str, int] = {}  # 日期到年份的索引
    
    def store_menu_data(self, date_str: str, meals: List[Meal]) -> None:
        """存储菜单数据，自动按年份分组"""
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        year = date_obj.year
        
        if year not in self.menu_data_by_year:
            self.menu_data_by_year[year] = {}
        
        self.menu_data_by_year[year][date_str] = meals
        self.date_index[date_str] = year
    
    def get_menu_by_date(self, date_str: str) -> Optional[List[Meal]]:
        """获取指定日期的菜单"""
        if date_str in self.date_index:
            year = self.date_index[date_str]
            return self.menu_data_by_year[year].get(date_str)
        return None
    
    def get_available_dates_in_range(self, start_date: str, end_date: str) -> List[str]:
        """获取日期范围内的可用日期（支持跨年）"""
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        available_dates = []
        for date_str in self.date_index:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            if start <= date_obj <= end:
                available_dates.append(date_str)
        
        return sorted(available_dates)
```

### 5. 前端日期导航优化

**跨年月历组件：**
```typescript
interface CrossYearCalendarProps {
  selectedDate: Date;
  availableDates: string[];
  onDateChange: (date: Date) => void;
}

const CrossYearCalendar: React.FC<CrossYearCalendarProps> = ({
  selectedDate,
  availableDates,
  onDateChange
}) => {
  const [currentViewDate, setCurrentViewDate] = useState(selectedDate);
  
  // 处理跨年导航
  const handleMonthNavigation = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentViewDate);
    
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    
    setCurrentViewDate(newDate);
  };
  
  // 检查日期是否有菜单数据
  const hasMenuData = (date: Date): boolean => {
    const dateStr = formatDateString(date);
    return availableDates.includes(dateStr);
  };
  
  // 修复的日期格式化函数（避免时区偏移）
  const formatDateString = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };
  
  return (
    <div className="cross-year-calendar">
      <div className="calendar-header">
        <button onClick={() => handleMonthNavigation('prev')}>
          ← 上个月
        </button>
        <h3>
          {currentViewDate.getFullYear()}年{currentViewDate.getMonth() + 1}月
        </h3>
        <button onClick={() => handleMonthNavigation('next')}>
          下个月 →
        </button>
      </div>
      
      <div className="calendar-grid">
        {/* 渲染日历网格，支持跨年高亮 */}
        {renderCalendarDays(currentViewDate, hasMenuData, onDateChange)}
      </div>
    </div>
  );
};
```

### 6. API接口增强

**跨年日期查询API：**
```python
@menu_bp.route('/api/menu/range', methods=['GET'])
def get_menu_range():
    """获取日期范围内的菜单数据（支持跨年）"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': '需要提供start_date和end_date参数'}), 400
    
    try:
        # 验证日期格式
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
        
        storage = get_storage()
        available_dates = storage.get_available_dates_in_range(start_date, end_date)
        
        menu_data = {}
        for date_str in available_dates:
            meals = storage.get_menu_by_date(date_str)
            if meals:
                menu_data[date_str] = [meal.to_dict() for meal in meals]
        
        return jsonify({
            'start_date': start_date,
            'end_date': end_date,
            'menu_data': menu_data,
            'total_days': len(available_dates)
        })
        
    except ValueError as e:
        return jsonify({'error': f'日期格式错误: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"获取菜单范围数据时出错: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500
```

## 测试策略

### 单元测试

**年份推断测试：**
```python
class TestYearInference(unittest.TestCase):
    
    def test_infer_year_january_context(self):
        """测试1月份上下文的年份推断"""
        # 当前时间：2026年1月
        current_date = datetime(2026, 1, 15)
        
        # 12月应该是2025年
        self.assertEqual(infer_year_for_month(12, current_date), 2025)
        
        # 1月应该是2026年
        self.assertEqual(infer_year_for_month(1, current_date), 2026)
    
    def test_infer_year_december_context(self):
        """测试12月份上下文的年份推断"""
        # 当前时间：2025年12月
        current_date = datetime(2025, 12, 15)
        
        # 12月应该是2025年
        self.assertEqual(infer_year_for_month(12, current_date), 2025)
        
        # 1月应该是2026年
        self.assertEqual(infer_year_for_month(1, current_date), 2026)
    
    def test_cross_year_boundary(self):
        """测试跨年边界情况"""
        # 12月31日
        current_date = datetime(2025, 12, 31)
        self.assertEqual(infer_year_for_month(1, current_date), 2026)
        
        # 1月1日
        current_date = datetime(2026, 1, 1)
        self.assertEqual(infer_year_for_month(12, current_date), 2025)
```

**文件名解析测试：**
```python
class TestCrossYearFilenameExtraction(unittest.TestCase):
    
    def test_extract_december_dates(self):
        """测试12月文件名解析"""
        extractor = EnhancedDateExtractor()
        
        # 模拟当前时间为2026年1月
        with patch('app.services.excel_parser.now') as mock_now:
            mock_now.return_value = datetime(2026, 1, 15)
            
            dates = extractor.extract_dates_from_filename('省投食堂菜单；12月8-12.et')
            
            expected_dates = [
                date(2025, 12, 8),
                date(2025, 12, 9),
                date(2025, 12, 10),
                date(2025, 12, 11),
                date(2025, 12, 12)
            ]
            
            self.assertEqual(dates, expected_dates)
    
    def test_extract_january_dates(self):
        """测试1月文件名解析"""
        extractor = EnhancedDateExtractor()
        
        with patch('app.services.excel_parser.now') as mock_now:
            mock_now.return_value = datetime(2026, 1, 15)
            
            dates = extractor.extract_dates_from_filename('省投食堂菜单：1月4日-9日.xlsx')
            
            expected_dates = [
                date(2026, 1, 4),
                date(2026, 1, 5),
                date(2026, 1, 6),
                date(2026, 1, 7),
                date(2026, 1, 8),
                date(2026, 1, 9)
            ]
            
            self.assertEqual(dates, expected_dates)
```

### 集成测试

**跨年菜单加载测试：**
```python
class TestCrossYearMenuLoading(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        # 模拟跨年菜单文件
        self.test_files = [
            'menu/省投食堂菜单；12月29-31.et',
            'menu/省投食堂菜单：1月4日-9日.xlsx'
        ]
    
    def test_cross_year_menu_dates(self):
        """测试跨年菜单日期正确性"""
        with self.app.app_context():
            # 加载菜单数据
            scanner = FileScanner()
            result = scanner.scan_and_load_files()
            
            self.assertTrue(result['success'])
            
            # 验证12月日期
            response = self.client.get('/api/menu?date=2025-12-30')
            self.assertEqual(response.status_code, 200)
            
            # 验证1月日期
            response = self.client.get('/api/menu?date=2026-01-05')
            self.assertEqual(response.status_code, 200)
            
            # 验证日期范围查询
            response = self.client.get('/api/menu/range?start_date=2025-12-29&end_date=2026-01-09')
            self.assertEqual(response.status_code, 200)
            
            data = response.get_json()
            self.assertIn('2025-12-29', data['menu_data'])
            self.assertIn('2026-01-05', data['menu_data'])
```

## 部署和监控

### 配置管理

**年份推断配置：**
```python
# config.py
class Config:
    # 年份推断策略配置
    YEAR_INFERENCE_STRATEGY = 'distance_based'  # 'window_based' or 'distance_based'
    YEAR_INFERENCE_WINDOW_MONTHS = 6  # 时间窗口月数
    ENABLE_CROSS_YEAR_VALIDATION = True  # 启用跨年验证
    
    # 日期范围限制
    MAX_FUTURE_MONTHS = 6  # 最多支持6个月的未来日期
    MAX_PAST_MONTHS = 12   # 最多支持12个月的历史日期
```

### 监控指标

**跨年处理监控：**
```python
class CrossYearMetrics:
    """跨年处理监控指标"""
    
    def __init__(self):
        self.year_inference_count = 0
        self.cross_year_files_processed = 0
        self.date_parsing_errors = 0
        self.year_correction_count = 0
    
    def record_year_inference(self, month: int, inferred_year: int):
        """记录年份推断"""
        self.year_inference_count += 1
        logger.info(f"年份推断: 月份{month} -> 年份{inferred_year}")
    
    def record_cross_year_file(self, filename: str):
        """记录跨年文件处理"""
        self.cross_year_files_processed += 1
        logger.info(f"处理跨年文件: {filename}")
    
    def get_metrics(self) -> Dict[str, int]:
        """获取监控指标"""
        return {
            'year_inference_count': self.year_inference_count,
            'cross_year_files_processed': self.cross_year_files_processed,
            'date_parsing_errors': self.date_parsing_errors,
            'year_correction_count': self.year_correction_count
        }
```

## 风险缓解

### 数据迁移风险

**现有数据修正：**
```python
def migrate_existing_menu_data():
    """修正现有菜单数据的年份"""
    storage = get_storage()
    
    # 获取所有现有日期
    all_dates = storage.get_available_dates()
    
    corrections = []
    for date_str in all_dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # 检查是否需要年份修正
        correct_year = infer_year_for_month(date_obj.month)
        if date_obj.year != correct_year:
            correct_date_str = f"{correct_year}-{date_obj.month:02d}-{date_obj.day:02d}"
            
            # 移动数据
            meals = storage.get_menu_by_date(date_str)
            if meals:
                storage.store_menu_data(correct_date_str, meals)
                storage.remove_menu_data(date_str)
                corrections.append((date_str, correct_date_str))
    
    return corrections
```

### 回滚策略

**版本兼容性：**
```python
class BackwardCompatibleDateHandler:
    """向后兼容的日期处理器"""
    
    def __init__(self, use_legacy_mode: bool = False):
        self.use_legacy_mode = use_legacy_mode
    
    def parse_date(self, month: int, day: int) -> date:
        """解析日期，支持遗留模式"""
        if self.use_legacy_mode:
            # 使用旧的逻辑（总是当前年份）
            from ..utils.timezone import current_year
            year = current_year()
        else:
            # 使用新的智能推断
            year = infer_year_for_month(month)
        
        return date(year, month, day)
```

## 总结

跨年日期处理是一个复杂但重要的功能改进，主要包括：

1. **智能年份推断** - 基于月份和当前时间的智能算法
2. **增强文件解析** - 支持多种日期格式和跨年范围
3. **优化数据存储** - 按年份分组，提高查询效率
4. **改进用户体验** - 无缝的跨年导航和显示
5. **完整测试覆盖** - 确保各种边界情况的正确处理

通过这些改进，系统将能够正确处理跨年菜单，为用户提供准确、流畅的菜单浏览体验。