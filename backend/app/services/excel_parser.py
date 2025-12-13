"""
Excel parser module for the Canteen Menu System.

This module provides functionality to parse Excel files containing menu data
and convert them into structured MenuData objects.
"""

import pandas as pd
from openpyxl import load_workbook
from typing import List, Optional, Dict, Any, Union
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
        self.supported_extensions = {'.xlsx', '.xls', '.csv'}
    
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
        
        # Try weekly format first (Chinese canteen style)
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
        
        # Find weekday columns (look for patterns like 星期一, 星期二, etc.)
        weekday_columns = []
        for i, col in enumerate(df.columns):
            if i == 0:  # Skip first column (category column)
                continue
            weekday_columns.append(col)
        
        if len(weekday_columns) < 5:  # Need at least 5 weekdays
            raise ExcelParsingError("Could not find enough weekday columns in weekly format")
        
        # Generate dates for the week based on current year
        from datetime import datetime, timedelta
        from ..utils.timezone import current_year
        # Use current year and determine the Monday of the week
        current_year_val = current_year()
        
        # Try to extract date range from filename if available
        # Look for patterns like "12月8-12" or "12月15-19"
        import re
        filename = getattr(self, '_current_filename', '')
        date_match = re.search(r'(\d+)月(\d+)-(\d+)', filename)
        
        if date_match:
            month = int(date_match.group(1))
            start_day = int(date_match.group(2))
            monday = datetime(current_year_val, month, start_day)
        else:
            # Default to December 8, 2025 if no pattern found
            monday = datetime(2025, 12, 8)
        
        # Map weekday columns to dates
        weekday_to_date = {}
        for i, col in enumerate(weekday_columns[:5]):  # Only use first 5 columns
            date_obj = monday + timedelta(days=i)
            weekday_to_date[col] = date_obj.strftime('%Y-%m-%d')
        
        # Find meal sections and process data
        current_meal_type = None
        current_category = None
        
        for idx, row in df.iterrows():
            first_col_value = str(row.iloc[0]).strip()
            
            # Skip empty rows
            if pd.isna(first_col_value) or first_col_value.lower() in ['nan', 'none', '']:
                continue
            
            # Identify meal sections
            if first_col_value in ['早餐', '午餐', '晚餐']:
                current_meal_type = self._normalize_meal_type(first_col_value)
                continue
            elif first_col_value == '类别':
                continue  # Skip header row
            
            # This is a food category or food item row
            current_category = first_col_value
                
            # Process food items for each weekday
            for col in weekday_columns[:5]:
                if col not in weekday_to_date:
                    continue
                    
                date_key = weekday_to_date[col]
                food_items = str(row[col])
                
                if pd.isna(food_items) or food_items.lower() in ['nan', 'none', '']:
                    continue
                
                # Create or get MenuData for this date
                if date_key not in menu_data_dict:
                    menu_data_dict[date_key] = MenuData(date=date_key)
                
                menu_data = menu_data_dict[date_key]
                
                # Determine meal type and time
                meal_type = current_meal_type or 'lunch'
                time_str = self._get_meal_time(meal_type)
                
                # Find or create meal
                meal = menu_data.get_meal_by_type(meal_type)
                if not meal:
                    meal = Meal(type=meal_type, time=time_str)
                    menu_data.add_meal(meal)
                
                # Split multiple food items (separated by commas, slashes, etc.)
                food_list = self._split_food_items(food_items)
                
                for food_name in food_list:
                    if food_name.strip():
                        menu_item = MenuItem(
                            name=food_name.strip(),
                            category=current_category
                        )
                        meal.add_item(menu_item)
        
        result = list(menu_data_dict.values())
        if not result:
            raise ExcelParsingError("No valid menu data found in weekly format")
        
        return sorted(result, key=lambda x: x.date)
    
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
        
        # Extract data using the identified column mapping
        menu_data_dict = {}  # date -> MenuData
        
        for index, row in df.iterrows():
            try:
                # Skip empty rows
                if row.isna().all():
                    continue
                
                # Extract date
                date_str = self._extract_date(row, column_mapping)
                if not date_str:
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
        
        # Ensure we have at least date and food_name
        if 'date' not in column_mapping or 'food_name' not in column_mapping:
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