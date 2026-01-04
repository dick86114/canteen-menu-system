"""
Excel parser module for the Canteen Menu System.

This module provides functionality to parse Excel files containing menu data
and convert them into structured MenuData objects.
"""

import pandas as pd
from openpyxl import load_workbook
from typing import List, Optional, Dict, Any, Union, Tuple
from datetime import datetime, date
import re
import logging
import os
from pathlib import Path

from ..models.menu import MenuData, Meal, MenuItem


logger = logging.getLogger(__name__)


class ExcelParsingError(Exception):
    """Custom exception for Excel parsing errors."""
    pass


class ExcelParser:
    """
    Excel parser for canteen menu files.
    
    Handles various Excel structures and date formats to extract menu data.
    """
    
    # Common date formats to try when parsing dates
    DATE_FORMATS = [
        '%Y-%m-%d',      # 2023-12-15
        '%Y/%m/%d',      # 2023/12/15
        '%d/%m/%Y',      # 15/12/2023
        '%d-%m-%Y',      # 15-12-2023
        '%m/%d/%Y',      # 12/15/2023
        '%m-%d-%Y',      # 12-15-2023
        '%Y年%m月%d日',   # Chinese format: 2023年12月15日
        '%m月%d日',       # Chinese format: 12月15日
    ]
    
    # Common meal type mappings (case-insensitive)
    MEAL_TYPE_MAPPINGS = {
        'breakfast': ['breakfast', '早餐', '早饭', '早点', 'morning'],
        'lunch': ['lunch', '午餐', '午饭', '中餐', 'noon', 'midday'],
        'dinner': ['dinner', '晚餐', '晚饭', '晚点', 'evening', 'supper']
    }
    
    def __init__(self):
        """Initialize the Excel parser."""
        self.supported_extensions = {'.xlsx', '.xls', '.csv', '.et'}
    
    def validate_file_format(self, file_path: Union[str, Path]) -> bool:
        """
        Validate that the file has a supported Excel format.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            True if file format is supported, False otherwise
        """
        try:
            path = Path(file_path)
            return path.suffix.lower() in self.supported_extensions
        except Exception as e:
            logger.error(f"Error validating file format: {e}")
            return False
    
    def parse_excel_file(self, file_path: Union[str, Path]) -> List[MenuData]:
        """
        Parse an Excel file and extract menu data.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            List of MenuData objects parsed from the file
            
        Raises:
            ExcelParsingError: If file cannot be parsed or is invalid
        """
        if not self.validate_file_format(file_path):
            raise ExcelParsingError(f"Unsupported file format. Supported formats: {self.supported_extensions}")
        
        try:
            # Store filename for date extraction
            self._current_filename = os.path.basename(str(file_path))
            
            # 检查文件扩展名
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.csv':
                # 读取CSV文件
                df = pd.read_csv(file_path, encoding='utf-8')
            elif file_extension == '.et':
                # 处理WPS表格文件(.et格式)
                df = self._parse_et_file(file_path)
            else:
                # 处理Excel文件
                # Try to load the workbook first to check if it's a valid Excel file
                workbook = None
                try:
                    workbook = load_workbook(file_path, read_only=True)
                    # Close workbook immediately after validation
                    workbook.close()
                except Exception as e:
                    if workbook:
                        workbook.close()
                    raise e
                
                # Read the Excel file with pandas for easier data manipulation
                # Use context manager to ensure proper file closure
                with pd.ExcelFile(file_path) as excel_file:
                    df = pd.read_excel(excel_file, sheet_name=0)  # Read first sheet
            
            if df.empty:
                raise ExcelParsingError("文件为空")
            
            return self._extract_menu_data(df)
            
        except FileNotFoundError:
            raise ExcelParsingError(f"File not found: {file_path}")
        except PermissionError:
            raise ExcelParsingError(f"Permission denied accessing file: {file_path}")
        except Exception as e:
            logger.error(f"Error parsing Excel file {file_path}: {e}")
            raise ExcelParsingError(f"Failed to parse Excel file: {str(e)}")
        finally:
            # Clean up filename reference
            if hasattr(self, '_current_filename'):
                delattr(self, '_current_filename')
    
    def _extract_menu_data(self, df: pd.DataFrame) -> List[MenuData]:
        """
        Extract menu data from a pandas DataFrame.
        
        Args:
            df: DataFrame containing the Excel data
            
        Returns:
            List of MenuData objects
        """
        # Clean the DataFrame
        df = self._clean_dataframe(df)
        
        # Try horizontal weekly format first (new format with weekdays as columns)
        try:
            return self._parse_horizontal_weekly_format(df)
        except Exception as e:
            logger.info(f"Horizontal weekly format parsing failed: {e}, trying standard weekly format")
        
        # Try weekly format (Chinese canteen style)
        try:
            return self._parse_weekly_format(df)
        except Exception as e:
            logger.info(f"Weekly format parsing failed: {e}, trying standard format")
        
        # Fall back to standard column-based format
        return self._parse_standard_format(df)
    
    def _parse_weekly_format(self, df: pd.DataFrame) -> List[MenuData]:
        """
        Parse weekly menu format (Chinese canteen style).
        
        Args:
            df: DataFrame with weekly menu structure
            
        Returns:
            List of MenuData objects
        """
        menu_data_dict = {}
        
        # 查找包含星期信息的行
        weekday_row_idx = None
        weekday_cols = {}
        
        for row_idx in range(min(10, len(df))):
            found_weekday_in_row = False
            for col_idx in range(1, len(df.columns)):  # 跳过第一列
                try:
                    cell_value = str(df.iloc[row_idx, col_idx]).strip()
                    if '星期' in cell_value:
                        if weekday_row_idx is None:
                            weekday_row_idx = row_idx
                        found_weekday_in_row = True
                        # 映射列索引到星期
                        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
                        for weekday in weekdays:
                            if weekday in cell_value:
                                weekday_cols[col_idx] = weekday
                                break  # 找到匹配的星期后跳出weekdays循环
                except:
                    continue
            # 如果这一行找到了星期信息，继续检查这一行的其他列，但不检查其他行
            if found_weekday_in_row:
                break
        
        if not weekday_cols:
            raise ExcelParsingError("Could not find weekday information in weekly format")
        
        logger.info(f"找到星期行: {weekday_row_idx}, 星期列映射: {weekday_cols}")
        
        # 从文件名提取日期信息
        from ..utils.timezone import current_year
        current_year_val = current_year()
        
        # 尝试从文件名中提取月份和日期范围
        filename = getattr(self, '_current_filename', '')
        logger.info(f"处理文件: {filename}")
        
        # 解析文件名中的日期信息（如：12月29-31）
        import re
        date_match = re.search(r'(\d+)月(\d+)-(\d+)', filename)
        if date_match:
            month = int(date_match.group(1))
            start_day = int(date_match.group(2))
            end_day = int(date_match.group(3))
            
            # 生成日期列表
            dates = []
            for day in range(start_day, end_day + 1):
                try:
                    from datetime import datetime
                    date_obj = datetime(current_year_val, month, day)
                    dates.append(date_obj.strftime('%Y-%m-%d'))
                except ValueError:
                    continue
            
            logger.info(f"解析出的日期: {dates}")
            
            if not dates:
                logger.warning("未能解析出有效日期")
                raise ExcelParsingError("Could not parse dates from filename")
            
            # 映射星期到日期
            weekday_to_date = {}
            weekday_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
            for col_idx, weekday in weekday_cols.items():
                weekday_index = weekday_names.index(weekday)
                if weekday_index < len(dates):
                    weekday_to_date[col_idx] = dates[weekday_index]
            
            logger.info(f"星期到日期映射: {weekday_to_date}")
            
            # 处理菜单数据
            current_meal_type = "早餐"  # 默认餐次
            category_row_count = 0  # 记录遇到的"类别"行数量
            explicit_meal_set = False  # 标记是否已经通过明确标识设置了餐次
            current_category = None  # 当前分类名称，用于延续到后续行
            category_order = 0  # 分类顺序计数器
            item_order = 0  # 菜品顺序计数器
            category_order_map = {}  # 分类名称到顺序的映射
            
            for row_idx in range(len(df)):
                if row_idx == weekday_row_idx:
                    continue
                    
                try:
                    first_col_value = str(df.iloc[row_idx, 0]).strip()
                    
                    # 检查是否是餐次标识
                    if first_col_value in ['早餐', '午餐', '晚餐']:
                        current_meal_type = first_col_value
                        explicit_meal_set = True  # 标记为明确设置
                        current_category = None  # 重置分类
                        category_order = 0  # 重置分类顺序
                        item_order = 0  # 重置菜品顺序
                        category_order_map = {}  # 重置分类顺序映射
                        logger.info(f"明确识别餐次标识: {current_meal_type}")
                        continue
                    
                    # 检查是否是类别行或空行
                    if first_col_value == '类别':
                        category_row_count += 1
                        current_category = None  # 重置分类
                        category_order = 0  # 重置分类顺序
                        item_order = 0  # 重置菜品顺序
                        category_order_map = {}  # 重置分类顺序映射
                        if not explicit_meal_set:  # 只有在没有明确餐次标识时才推断
                            if category_row_count == 1:
                                # 第一个"类别"行，通常是早餐
                                current_meal_type = "早餐"
                            elif category_row_count == 2:
                                # 第二个"类别"行，通常是午餐
                                current_meal_type = "午餐"
                            elif category_row_count == 3:
                                # 第三个"类别"行，通常是晚餐
                                current_meal_type = "晚餐"
                            logger.info(f"推断第{category_row_count}个类别行为{current_meal_type}")
                        else:
                            logger.info(f"跳过第{category_row_count}个类别行推断，当前餐次: {current_meal_type}")
                        # 重置明确设置标记，为下一个餐次做准备
                        if category_row_count > 1:
                            explicit_meal_set = False
                        continue
                    elif first_col_value in ['NaN', 'nan'] or pd.isna(df.iloc[row_idx, 0]):
                        # 第一列为空（NaN），继续使用当前分类，不做任何处理
                        pass
                    elif first_col_value == '':
                        # 空字符串，继续使用当前分类
                        pass
                    else:
                        # 如果第一列有内容，检查是否是新的分类名称
                        # 使用更智能的分类识别逻辑
                        is_category = self._is_likely_category_name(first_col_value)
                        if is_category:
                            # 这是一个新的分类名称
                            current_category = first_col_value
                            category_order += 1
                            category_order_map[current_category] = category_order
                            logger.info(f"识别到新分类: {current_category} (顺序: {category_order})")
                        else:
                            # 如果第一列内容看起来像菜品名称，则不更新分类
                            logger.debug(f"第{row_idx}行第一列看起来像菜品名称，不更新分类: {first_col_value}")
                            pass
                    
                    # 处理菜品数据
                    for col_idx, date_str in weekday_to_date.items():
                        try:
                            food_value = str(df.iloc[row_idx, col_idx]).strip()
                            
                            if food_value and food_value not in ['NaN', 'nan', '<NA>', '']:
                                # 创建或获取MenuData
                                if date_str not in menu_data_dict:
                                    menu_data_dict[date_str] = MenuData(date=date_str)
                                
                                menu_data = menu_data_dict[date_str]
                                
                                # 确定餐次和时间
                                meal_type = self._normalize_meal_type(current_meal_type) or 'lunch'
                                time_str = self._get_meal_time(meal_type)
                                
                                # 查找或创建餐次
                                meal = menu_data.get_meal_by_type(meal_type)
                                if not meal:
                                    meal = Meal(type=meal_type, time=time_str)
                                    menu_data.add_meal(meal)
                                
                                # 分割多个菜品（用逗号、顿号等分隔）
                                foods = re.split(r'[，,、/]', food_value)
                                for food in foods:
                                    food = food.strip()
                                    if food:
                                        # 使用当前分类，如果没有则使用第一列的值
                                        category_to_use = current_category
                                        if not category_to_use and first_col_value not in ['NaN', 'nan', '']:
                                            category_to_use = first_col_value
                                        
                                        # 获取分类顺序
                                        cat_order = category_order_map.get(category_to_use, 0)
                                        
                                        item_order += 1
                                        menu_item = MenuItem(
                                            name=food,
                                            category=category_to_use,
                                            order=item_order,
                                            category_order=cat_order
                                        )
                                        meal.add_item(menu_item)
                        except Exception as e:
                            logger.warning(f"处理第{row_idx}行第{col_idx}列时出错: {e}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"处理第{row_idx}行时出错: {e}")
                    continue
        
        result = list(menu_data_dict.values())
        if not result:
            raise ExcelParsingError("No valid menu data found in weekly format")
        
        logger.info(f"成功解析weekly格式，生成{len(result)}天菜单")
        return sorted(result, key=lambda x: x.date)
    
    def _parse_horizontal_weekly_format(self, df: pd.DataFrame) -> List[MenuData]:
        """
        Parse horizontal weekly format where weekdays are columns and categories are rows.
        Enhanced version with multi-meal support.
        
        This format has:
        - First row: title (e.g., "食堂菜单（1月4-9日）")
        - Second row: meal type (e.g., "早餐")
        - Third row: weekday headers (星期天, 星期一, etc.)
        - Following rows: categories and food items
        
        Args:
            df: DataFrame with horizontal weekly structure
            
        Returns:
            List of MenuData objects
        """
        logger.info("尝试解析横向weekly格式（支持多餐次）")
        
        try:
            return self._parse_horizontal_weekly_format_multi_meal(df)
        except Exception as e:
            logger.warning(f"多餐次解析失败，回退到原始方法: {e}")
            return self._parse_horizontal_weekly_format_single_meal(df)
    
    def _parse_horizontal_weekly_format_multi_meal(self, df: pd.DataFrame) -> List[MenuData]:
        """
        增强的横向格式解析器，支持多餐次识别
        """
        logger.info("使用多餐次解析器")
        
        # 1. 找到星期标题行
        weekday_row_idx, weekday_cols = self._find_weekday_headers(df)
        if not weekday_cols:
            raise ExcelParsingError("Could not find weekday headers in horizontal format")
        
        # 2. 识别餐次分段
        from .meal_segment_identifier import MealSegmentIdentifier
        segment_identifier = MealSegmentIdentifier()
        meal_segments = segment_identifier.identify_meal_segments(df, weekday_row_idx)
        
        logger.info(f"识别到 {len(meal_segments)} 个餐次分段")
        for i, segment in enumerate(meal_segments):
            logger.info(f"分段{i+1}: {segment.meal_type}, 行{segment.start_row}-{segment.end_row}")
        
        # 3. 提取基准日期
        base_date = self._extract_base_date_from_df(df)
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
    
    def _find_weekday_headers(self, df: pd.DataFrame) -> Tuple[Optional[int], Dict[int, Tuple[str, int]]]:
        """
        找到星期标题行
        
        Returns:
            Tuple[Optional[int], Dict[int, Tuple[str, int]]]: (行索引, {列索引: (星期名, 星期数)})
        """
        weekday_row_idx = None
        weekday_cols = {}
        
        for row_idx in range(min(5, len(df))):
            row_data = df.iloc[row_idx].astype(str)
            weekday_found = False
            
            for col_idx, cell_value in enumerate(row_data):
                if pd.isna(cell_value) or cell_value.strip() == 'nan':
                    continue
                    
                cell_value = str(cell_value).strip()
                
                # Check for weekday patterns
                weekdays = {
                    '星期天': 6, '星期日': 6, '周日': 6, '日': 6,
                    '星期一': 0, '周一': 0, '一': 0,
                    '星期二': 1, '周二': 1, '二': 1,
                    '星期三': 2, '周三': 2, '三': 2,
                    '星期四': 3, '周四': 3, '四': 3,
                    '星期五': 4, '周五': 4, '五': 4,
                    '星期六': 5, '周六': 5, '六': 5,
                }
                
                for weekday_name, weekday_num in weekdays.items():
                    if weekday_name in cell_value:
                        weekday_row_idx = row_idx
                        weekday_cols[col_idx] = (weekday_name, weekday_num)
                        weekday_found = True
                        break
            
            if weekday_found:
                break
        
        return weekday_row_idx, weekday_cols
    
    def _extract_base_date_from_df(self, df: pd.DataFrame) -> Optional[date]:
        """从DataFrame中提取基准日期"""
        # Try to extract from filename first
        if hasattr(self, '_current_filename'):
            base_date = self._extract_date_from_filename_string(self._current_filename)
            if base_date:
                return base_date
        
        # Try to extract from title row
        if len(df) > 0:
            title_row = df.iloc[0, 0] if len(df) > 0 else ""
            base_date = self._extract_date_from_title(str(title_row))
            if base_date:
                return base_date
        
        return None
    
    def _extract_items_from_segment(self, df: pd.DataFrame, segment, col_idx: int) -> List[MenuItem]:
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
    
    def _parse_horizontal_weekly_format_single_meal(self, df: pd.DataFrame) -> List[MenuData]:
        """
        原始的单餐次解析方法（作为回退）
        """
        logger.info("使用单餐次回退解析器")
        
        # Find the row with weekday headers
        weekday_row_idx = None
        weekday_cols = {}
        
        for row_idx in range(min(5, len(df))):
            row_data = df.iloc[row_idx].astype(str)
            weekday_found = False
            
            for col_idx, cell_value in enumerate(row_data):
                if pd.isna(cell_value) or cell_value.strip() == 'nan':
                    continue
                    
                cell_value = str(cell_value).strip()
                
                # Check for weekday patterns
                weekdays = {
                    '星期天': 6, '星期日': 6, '周日': 6, '日': 6,
                    '星期一': 0, '周一': 0, '一': 0,
                    '星期二': 1, '周二': 1, '二': 1,
                    '星期三': 2, '周三': 2, '三': 2,
                    '星期四': 3, '周四': 3, '四': 3,
                    '星期五': 4, '周五': 4, '五': 4,
                    '星期六': 5, '周六': 5, '六': 5,
                }
                
                for weekday_name, weekday_num in weekdays.items():
                    if weekday_name in cell_value:
                        weekday_row_idx = row_idx
                        weekday_cols[col_idx] = (weekday_name, weekday_num)
                        weekday_found = True
                        break
            
            if weekday_found:
                break
        
        if not weekday_cols:
            raise ExcelParsingError("Could not find weekday headers in horizontal format")
        
        logger.info(f"找到星期标题行: {weekday_row_idx}, 列映射: {weekday_cols}")
        
        # Find meal type (should be in a row before weekday headers)
        meal_type = 'lunch'  # default
        for row_idx in range(max(0, weekday_row_idx - 2), weekday_row_idx):
            for col_idx in range(len(df.columns)):
                cell_value = str(df.iloc[row_idx, col_idx]).strip()
                if cell_value in ['早餐', 'breakfast']:
                    meal_type = 'breakfast'
                elif cell_value in ['午餐', '中餐', 'lunch']:
                    meal_type = 'lunch'
                elif cell_value in ['晚餐', 'dinner']:
                    meal_type = 'dinner'
        
        # Extract date range from filename or title
        base_date = self._extract_base_date_from_df(df)
        if not base_date:
            raise ExcelParsingError("Could not determine base date for horizontal weekly format")
        
        # Parse menu data for each weekday
        result = []
        
        for col_idx, (weekday_name, weekday_num) in weekday_cols.items():
            # Calculate the actual date for this weekday
            menu_date = self._calculate_date_for_weekday(base_date, weekday_num)
            
            # Extract food items for this day
            items = []
            current_category = None
            
            # Start from the row after weekday headers
            for row_idx in range(weekday_row_idx + 1, len(df)):
                # Check first column for category
                category_cell = str(df.iloc[row_idx, 0]).strip()
                if category_cell and category_cell != 'nan' and not pd.isna(df.iloc[row_idx, 0]):
                    current_category = category_cell
                
                # Get food item for this day
                if col_idx < len(df.columns):
                    food_cell = df.iloc[row_idx, col_idx]
                    if pd.isna(food_cell) or str(food_cell).strip() in ['', 'nan']:
                        continue
                    
                    food_items = str(food_cell).strip()
                    if food_items:
                        # Split multiple items (separated by comma, 、, or other delimiters)
                        item_list = re.split(r'[,，、；;]', food_items)
                        for item_name in item_list:
                            item_name = item_name.strip()
                            if item_name and item_name != 'nan':
                                items.append(MenuItem(
                                    name=item_name,
                                    category=current_category or '其他',
                                    description=None,
                                    price=None
                                ))
            
            if items:
                # Create meal with default time based on meal type
                meal_times = {
                    'breakfast': '07:30',
                    'lunch': '12:00',
                    'dinner': '18:00'
                }
                
                meal = Meal(
                    type=meal_type,
                    time=meal_times.get(meal_type, '12:00'),
                    items=items
                )
                
                menu_data = MenuData(
                    date=menu_date.strftime('%Y-%m-%d'),
                    meals=[meal]
                )
                
                result.append(menu_data)
                logger.info(f"解析{weekday_name}({menu_date})菜单，共{len(items)}道菜")
        
        if not result:
            raise ExcelParsingError("No valid menu data found in horizontal weekly format")
        
        logger.info(f"成功解析横向weekly格式（单餐次），生成{len(result)}天菜单")
        return sorted(result, key=lambda x: x.date)
        weekday_cols = {}
        
        for row_idx in range(min(5, len(df))):
            row_data = df.iloc[row_idx].astype(str)
            weekday_found = False
            
            for col_idx, cell_value in enumerate(row_data):
                if pd.isna(cell_value) or cell_value.strip() == 'nan':
                    continue
                    
                cell_value = str(cell_value).strip()
                
                # Check for weekday patterns
                weekdays = {
                    '星期天': 6, '星期日': 6, '周日': 6, '日': 6,
                    '星期一': 0, '周一': 0, '一': 0,
                    '星期二': 1, '周二': 1, '二': 1,
                    '星期三': 2, '周三': 2, '三': 2,
                    '星期四': 3, '周四': 3, '四': 3,
                    '星期五': 4, '周五': 4, '五': 4,
                    '星期六': 5, '周六': 5, '六': 5,
                }
                
                for weekday_name, weekday_num in weekdays.items():
                    if weekday_name in cell_value:
                        weekday_row_idx = row_idx
                        weekday_cols[col_idx] = (weekday_name, weekday_num)
                        weekday_found = True
                        break
            
            if weekday_found:
                break
        
        if not weekday_cols:
            raise ExcelParsingError("Could not find weekday headers in horizontal format")
        
        logger.info(f"找到星期标题行: {weekday_row_idx}, 列映射: {weekday_cols}")
        
        # Find meal type (should be in a row before weekday headers)
        meal_type = 'lunch'  # default
        for row_idx in range(max(0, weekday_row_idx - 2), weekday_row_idx):
            for col_idx in range(len(df.columns)):
                cell_value = str(df.iloc[row_idx, col_idx]).strip()
                if cell_value in ['早餐', 'breakfast']:
                    meal_type = 'breakfast'
                elif cell_value in ['午餐', '中餐', 'lunch']:
                    meal_type = 'lunch'
                elif cell_value in ['晚餐', 'dinner']:
                    meal_type = 'dinner'
        
        # Extract date range from filename or title
        base_date = None
        
        # Try to extract from filename
        if hasattr(self, '_current_filename'):
            base_date = self._extract_date_from_filename_string(self._current_filename)
        
        if not base_date:
            # Try to extract from title row
            title_row = df.iloc[0, 0] if len(df) > 0 else ""
            base_date = self._extract_date_from_title(str(title_row))
        
        if not base_date:
            raise ExcelParsingError("Could not determine base date for horizontal weekly format")
        
        # Parse menu data for each weekday
        result = []
        
        for col_idx, (weekday_name, weekday_num) in weekday_cols.items():
            # Calculate the actual date for this weekday
            menu_date = self._calculate_date_for_weekday(base_date, weekday_num)
            
            # Extract food items for this day
            items = []
            current_category = None
            
            # Start from the row after weekday headers
            for row_idx in range(weekday_row_idx + 1, len(df)):
                # Check first column for category
                category_cell = str(df.iloc[row_idx, 0]).strip()
                if category_cell and category_cell != 'nan' and not pd.isna(df.iloc[row_idx, 0]):
                    current_category = category_cell
                
                # Get food item for this day
                if col_idx < len(df.columns):
                    food_cell = df.iloc[row_idx, col_idx]
                    if pd.isna(food_cell) or str(food_cell).strip() in ['', 'nan']:
                        continue
                    
                    food_items = str(food_cell).strip()
                    if food_items:
                        # Split multiple items (separated by comma, 、, or other delimiters)
                        item_list = re.split(r'[,，、；;]', food_items)
                        for item_name in item_list:
                            item_name = item_name.strip()
                            if item_name and item_name != 'nan':
                                items.append(MenuItem(
                                    name=item_name,
                                    category=current_category or '其他',
                                    description=None,
                                    price=None
                                ))
            
            if items:
                # Create meal with default time based on meal type
                meal_times = {
                    'breakfast': '07:30',
                    'lunch': '12:00',
                    'dinner': '18:00'
                }
                
                meal = Meal(
                    type=meal_type,
                    time=meal_times.get(meal_type, '12:00'),
                    items=items
                )
                
                menu_data = MenuData(
                    date=menu_date.strftime('%Y-%m-%d'),  # 转换为字符串格式
                    meals=[meal]
                )
                
                result.append(menu_data)
                logger.info(f"解析{weekday_name}({menu_date})菜单，共{len(items)}道菜")
        
        if not result:
            raise ExcelParsingError("No valid menu data found in horizontal weekly format")
        
        logger.info(f"成功解析横向weekly格式，生成{len(result)}天菜单")
        return sorted(result, key=lambda x: x.date)
    
    def _extract_date_from_title(self, title: str) -> Optional[date]:
        """Extract date from title string like '食堂菜单（1月4-9日）'"""
        try:
            # Pattern for Chinese date format like "1月4-9日" or "1月4日-9日"
            pattern = r'(\d+)月(\d+)[-–]?(\d*)日?'
            match = re.search(pattern, title)
            if match:
                month = int(match.group(1))
                start_day = int(match.group(2))
                
                # Use current year
                current_year = datetime.now().year
                return date(current_year, month, start_day)
        except Exception as e:
            logger.warning(f"Could not extract date from title '{title}': {e}")
        
        return None
    
    def _extract_date_from_filename_string(self, filename: str) -> Optional[date]:
        """Extract date from filename string"""
        try:
            # 优先尝试包含年份的完整格式
            # 格式1: "2025年12月15-19" 或 "2026年1月4日-9日"
            year_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日?[-–](\d{1,2})日?'
            match = re.search(year_pattern, filename)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                start_day = int(match.group(3))
                logger.info(f"从文件名提取完整日期: {year}年{month}月{start_day}日")
                return date(year, month, start_day)
            
            # 回退到只有月日的格式（使用智能年份推断）
            # 格式2: "1月4日-9日" 或 "1月4-9日"
            month_pattern = r'(\d{1,2})月(\d{1,2})日?[-–](\d{1,2})日?'
            match = re.search(month_pattern, filename)
            if match:
                month = int(match.group(1))
                start_day = int(match.group(2))
                
                # 使用智能年份推断
                inferred_year = self._infer_year_from_month(month)
                logger.info(f"从文件名提取月日，推断年份: {inferred_year}年{month}月{start_day}日")
                return date(inferred_year, month, start_day)
                
        except Exception as e:
            logger.warning(f"Could not extract date from filename '{filename}': {e}")
        
        return None
    
    def _infer_year_from_month(self, month: int) -> int:
        """
        基于月份智能推断年份
        
        Args:
            month: 月份 (1-12)
            
        Returns:
            推断的年份
        """
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # 策略：基于时间窗口的推断
        if current_month <= 6:  # 当前是上半年 (1-6月)
            if month >= 7:  # 目标是下半年 (7-12月) -> 上一年
                return current_year - 1
            else:  # 目标是上半年 (1-6月) -> 当前年
                return current_year
        else:  # 当前是下半年 (7-12月)
            if month <= 6:  # 目标是上半年 (1-6月) -> 下一年
                return current_year + 1
            else:  # 目标是下半年 (7-12月) -> 当前年
                return current_year
    
    def _calculate_date_for_weekday(self, base_date: date, target_weekday: int) -> date:
        """
        Calculate the actual date for a given weekday based on a base date.
        
        Args:
            base_date: Base date (usually the start of the week)
            target_weekday: Target weekday (0=Monday, 6=Sunday)
            
        Returns:
            The calculated date
        """
        from datetime import timedelta
        
        # Get the weekday of the base date (0=Monday, 6=Sunday)
        base_weekday = base_date.weekday()
        
        # Calculate the difference in days
        days_diff = target_weekday - base_weekday
        
        # If the target weekday is before the base weekday in the same week,
        # it might be in the next week
        if days_diff < 0:
            days_diff += 7
        
        return base_date + timedelta(days=days_diff)
    
    def _parse_standard_format(self, df: pd.DataFrame) -> List[MenuData]:
        """
        Parse standard column-based format.
        
        Args:
            df: DataFrame with standard column structure
            
        Returns:
            List of MenuData objects
        """
        # Try to identify column structure
        column_mapping = self._identify_columns(df)
        
        if not column_mapping:
            raise ExcelParsingError("Could not identify required columns in Excel file")
        
        # 检查是否是weekly格式
        if column_mapping.get('format') == 'weekly':
            logger.info("使用weekly格式解析")
            return self._parse_weekly_format(df)
        
        # Extract data using the identified column mapping
        menu_data_dict = {}  # date -> MenuData
        
        for index, row in df.iterrows():
            try:
                # Skip empty rows
                if row.isna().all():
                    continue
                
                # Extract date
                try:
                    date_str = self._extract_date(row, column_mapping)
                    if not date_str:
                        continue
                except Exception as e:
                    logger.warning(f"Error extracting date from row {index}: {e}, column_mapping: {column_mapping}, row: {row.to_dict()}")
                    continue
                
                # Extract meal information
                meal_type = self._extract_meal_type(row, column_mapping)
                meal_time = self._extract_meal_time(row, column_mapping)
                food_name = self._extract_food_name(row, column_mapping)
                
                if not food_name:
                    continue
                
                # Create MenuItem
                menu_item = MenuItem(
                    name=food_name,
                    description=self._extract_description(row, column_mapping),
                    category=self._extract_category(row, column_mapping)
                )
                
                # Ensure MenuData exists for this date
                if date_str not in menu_data_dict:
                    menu_data_dict[date_str] = MenuData(date=date_str)
                
                # Find or create meal
                meal = menu_data_dict[date_str].get_meal_by_type(meal_type)
                if not meal:
                    meal = Meal(type=meal_type, time=meal_time)
                    menu_data_dict[date_str].add_meal(meal)
                
                # Add item to meal
                meal.add_item(menu_item)
                
            except Exception as e:
                logger.warning(f"Error processing row {index}: {e}")
                continue
        
        # Convert to list and validate
        result = []
        for menu_data in menu_data_dict.values():
            if menu_data.validate():
                result.append(menu_data)
            else:
                logger.warning(f"Invalid menu data for date {menu_data.date}")
        
        if not result:
            raise ExcelParsingError("No valid menu data found in Excel file")
        
        return sorted(result, key=lambda x: x.date)
    
    def _get_meal_time(self, meal_type: str) -> str:
        """Get default time for meal type."""
        time_map = {
            'breakfast': '07:30',
            'lunch': '12:00',
            'dinner': '18:00'
        }
        return time_map.get(meal_type, '12:00')
    
    def _split_food_items(self, food_items: str) -> List[str]:
        """Split food items string into individual items."""
        import re
        # Split by common separators
        items = re.split(r'[,，、/\\|]', food_items)
        return [item.strip() for item in items if item.strip()]
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the DataFrame by removing empty rows and columns.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Strip whitespace from string columns
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('nan', pd.NA)
        
        return df
    
    def _identify_columns(self, df: pd.DataFrame) -> Optional[Dict[str, str]]:
        """
        Identify which columns contain which type of data.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary mapping data types to column names, or None if identification fails
        """
        column_mapping = {}
        
        # Convert column names to strings and make them lowercase for comparison
        columns = [str(col).lower().strip() for col in df.columns]
        
        # Try to identify columns by name patterns
        for i, col_name in enumerate(columns):
            original_col = df.columns[i]
            
            # Date column patterns
            if any(pattern in col_name for pattern in ['date', '日期', '时间', 'time']):
                if 'date' not in column_mapping:
                    column_mapping['date'] = original_col
            
            # Meal type patterns
            elif any(pattern in col_name for pattern in ['meal', 'type', '餐次', '类型']):
                column_mapping['meal_type'] = original_col
            
            # Time patterns
            elif any(pattern in col_name for pattern in ['time', '时间', 'hour']):
                if 'time' not in column_mapping:
                    column_mapping['time'] = original_col
            
            # Food name patterns
            elif any(pattern in col_name for pattern in ['food', 'name', '菜名', '食物', 'dish']):
                column_mapping['food_name'] = original_col
            
            # Description patterns
            elif any(pattern in col_name for pattern in ['desc', '描述', '说明', 'detail']):
                column_mapping['description'] = original_col
            
            # Category patterns
            elif any(pattern in col_name for pattern in ['category', '类别', '分类', 'cat']):
                column_mapping['category'] = original_col
        
        # If we couldn't identify by column names, try to infer from data
        if 'date' not in column_mapping or 'food_name' not in column_mapping:
            column_mapping = self._infer_columns_from_data(df)
        
        # 特殊处理：检查是否是基于星期的菜单格式
        if 'date' not in column_mapping or 'food_name' not in column_mapping:
            weekly_mapping = self._try_parse_weekly_format(df)
            if weekly_mapping and weekly_mapping.get('format') == 'weekly':
                # 直接使用weekly格式解析，不需要column mapping
                return weekly_mapping
        
        # Ensure we have at least date and food_name
        if 'date' not in column_mapping or 'food_name' not in column_mapping:
            logger.error(f"无法识别必需的列。当前列映射: {column_mapping}")
            logger.error(f"DataFrame列名: {list(df.columns)}")
            logger.error(f"DataFrame前5行数据:")
            logger.error(f"{df.head().to_string()}")
            return None
        
        return column_mapping
    
    def _infer_columns_from_data(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Infer column types from data content when column names are not clear.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary mapping data types to column names
        """
        column_mapping = {}
        
        for col in df.columns:
            sample_values = df[col].dropna().head(10)
            
            if sample_values.empty:
                continue
            
            # Check if this looks like a date column
            if self._looks_like_date_column(sample_values):
                if 'date' not in column_mapping:
                    column_mapping['date'] = col
            
            # Check if this looks like a meal type column
            elif self._looks_like_meal_type_column(sample_values):
                column_mapping['meal_type'] = col
            
            # Check if this looks like a time column
            elif self._looks_like_time_column(sample_values):
                column_mapping['time'] = col
            
            # Check if this looks like a food name column (usually has longer text)
            elif self._looks_like_food_name_column(sample_values):
                if 'food_name' not in column_mapping:
                    column_mapping['food_name'] = col
        
        return column_mapping
    
    def _looks_like_date_column(self, values: pd.Series) -> bool:
        """Check if values look like dates."""
        for value in values:
            if pd.isna(value):
                continue
            if self._parse_date(str(value)):
                return True
        return False
    
    def _looks_like_meal_type_column(self, values: pd.Series) -> bool:
        """Check if values look like meal types."""
        for value in values:
            if pd.isna(value):
                continue
            if self._normalize_meal_type(str(value)):
                return True
        return False
    
    def _looks_like_time_column(self, values: pd.Series) -> bool:
        """Check if values look like times."""
        time_pattern = re.compile(r'^\d{1,2}:\d{2}')
        for value in values:
            if pd.isna(value):
                continue
            if time_pattern.match(str(value)):
                return True
        return False
    
    def _looks_like_food_name_column(self, values: pd.Series) -> bool:
        """Check if values look like food names (longer text, varied content)."""
        text_lengths = []
        for value in values:
            if pd.isna(value):
                continue
            text_lengths.append(len(str(value)))
        
        if not text_lengths:
            return False
        
        # Food names typically have some length and variation
        avg_length = sum(text_lengths) / len(text_lengths)
        return avg_length > 2 and len(set(text_lengths)) > 1
    
    def _extract_date(self, row: pd.Series, column_mapping: Dict[str, str]) -> Optional[str]:
        """Extract and normalize date from row."""
        if 'date' not in column_mapping:
            return None
        
        date_value = row[column_mapping['date']]
        if pd.isna(date_value):
            return None
        
        return self._parse_date(str(date_value))
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse various date formats and return normalized YYYY-MM-DD format.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Normalized date string or None if parsing fails
        """
        date_str = str(date_str).strip()
        
        # 如果已经是YYYY-MM-DD格式，验证并返回
        import re
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            try:
                # 验证日期是否有效
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                # 如果日期无效，继续尝试其他格式
                pass
        
        # Handle pandas Timestamp objects
        try:
            if 'Timestamp' in str(type(date_str)):
                return date_str.strftime('%Y-%m-%d')
        except:
            pass
        
        # Try different date formats
        for fmt in self.DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Try pandas to_datetime as fallback
        try:
            parsed_date = pd.to_datetime(date_str)
            return parsed_date.strftime('%Y-%m-%d')
        except:
            pass
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _extract_meal_type(self, row: pd.Series, column_mapping: Dict[str, str]) -> str:
        """Extract and normalize meal type from row."""
        if 'meal_type' in column_mapping:
            meal_value = row[column_mapping['meal_type']]
            if not pd.isna(meal_value):
                normalized = self._normalize_meal_type(str(meal_value))
                if normalized:
                    return normalized
        
        # Default to lunch if no meal type specified
        return 'lunch'
    
    def _is_likely_category_name(self, text: str) -> bool:
        """
        判断文本是否可能是分类名称
        
        Args:
            text: 要判断的文本
            
        Returns:
            True if likely a category name, False otherwise
        """
        # 已知的分类名称列表
        known_categories = {
            '油炸食品', '小菜类', '营养鸡蛋', '粥品', '饮品类', '包点', '清炒时蔬', '传统风味',
            '荤类', '半荤素', '蔬菜', '主食/面点', '控糖主食', '免费例汤', '炖罐', '捞化档口', 
            '水果酸奶', '档口特色', '营养例汤', '盖浇饭套餐', '每日下午外卖包点'
        }
        
        # 如果是已知分类，直接返回True
        if text in known_categories:
            return True
        
        # 分类名称的特征：
        # 1. 长度通常不超过8个字符
        # 2. 通常包含类别性词汇
        # 3. 不包含具体的菜品描述词汇
        
        if len(text) > 8:
            return False
        
        # 分类关键词
        category_keywords = ['类', '品', '食', '汤', '罐', '档', '奶', '特色', '套餐', '包点', '主食', '例汤']
        has_category_keyword = any(keyword in text for keyword in category_keywords)
        
        # 菜品描述词汇（这些通常出现在具体菜品名称中）
        dish_keywords = ['红烧', '清蒸', '白灼', '爆炒', '糖醋', '麻辣', '香辣', '蒜蓉', '葱爆', '宫保']
        has_dish_keyword = any(keyword in text for keyword in dish_keywords)
        
        # 如果包含分类关键词且不包含菜品描述词汇，可能是分类
        if has_category_keyword and not has_dish_keyword:
            return True
        
        # 如果长度很短（2-4字符）且不包含菜品描述词汇，也可能是分类
        if 2 <= len(text) <= 4 and not has_dish_keyword:
            return True
        
        return False
    
    def _normalize_meal_type(self, meal_str: str) -> Optional[str]:
        """
        Normalize meal type string to standard values.
        
        Args:
            meal_str: Raw meal type string
            
        Returns:
            Normalized meal type or None if not recognized
        """
        meal_str = meal_str.lower().strip()
        
        for standard_type, variations in self.MEAL_TYPE_MAPPINGS.items():
            if any(variation in meal_str for variation in variations):
                return standard_type
        
        return None
    
    def _extract_meal_time(self, row: pd.Series, column_mapping: Dict[str, str]) -> str:
        """Extract meal time from row."""
        if 'time' in column_mapping:
            time_value = row[column_mapping['time']]
            if not pd.isna(time_value):
                time_str = str(time_value).strip()
                # Try to parse and format time
                time_match = re.match(r'(\d{1,2}):(\d{2})', time_str)
                if time_match:
                    hour, minute = time_match.groups()
                    return f"{int(hour):02d}:{minute}"
        
        # Default times based on meal type (will be set later)
        return "12:00"
    
    def _extract_food_name(self, row: pd.Series, column_mapping: Dict[str, str]) -> Optional[str]:
        """Extract food name from row."""
        if 'food_name' not in column_mapping:
            return None
        
        food_value = row[column_mapping['food_name']]
        if pd.isna(food_value):
            return None
        
        food_name = str(food_value).strip()
        return food_name if food_name and food_name != 'nan' else None
    
    def _extract_description(self, row: pd.Series, column_mapping: Dict[str, str]) -> Optional[str]:
        """Extract description from row."""
        if 'description' not in column_mapping:
            return None
        
        desc_value = row[column_mapping['description']]
        if pd.isna(desc_value):
            return None
        
        description = str(desc_value).strip()
        return description if description and description != 'nan' else None
    
    def _extract_category(self, row: pd.Series, column_mapping: Dict[str, str]) -> Optional[str]:
        """Extract category from row."""
        if 'category' not in column_mapping:
            return None
        
        cat_value = row[column_mapping['category']]
        if pd.isna(cat_value):
            return None
        
        category = str(cat_value).strip()
        return category if category and category != 'nan' else None
    
    def _parse_et_file(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        解析WPS表格文件(.et格式)
        
        Args:
            file_path: WPS表格文件路径
            
        Returns:
            解析后的DataFrame
            
        Raises:
            ExcelParsingError: 如果文件无法解析
        """
        try:
            # 方法1: 尝试使用pandas直接读取（某些情况下pandas可以处理.et文件）
            try:
                logger.info(f"尝试使用pandas直接读取.et文件: {file_path}")
                df = pd.read_excel(file_path, engine='openpyxl')
                if not df.empty:
                    logger.info("成功使用pandas读取.et文件")
                    return df
            except Exception as e:
                logger.warning(f"pandas直接读取.et文件失败: {e}")
            
            # 方法2: 尝试使用xlrd引擎
            try:
                logger.info(f"尝试使用xlrd引擎读取.et文件: {file_path}")
                df = pd.read_excel(file_path, engine='xlrd')
                if not df.empty:
                    logger.info("成功使用xlrd引擎读取.et文件")
                    return df
            except Exception as e:
                logger.warning(f"xlrd引擎读取.et文件失败: {e}")
            
            # 方法3: 尝试将.et文件当作Excel文件处理
            try:
                logger.info(f"尝试将.et文件当作Excel文件处理: {file_path}")
                # 创建临时文件名，将.et改为.xlsx
                import tempfile
                import shutil
                
                with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                # 复制文件并重命名
                shutil.copy2(file_path, temp_path)
                
                try:
                    df = pd.read_excel(temp_path, engine='openpyxl')
                    if not df.empty:
                        logger.info("成功将.et文件当作Excel文件处理")
                        return df
                finally:
                    # 清理临时文件
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
            except Exception as e:
                logger.warning(f"将.et文件当作Excel文件处理失败: {e}")
            
            # 方法4: 尝试使用CSV方式读取（某些.et文件可能是文本格式）
            try:
                logger.info(f"尝试使用CSV方式读取.et文件: {file_path}")
                # 尝试不同的编码
                for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-16']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding, sep=None, engine='python')
                        if not df.empty:
                            logger.info(f"成功使用CSV方式读取.et文件，编码: {encoding}")
                            return df
                    except Exception:
                        continue
                        
            except Exception as e:
                logger.warning(f"CSV方式读取.et文件失败: {e}")
            
            # 如果所有方法都失败，抛出异常
            raise ExcelParsingError(
                f"无法解析WPS表格文件 {file_path}。"
                f"请尝试将文件另存为Excel格式(.xlsx)或CSV格式后重新上传。"
                f"支持的格式: {self.supported_extensions}"
            )
            
        except ExcelParsingError:
            raise
        except Exception as e:
            logger.error(f"解析.et文件时发生未知错误: {e}")
            raise ExcelParsingError(f"解析WPS表格文件失败: {str(e)}")
    
    def _try_parse_weekly_format(self, df: pd.DataFrame) -> Optional[Dict[str, str]]:
        """
        尝试解析基于星期的菜单格式
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Column mapping if weekly format detected, None otherwise
        """
        try:
            logger.info("尝试解析基于星期的菜单格式")
            
            # 检查是否包含星期信息（在数据行中而不是列名中）
            has_weekday = False
            for row_idx in range(min(10, len(df))):  # 检查前10行
                for col_idx in range(len(df.columns)):
                    try:
                        cell_value = str(df.iloc[row_idx, col_idx]).strip()
                        if any(day in cell_value for day in ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']):
                            has_weekday = True
                            logger.info(f"在第{row_idx}行第{col_idx}列发现星期信息: {cell_value}")
                            break
                    except:
                        continue
                if has_weekday:
                    break
            
            if not has_weekday:
                logger.info("未检测到星期格式")
                return None
            
            logger.info("检测到基于星期的菜单格式，将使用weekly格式解析")
            
            # 返回一个特殊的标记，表示这是weekly格式
            return {'format': 'weekly'}
            
        except Exception as e:
            logger.warning(f"解析基于星期的格式时出错: {e}")
            return None
    
    def _convert_weekly_to_standard_format(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        将基于星期的菜单格式转换为标准格式
        
        Args:
            df: 原始DataFrame
            
        Returns:
            转换后的DataFrame，包含标准的日期、餐次、菜品列
        """
        try:
            # 创建标准格式的数据列表
            standard_data = []
            
            # 从文件名提取日期信息
            from ..utils.timezone import current_year
            current_year_val = current_year()
            
            # 尝试从文件名中提取月份和日期范围
            filename = getattr(self, '_current_filename', '')
            logger.info(f"处理文件: {filename}")
            
            # 解析文件名中的日期信息（如：12月29-31）
            import re
            date_match = re.search(r'(\d+)月(\d+)-(\d+)', filename)
            if date_match:
                month = int(date_match.group(1))
                start_day = int(date_match.group(2))
                end_day = int(date_match.group(3))
                
                # 生成日期列表
                dates = []
                for day in range(start_day, end_day + 1):
                    try:
                        from datetime import datetime
                        date_obj = datetime(current_year_val, month, day)
                        dates.append(date_obj.strftime('%Y-%m-%d'))
                    except ValueError:
                        continue
                
                logger.info(f"解析出的日期: {dates}")
                
                if not dates:
                    logger.warning("未能解析出有效日期")
                    return None
                
                # 查找星期行
                weekday_row_idx = None
                weekday_cols = {}
                
                for row_idx in range(len(df)):
                    for col_idx, col in enumerate(df.columns):
                        cell_value = str(df.iloc[row_idx, col_idx]).strip()
                        if '星期' in cell_value:
                            weekday_row_idx = row_idx
                            # 映射星期到日期
                            weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
                            for i, weekday in enumerate(weekdays):
                                if weekday in cell_value and i < len(dates):
                                    weekday_cols[col] = dates[i]
                            break
                    if weekday_row_idx is not None:
                        break
                
                logger.info(f"星期列映射: {weekday_cols}")
                
                if weekday_cols:
                    # 处理菜单数据
                    current_meal_type = "早餐"  # 默认餐次
                    
                    for row_idx in range(len(df)):
                        if row_idx == weekday_row_idx:
                            continue
                            
                        first_col_value = str(df.iloc[row_idx, 0]).strip()
                        
                        # 检查是否是餐次标识
                        if first_col_value in ['早餐', '午餐', '晚餐', 'breakfast', 'lunch', 'dinner']:
                            current_meal_type = first_col_value
                            continue
                        
                        # 检查是否是类别行（跳过）
                        if first_col_value in ['类别', '油炸食品', '小菜类', '营养鸡蛋', '粥品', '饮品类', '包点', '清炒时蔬', '传统风味']:
                            continue
                        
                        # 处理菜品数据
                        for col, date_str in weekday_cols.items():
                            if col in df.columns:
                                col_idx = df.columns.get_loc(col)
                                food_value = str(df.iloc[row_idx, col_idx]).strip()
                                
                                if food_value and food_value != '<NA>' and food_value != 'nan':
                                    # 分割多个菜品（用逗号、顿号等分隔）
                                    foods = re.split(r'[，,、/]', food_value)
                                    for food in foods:
                                        food = food.strip()
                                        if food:
                                            standard_data.append({
                                                'date': date_str,  # 使用英文列名
                                                'meal_type': current_meal_type,
                                                'time': '12:00',  # 默认时间
                                                'food_name': food,
                                                'description': '',
                                                'category': first_col_value if first_col_value not in ['<NA>', 'nan', ''] else ''
                                            })
                
                if standard_data:
                    result_df = pd.DataFrame(standard_data)
                    logger.info(f"转换成功，生成 {len(result_df)} 行数据")
                    logger.info(f"转换后的前5行: \n{result_df.head().to_string()}")
                    return result_df
            
            logger.warning("无法从文件名解析日期信息")
            return None
            
        except Exception as e:
            logger.error(f"转换基于星期的格式时出错: {e}")
            return None