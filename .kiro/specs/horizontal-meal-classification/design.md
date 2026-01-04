# 横向格式菜单餐次分类设计文档

## 概述

本文档描述了修复横向格式菜单餐次分类问题的技术设计方案。当前系统在解析横向格式（星期格式）Excel文件时只能识别单一餐次，需要实现智能的多餐次识别算法，确保1月菜单能够正确显示早餐、午餐、晚餐分类。

## 当前问题分析

### 问题根因

**当前横向格式解析器的限制：**
```python
# backend/app/services/excel_parser.py - _parse_horizontal_weekly_format方法
# 问题：只查找一个餐次标识
meal_type = 'lunch'  # default
for row_idx in range(max(0, weekday_row_idx - 2), weekday_row_idx):
    for col_idx in range(len(df.columns)):
        cell_value = str(df.iloc[row_idx, col_idx]).strip()
        if cell_value in ['早餐', 'breakfast']:
            meal_type = 'breakfast'  # 只设置一次，不支持多餐次
        # ...

# 结果：所有菜品都使用同一个meal_type
meal = Meal(
    type=meal_type,  # 所有菜品都是同一餐次
    time=meal_times.get(meal_type, '12:00'),
    items=items
)
```

**具体影响：**
1. 1月菜单所有菜品都显示为同一餐次（通常是午餐）
2. 用户无法区分早餐、午餐、晚餐
3. 菜单显示缺乏时间结构，用户体验差

### 横向格式特点分析

**典型横向格式结构：**
```
行1: 标题（如：食堂菜单（1月4-9日））
行2: 可能的餐次标识（如：早餐）
行3: 星期标题行（星期一、星期二...）
行4: 分类1（如：粥品类）
行5: 菜品1
行6: 菜品2
行7: 空行或"类别"行 ← 餐次分隔符
行8: 分类2（如：荤菜类）
行9: 菜品3
...
```

## 技术设计方案

### 1. 多餐次识别算法

**核心策略：基于分隔符和内容特征的智能识别**

```python
class MealSegmentIdentifier:
    """餐次分段识别器"""
    
    def __init__(self):
        # 餐次分隔符模式
        self.meal_separators = [
            '类别',           # 最常见的分隔符
            '早餐', '午餐', '晚餐',  # 明确的餐次标识
            '',               # 空行分隔
        ]
        
        # 餐次特征分类
        self.meal_indicators = {
            'breakfast': {
                'categories': ['粥品', '包点', '豆浆', '油条', '煎蛋', '早点'],
                'keywords': ['粥', '包', '豆浆', '油条', '蛋', '饼']
            },
            'lunch': {
                'categories': ['荤菜', '素菜', '汤品', '主食', '米饭'],
                'keywords': ['肉', '鱼', '鸡', '猪', '牛', '菜', '汤']
            },
            'dinner': {
                'categories': ['清淡', '小菜', '汤品', '粥品'],
                'keywords': ['清', '淡', '小菜', '汤', '粥']
            }
        }
    
    def identify_meal_segments(self, df: pd.DataFrame, weekday_row_idx: int) -> List[MealSegment]:
        """
        识别餐次分段
        
        Returns:
            List[MealSegment]: 餐次分段列表
        """
        segments = []
        current_segment_start = weekday_row_idx + 1
        current_meal_type = None
        
        for row_idx in range(weekday_row_idx + 1, len(df)):
            first_col_value = str(df.iloc[row_idx, 0]).strip()
            
            # 检查是否是餐次分隔符
            if self._is_meal_separator(first_col_value, row_idx, df):
                # 结束当前分段
                if current_segment_start < row_idx:
                    segment = MealSegment(
                        start_row=current_segment_start,
                        end_row=row_idx - 1,
                        meal_type=current_meal_type or self._infer_meal_type_from_content(
                            df, current_segment_start, row_idx - 1
                        )
                    )
                    segments.append(segment)
                
                # 开始新分段
                current_segment_start = row_idx + 1
                current_meal_type = self._extract_meal_type_from_separator(first_col_value)
        
        # 处理最后一个分段
        if current_segment_start < len(df):
            segment = MealSegment(
                start_row=current_segment_start,
                end_row=len(df) - 1,
                meal_type=current_meal_type or self._infer_meal_type_from_content(
                    df, current_segment_start, len(df) - 1
                )
            )
            segments.append(segment)
        
        return self._validate_and_adjust_segments(segments)
    
    def _is_meal_separator(self, cell_value: str, row_idx: int, df: pd.DataFrame) -> bool:
        """判断是否是餐次分隔符"""
        # 明确的餐次标识
        if cell_value in ['早餐', '午餐', '晚餐', 'breakfast', 'lunch', 'dinner']:
            return True
        
        # "类别"行
        if cell_value == '类别':
            return True
        
        # 空行（整行都为空）
        if not cell_value or cell_value == 'nan':
            row_data = df.iloc[row_idx].astype(str)
            if all(pd.isna(val) or str(val).strip() in ['', 'nan'] for val in row_data):
                return True
        
        return False
    
    def _infer_meal_type_from_content(self, df: pd.DataFrame, start_row: int, end_row: int) -> str:
        """基于内容推断餐次类型"""
        content_text = ""
        
        # 收集分段内的所有文本内容
        for row_idx in range(start_row, end_row + 1):
            for col_idx in range(len(df.columns)):
                cell_value = str(df.iloc[row_idx, col_idx]).strip()
                if cell_value and cell_value != 'nan':
                    content_text += cell_value + " "
        
        # 基于关键词匹配推断餐次
        scores = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
        
        for meal_type, indicators in self.meal_indicators.items():
            # 分类名称匹配
            for category in indicators['categories']:
                if category in content_text:
                    scores[meal_type] += 3
            
            # 关键词匹配
            for keyword in indicators['keywords']:
                content_text_count = content_text.count(keyword)
                scores[meal_type] += content_text_count
        
        # 返回得分最高的餐次类型
        best_meal = max(scores.items(), key=lambda x: x[1])
        return best_meal[0] if best_meal[1] > 0 else 'lunch'  # 默认午餐
    
    def _validate_and_adjust_segments(self, segments: List[MealSegment]) -> List[MealSegment]:
        """验证和调整分段结果"""
        if not segments:
            return segments
        
        # 确保餐次类型的合理性
        if len(segments) == 1:
            # 只有一个分段，可能是午餐
            segments[0].meal_type = 'lunch'
        elif len(segments) == 2:
            # 两个分段，可能是早餐+午餐 或 午餐+晚餐
            segments[0].meal_type = 'breakfast'
            segments[1].meal_type = 'lunch'
        elif len(segments) >= 3:
            # 三个或更多分段，按早午晚顺序
            segments[0].meal_type = 'breakfast'
            segments[1].meal_type = 'lunch'
            segments[2].meal_type = 'dinner'
            # 多余的分段合并到晚餐
            for i in range(3, len(segments)):
                segments[2].end_row = segments[i].end_row
            segments = segments[:3]
        
        return segments

@dataclass
class MealSegment:
    """餐次分段数据结构"""
    start_row: int
    end_row: int
    meal_type: str
```

### 2. 增强的横向格式解析器

**重构`_parse_horizontal_weekly_format`方法：**

```python
def _parse_horizontal_weekly_format(self, df: pd.DataFrame) -> List[MenuData]:
    """
    增强的横向格式解析器，支持多餐次识别
    """
    logger.info("尝试解析横向weekly格式（支持多餐次）")
    
    # 1. 找到星期标题行
    weekday_row_idx, weekday_cols = self._find_weekday_headers(df)
    if not weekday_cols:
        raise ExcelParsingError("Could not find weekday headers in horizontal format")
    
    # 2. 识别餐次分段
    segment_identifier = MealSegmentIdentifier()
    meal_segments = segment_identifier.identify_meal_segments(df, weekday_row_idx)
    
    logger.info(f"识别到 {len(meal_segments)} 个餐次分段")
    for i, segment in enumerate(meal_segments):
        logger.info(f"分段{i+1}: {segment.meal_type}, 行{segment.start_row}-{segment.end_row}")
    
    # 3. 提取基准日期
    base_date = self._extract_base_date(df)
    if not base_date:
        raise ExcelParsingError("Could not determine base date for horizontal weekly format")
    
    # 4. 为每个星期和每个餐次解析菜单数据
    result = []
    
    for col_idx, (weekday_name, weekday_num) in weekday_cols.items():
        menu_date = self._calculate_date_for_weekday(base_date, weekday_num)
        meals = []
        
        # 为每个餐次分段创建Meal对象
        for segment in meal_segments:
            items = self._extract_items_from_segment(df, segment, col_idx)
            
            if items:  # 只有当有菜品时才创建餐次
                meal_times = {
                    'breakfast': '07:30',
                    'lunch': '12:00',
                    'dinner': '18:00'
                }
                
                meal = Meal(
                    type=segment.meal_type,
                    time=meal_times.get(segment.meal_type, '12:00'),
                    items=items
                )
                meals.append(meal)
        
        if meals:
            menu_data = MenuData(
                date=menu_date.strftime('%Y-%m-%d'),
                meals=meals
            )
            result.append(menu_data)
            logger.info(f"解析{weekday_name}({menu_date})菜单，共{len(meals)}个餐次")
    
    if not result:
        raise ExcelParsingError("No valid menu data found in horizontal weekly format")
    
    logger.info(f"成功解析横向weekly格式，生成{len(result)}天菜单")
    return sorted(result, key=lambda x: x.date)

def _extract_items_from_segment(self, df: pd.DataFrame, segment: MealSegment, col_idx: int) -> List[MenuItem]:
    """从餐次分段中提取菜品"""
    items = []
    current_category = None
    item_order = 0
    category_order = 0
    category_order_map = {}
    
    for row_idx in range(segment.start_row, segment.end_row + 1):
        # 检查第一列是否是分类
        category_cell = str(df.iloc[row_idx, 0]).strip()
        if category_cell and category_cell != 'nan' and not pd.isna(df.iloc[row_idx, 0]):
            if category_cell not in ['类别', '早餐', '午餐', '晚餐']:
                current_category = category_cell
                if current_category not in category_order_map:
                    category_order_map[current_category] = category_order
                    category_order += 1
        
        # 获取该星期的菜品
        if col_idx < len(df.columns):
            food_cell = df.iloc[row_idx, col_idx]
            if pd.isna(food_cell) or str(food_cell).strip() in ['', 'nan']:
                continue
            
            food_items = str(food_cell).strip()
            if food_items:
                # 分割多个菜品
                item_list = re.split(r'[,，、；;]', food_items)
                for item_name in item_list:
                    item_name = item_name.strip()
                    if item_name and item_name != 'nan':
                        items.append(MenuItem(
                            name=item_name,
                            category=current_category or '其他',
                            description=None,
                            price=None,
                            order=item_order,
                            category_order=category_order_map.get(current_category, 0)
                        ))
                        item_order += 1
    
    return items
```

### 3. 兼容性和回退策略

**确保不影响现有功能：**

```python
def _parse_horizontal_weekly_format_with_fallback(self, df: pd.DataFrame) -> List[MenuData]:
    """
    带回退策略的横向格式解析
    """
    try:
        # 尝试新的多餐次解析
        return self._parse_horizontal_weekly_format_multi_meal(df)
    except Exception as e:
        logger.warning(f"多餐次解析失败，回退到原始方法: {e}")
        
        try:
            # 回退到原始的单餐次解析
            return self._parse_horizontal_weekly_format_single_meal(df)
        except Exception as e2:
            logger.error(f"原始解析方法也失败: {e2}")
            raise ExcelParsingError(f"横向格式解析失败: {e2}")

def _parse_horizontal_weekly_format_single_meal(self, df: pd.DataFrame) -> List[MenuData]:
    """
    原始的单餐次解析方法（作为回退）
    """
    # 保留原始实现作为回退方案
    # ... 原始代码 ...
```

### 4. 测试和验证策略

**单元测试设计：**

```python
class TestHorizontalMealClassification(unittest.TestCase):
    
    def setUp(self):
        self.parser = ExcelParser()
        self.identifier = MealSegmentIdentifier()
    
    def test_meal_segment_identification(self):
        """测试餐次分段识别"""
        # 创建模拟DataFrame
        data = {
            'A': ['标题', '早餐', '星期一', '粥品', '小米粥', '类别', '荤菜', '红烧肉', '类别', '汤品', '紫菜蛋花汤'],
            'B': ['', '', '星期二', '', '大米粥', '', '', '糖醋里脊', '', '', '冬瓜汤']
        }
        df = pd.DataFrame(data)
        
        segments = self.identifier.identify_meal_segments(df, weekday_row_idx=2)
        
        # 验证分段结果
        self.assertEqual(len(segments), 3)  # 应该识别出3个餐次
        self.assertEqual(segments[0].meal_type, 'breakfast')
        self.assertEqual(segments[1].meal_type, 'lunch')
        self.assertEqual(segments[2].meal_type, 'dinner')
    
    def test_meal_type_inference(self):
        """测试餐次类型推断"""
        # 测试基于内容的餐次推断
        breakfast_content = "粥品 小米粥 包点 豆浆"
        lunch_content = "荤菜 红烧肉 素菜 青菜 汤品"
        dinner_content = "清淡 小菜 汤品 粥"
        
        # 验证推断结果
        self.assertEqual(self.identifier._infer_meal_type_from_content_text(breakfast_content), 'breakfast')
        self.assertEqual(self.identifier._infer_meal_type_from_content_text(lunch_content), 'lunch')
        self.assertEqual(self.identifier._infer_meal_type_from_content_text(dinner_content), 'dinner')
    
    def test_horizontal_format_parsing(self):
        """测试完整的横向格式解析"""
        # 使用真实的1月菜单文件进行测试
        file_path = 'menu/省投食堂菜单：1月4日-9日.xlsx'
        
        if os.path.exists(file_path):
            menu_data_list = self.parser.parse_excel_file(file_path)
            
            # 验证解析结果
            self.assertGreater(len(menu_data_list), 0)
            
            # 检查是否有多个餐次
            for menu_data in menu_data_list:
                self.assertGreater(len(menu_data.meals), 1, "应该识别出多个餐次")
                
                # 验证餐次类型
                meal_types = [meal.type for meal in menu_data.meals]
                self.assertIn('breakfast', meal_types, "应该包含早餐")
                self.assertIn('lunch', meal_types, "应该包含午餐")
```

### 5. 配置和监控

**配置选项：**

```python
# config.py
class Config:
    # 横向格式解析配置
    HORIZONTAL_MEAL_CLASSIFICATION_ENABLED = True
    HORIZONTAL_MEAL_FALLBACK_ENABLED = True
    
    # 餐次识别配置
    MEAL_INFERENCE_STRATEGY = 'content_based'  # 'content_based' or 'position_based'
    MEAL_SEPARATOR_PATTERNS = ['类别', '早餐', '午餐', '晚餐']
    
    # 默认餐次时间
    DEFAULT_MEAL_TIMES = {
        'breakfast': '07:30',
        'lunch': '12:00',
        'dinner': '18:00'
    }
```

**监控指标：**

```python
class HorizontalMealClassificationMetrics:
    """横向格式餐次分类监控"""
    
    def __init__(self):
        self.files_processed = 0
        self.multi_meal_success = 0
        self.fallback_used = 0
        self.meal_segments_identified = 0
    
    def record_processing(self, filename: str, segments_count: int, used_fallback: bool):
        """记录处理结果"""
        self.files_processed += 1
        self.meal_segments_identified += segments_count
        
        if used_fallback:
            self.fallback_used += 1
        else:
            self.multi_meal_success += 1
        
        logger.info(f"处理横向格式文件: {filename}, 识别{segments_count}个餐次分段, 回退: {used_fallback}")
    
    def get_success_rate(self) -> float:
        """获取多餐次识别成功率"""
        if self.files_processed == 0:
            return 0.0
        return self.multi_meal_success / self.files_processed
```

## 实施优先级

### 高优先级（立即实施）
1. **MealSegmentIdentifier类实现** - 核心餐次识别算法
2. **横向解析器重构** - 支持多餐次的解析逻辑
3. **基础测试用例** - 确保功能正确性

### 中优先级（后续优化）
1. **智能推断算法优化** - 提高识别准确率
2. **配置化支持** - 支持自定义餐次时间和分隔符
3. **性能优化** - 减少解析时间

### 低优先级（可选功能）
1. **高级监控指标** - 详细的统计和分析
2. **用户界面增强** - 餐次分类的可视化改进
3. **批量处理优化** - 大量文件的处理优化

## 风险缓解

### 技术风险
1. **解析准确性** - 通过多种识别策略和回退机制保证
2. **性能影响** - 算法优化和缓存策略
3. **兼容性问题** - 保留原始解析方法作为回退

### 业务风险
1. **用户体验中断** - 渐进式部署和快速回滚机制
2. **数据准确性** - 全面测试和验证
3. **维护复杂度** - 清晰的代码结构和文档

## 总结

横向格式菜单餐次分类的核心是实现智能的多餐次识别算法，通过分析Excel文件中的分隔符、内容特征和位置信息，准确识别早餐、午餐、晚餐的分段。

**关键技术点：**
1. **分段识别** - 基于"类别"行、空行、餐次标识等分隔符
2. **内容推断** - 基于菜品分类和关键词的餐次类型推断
3. **兼容性保证** - 回退机制确保不影响现有功能
4. **全面测试** - 确保各种格式和边界情况的正确处理

通过这个设计方案，1月菜单文件将能够正确显示早餐、午餐、晚餐的分类，显著改善用户体验。