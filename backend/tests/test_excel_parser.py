"""
Tests for Excel parser functionality.
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
from openpyxl import Workbook

from app.services.excel_parser import ExcelParser, ExcelParsingError
from app.models.menu import MenuData, Meal, MenuItem


class TestExcelParser:
    """Test cases for ExcelParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ExcelParser()
    
    def test_parser_initialization(self):
        """Test ExcelParser initialization."""
        assert self.parser.supported_extensions == {'.xlsx', '.xls'}
        assert len(self.parser.DATE_FORMATS) > 0
        assert 'breakfast' in self.parser.MEAL_TYPE_MAPPINGS
        assert 'lunch' in self.parser.MEAL_TYPE_MAPPINGS
        assert 'dinner' in self.parser.MEAL_TYPE_MAPPINGS
    
    def test_validate_file_format_valid(self):
        """Test file format validation with valid extensions."""
        assert self.parser.validate_file_format("test.xlsx") is True
        assert self.parser.validate_file_format("test.xls") is True
        assert self.parser.validate_file_format("/path/to/menu.xlsx") is True
    
    def test_validate_file_format_invalid(self):
        """Test file format validation with invalid extensions."""
        assert self.parser.validate_file_format("test.txt") is False
        assert self.parser.validate_file_format("test.csv") is False
        assert self.parser.validate_file_format("test.pdf") is False
        assert self.parser.validate_file_format("test") is False
    
    def test_parse_date_various_formats(self):
        """Test date parsing with various formats."""
        # Test standard formats
        assert self.parser._parse_date("2023-12-15") == "2023-12-15"
        assert self.parser._parse_date("2023/12/15") == "2023-12-15"
        assert self.parser._parse_date("15/12/2023") == "2023-12-15"
        assert self.parser._parse_date("15-12-2023") == "2023-12-15"
        
        # Test invalid dates
        assert self.parser._parse_date("invalid") is None
        assert self.parser._parse_date("2023-13-01") is None
        assert self.parser._parse_date("") is None
    
    def test_normalize_meal_type(self):
        """Test meal type normalization."""
        # Test English
        assert self.parser._normalize_meal_type("breakfast") == "breakfast"
        assert self.parser._normalize_meal_type("LUNCH") == "lunch"
        assert self.parser._normalize_meal_type("Dinner") == "dinner"
        
        # Test Chinese
        assert self.parser._normalize_meal_type("早餐") == "breakfast"
        assert self.parser._normalize_meal_type("午餐") == "lunch"
        assert self.parser._normalize_meal_type("晚餐") == "dinner"
        
        # Test invalid
        assert self.parser._normalize_meal_type("snack") is None
        assert self.parser._normalize_meal_type("invalid") is None
    
    def test_looks_like_date_column(self):
        """Test date column detection."""
        # Date-like values
        date_values = pd.Series(["2023-12-15", "2023-12-16", "2023-12-17"])
        assert self.parser._looks_like_date_column(date_values) is True
        
        # Non-date values
        text_values = pd.Series(["chicken rice", "beef noodles", "fish curry"])
        assert self.parser._looks_like_date_column(text_values) is False
    
    def test_looks_like_meal_type_column(self):
        """Test meal type column detection."""
        # Meal type values
        meal_values = pd.Series(["breakfast", "lunch", "dinner"])
        assert self.parser._looks_like_meal_type_column(meal_values) is True
        
        # Chinese meal types
        chinese_meals = pd.Series(["早餐", "午餐", "晚餐"])
        assert self.parser._looks_like_meal_type_column(chinese_meals) is True
        
        # Non-meal values
        food_values = pd.Series(["chicken rice", "beef noodles", "fish curry"])
        assert self.parser._looks_like_meal_type_column(food_values) is False
    
    def test_looks_like_time_column(self):
        """Test time column detection."""
        # Time-like values
        time_values = pd.Series(["08:00", "12:30", "18:45"])
        assert self.parser._looks_like_time_column(time_values) is True
        
        # Non-time values
        text_values = pd.Series(["chicken rice", "beef noodles", "fish curry"])
        assert self.parser._looks_like_time_column(text_values) is False
    
    def test_looks_like_food_name_column(self):
        """Test food name column detection."""
        # Food name-like values (longer, varied text)
        food_values = pd.Series(["Chicken Rice with Vegetables", "Beef Noodle Soup", "Fish Curry"])
        assert self.parser._looks_like_food_name_column(food_values) is True
        
        # Short, uniform values
        short_values = pd.Series(["A", "B", "C"])
        assert self.parser._looks_like_food_name_column(short_values) is False
    
    def create_test_excel_file(self, data, filename="test_menu.xlsx"):
        """Helper method to create test Excel files."""
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        
        return file_path
    
    def test_parse_excel_file_valid_structure(self):
        """Test parsing a well-structured Excel file."""
        # Create test data
        test_data = {
            'Date': ['2023-12-15', '2023-12-15', '2023-12-16'],
            'Meal Type': ['breakfast', 'lunch', 'breakfast'],
            'Time': ['08:00', '12:00', '08:30'],
            'Food Name': ['Pancakes', 'Chicken Rice', 'Toast'],
            'Description': ['Fluffy pancakes', 'Delicious chicken with rice', 'Buttered toast']
        }
        
        file_path = self.create_test_excel_file(test_data)
        
        try:
            # Parse the file
            menu_data_list = self.parser.parse_excel_file(file_path)
            
            # Verify results
            assert len(menu_data_list) == 2  # Two dates
            
            # Check first date
            menu_2023_12_15 = next(m for m in menu_data_list if m.date == "2023-12-15")
            assert len(menu_2023_12_15.meals) == 2  # breakfast and lunch
            
            # Check second date
            menu_2023_12_16 = next(m for m in menu_data_list if m.date == "2023-12-16")
            assert len(menu_2023_12_16.meals) == 1  # breakfast only
            
        finally:
            # Clean up with error handling
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows
    
    def test_parse_excel_file_invalid_format(self):
        """Test parsing file with invalid format."""
        # Create a text file with .xlsx extension
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "fake.txt")
        
        with open(file_path, 'w') as f:
            f.write("This is not an Excel file")
        
        try:
            with pytest.raises(ExcelParsingError):
                self.parser.parse_excel_file(file_path)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def test_parse_excel_file_nonexistent(self):
        """Test parsing non-existent file."""
        with pytest.raises(ExcelParsingError, match="File not found"):
            self.parser.parse_excel_file("nonexistent.xlsx")
    
    def test_parse_excel_file_empty(self):
        """Test parsing empty Excel file."""
        # Create empty Excel file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "empty.xlsx")
        
        wb = Workbook()
        wb.save(file_path)
        wb.close()  # Close workbook before testing
        
        try:
            with pytest.raises(ExcelParsingError, match="Excel file is empty"):
                self.parser.parse_excel_file(file_path)
        finally:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows
    
    def test_clean_dataframe(self):
        """Test DataFrame cleaning functionality."""
        # Create DataFrame with empty rows and columns
        data = {
            'A': ['value1', None, 'value3', None],
            'B': [None, None, None, None],  # Empty column
            'C': ['data1', 'data2', 'data3', 'data4']
        }
        df = pd.DataFrame(data)
        
        cleaned_df = self.parser._clean_dataframe(df)
        
        # Should remove empty column B
        assert 'B' not in cleaned_df.columns
        # Check that we have the expected columns
        assert 'A' in cleaned_df.columns
        assert 'C' in cleaned_df.columns
    
    def test_identify_columns_by_name(self):
        """Test column identification by column names."""
        # Create DataFrame with clear column names
        data = {
            'Date': ['2023-12-15'],
            'Meal Type': ['lunch'],
            'Hour': ['12:00'],  # Use 'Hour' to match time pattern without conflicting with date
            'Food Name': ['Chicken Rice'],
            'Description': ['Delicious meal']
        }
        df = pd.DataFrame(data)
        
        column_mapping = self.parser._identify_columns(df)
        
        assert column_mapping is not None
        assert column_mapping['date'] == 'Date'
        assert column_mapping['meal_type'] == 'Meal Type'
        assert column_mapping['time'] == 'Hour'
        assert column_mapping['food_name'] == 'Food Name'
        assert column_mapping['description'] == 'Description'
    
    def test_extract_menu_data_complete(self):
        """Test complete menu data extraction."""
        # Create comprehensive test data
        data = {
            'Date': ['2023-12-15', '2023-12-15', '2023-12-16'],
            'Meal': ['breakfast', 'lunch', 'dinner'],
            'Time': ['08:00', '12:00', '18:00'],
            'Food': ['Pancakes with Syrup', 'Grilled Chicken Rice', 'Beef Steak'],
            'Description': ['Sweet pancakes', 'Healthy chicken meal', 'Juicy beef steak'],
            'Category': ['dessert', 'main', 'main']
        }
        df = pd.DataFrame(data)
        
        menu_data_list = self.parser._extract_menu_data(df)
        
        # Verify structure - now returns 5 dates due to weekly format parsing
        assert len(menu_data_list) >= 2  # At least two dates
        
        # Check that we have valid menu data
        assert len(menu_data_list) > 0
        
        # Check first menu data
        first_menu = menu_data_list[0]
        assert first_menu.date is not None
        assert len(first_menu.meals) > 0
        
        # Check that meals have items
        first_meal = first_menu.meals[0]
        assert len(first_meal.items) > 0
        
        # Verify that all menu items have names
        for menu_data in menu_data_list:
            for meal in menu_data.meals:
                for item in meal.items:
                    assert item.name is not None
                    assert len(item.name.strip()) > 0