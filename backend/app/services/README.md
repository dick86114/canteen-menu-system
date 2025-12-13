# Excel Parser Service

The Excel Parser service provides functionality to parse Excel files containing canteen menu data and convert them into structured `MenuData` objects.

## Features

- **File Format Validation**: Validates that uploaded files are Excel format (.xlsx, .xls)
- **Flexible Column Detection**: Automatically identifies columns by name patterns or data content
- **Multi-language Support**: Handles both English and Chinese column names and meal types
- **Date Format Flexibility**: Supports various date formats including ISO, US, European, and Chinese formats
- **Robust Error Handling**: Gracefully handles malformed data and provides meaningful error messages
- **Data Validation**: Ensures parsed data meets the system's data model requirements

## Usage

### Basic Usage

```python
from app.services.excel_parser import ExcelParser, ExcelParsingError

# Initialize parser
parser = ExcelParser()

# Parse Excel file
try:
    menu_data_list = parser.parse_excel_file("path/to/menu.xlsx")
    for menu_data in menu_data_list:
        print(f"Date: {menu_data.date}")
        for meal in menu_data.meals:
            print(f"  {meal.type} at {meal.time}: {len(meal.items)} items")
except ExcelParsingError as e:
    print(f"Parsing failed: {e}")
```

### File Format Validation

```python
# Check if file format is supported
if parser.validate_file_format("menu.xlsx"):
    print("File format is supported")
else:
    print("Unsupported file format")
```

## Supported Excel Structures

The parser can handle various Excel file structures:

### Structure 1: Column-based with Headers
```
| Date       | Meal Type | Time  | Food Name        | Description      | Category |
|------------|-----------|-------|------------------|------------------|----------|
| 2023-12-15 | breakfast | 08:00 | Pancakes         | Fluffy pancakes  | dessert  |
| 2023-12-15 | lunch     | 12:00 | Chicken Rice     | Healthy meal     | main     |
```

### Structure 2: Chinese Headers
```
| 日期       | 餐次      | 时间  | 菜名             | 描述             | 类别     |
|------------|-----------|-------|------------------|------------------|----------|
| 2023-12-15 | 早餐      | 08:00 | 煎饼             | 美味煎饼         | 主食     |
| 2023-12-15 | 午餐      | 12:00 | 鸡肉饭           | 健康餐           | 主菜     |
```

### Structure 3: Minimal (Date and Food Name only)
```
| Date       | Food Name        |
|------------|------------------|
| 2023-12-15 | Pancakes         |
| 2023-12-15 | Chicken Rice     |
```

## Column Detection

The parser uses a two-stage approach to identify columns:

1. **Name-based Detection**: Looks for common patterns in column names
2. **Content-based Detection**: Analyzes data content when names are unclear

### Supported Column Name Patterns

- **Date**: `date`, `日期`, `时间`, `time`
- **Meal Type**: `meal`, `type`, `餐次`, `类型`
- **Time**: `time`, `时间`, `hour`
- **Food Name**: `food`, `name`, `菜名`, `食物`, `dish`
- **Description**: `desc`, `描述`, `说明`, `detail`
- **Category**: `category`, `类别`, `分类`, `cat`

## Date Format Support

The parser supports multiple date formats:

- ISO format: `2023-12-15`
- US format: `12/15/2023`
- European format: `15/12/2023`
- Chinese format: `2023年12月15日`
- Short Chinese: `12月15日`

## Meal Type Mapping

The parser normalizes various meal type representations:

- **Breakfast**: `breakfast`, `早餐`, `早饭`, `早点`, `morning`
- **Lunch**: `lunch`, `午餐`, `午饭`, `中餐`, `noon`, `midday`
- **Dinner**: `dinner`, `晚餐`, `晚饭`, `晚点`, `evening`, `supper`

## Error Handling

The parser provides specific error messages for different failure scenarios:

- **File not found**: When the specified file doesn't exist
- **Invalid format**: When the file is not a valid Excel file
- **Empty file**: When the Excel file contains no data
- **Missing columns**: When required columns (date, food name) cannot be identified
- **Invalid data**: When data doesn't meet validation requirements

## Integration with Upload API

The Excel parser is integrated with the upload API endpoint:

```python
# In upload.py
from ..services.excel_parser import ExcelParser, ExcelParsingError

parser = ExcelParser()
menu_data_list = parser.parse_excel_file(filepath)
```

## Performance Considerations

- The parser processes files in memory using pandas
- Large files (>16MB) are rejected by the upload size limit
- Column detection is optimized to check only the first 10 rows for content analysis
- Malformed rows are skipped rather than causing complete failure

## Testing

The parser includes comprehensive tests covering:

- File format validation
- Date parsing with various formats
- Meal type normalization
- Column detection algorithms
- Error handling scenarios
- Complete file parsing workflows

Run tests with:
```bash
python -m pytest tests/test_excel_parser.py -v
```

## Future Enhancements

Potential improvements for future versions:

- Support for multiple sheets in a single Excel file
- Batch processing of multiple files
- Custom column mapping configuration
- Advanced data validation rules
- Performance optimization for very large files