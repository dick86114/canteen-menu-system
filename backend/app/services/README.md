# Excel 解析服务

Excel 解析服务提供解析包含食堂菜单数据的 Excel 文件并将其转换为结构化 `MenuData` 对象的功能。

## 功能特性

- **文件格式验证**: 验证上传的文件是否为 Excel 格式 (.xlsx, .xls)
- **灵活的列检测**: 通过名称模式或数据内容自动识别列
- **多语言支持**: 处理英文和中文列名及餐次类型
- **日期格式灵活性**: 支持多种日期格式，包括 ISO、美式、欧式和中文格式
- **健壮的错误处理**: 优雅地处理格式错误的数据并提供有意义的错误消息
- **数据验证**: 确保解析的数据符合系统的数据模型要求

## 使用方法

### 基本用法

```python
from app.services.excel_parser import ExcelParser, ExcelParsingError

# 初始化解析器
parser = ExcelParser()

# 解析 Excel 文件
try:
    menu_data_list = parser.parse_excel_file("path/to/menu.xlsx")
    for menu_data in menu_data_list:
        print(f"日期: {menu_data.date}")
        for meal in menu_data.meals:
            print(f"  {meal.type} 在 {meal.time}: {len(meal.items)} 个菜品")
except ExcelParsingError as e:
    print(f"解析失败: {e}")
```

### 文件格式验证

```python
# 检查文件格式是否支持
if parser.validate_file_format("menu.xlsx"):
    print("文件格式受支持")
else:
    print("不支持的文件格式")
```

## 支持的 Excel 结构

解析器可以处理各种 Excel 文件结构：

### 结构 1: 基于列的带标题格式
```
| Date       | Meal Type | Time  | Food Name        | Description      | Category |
|------------|-----------|-------|------------------|------------------|----------|
| 2023-12-15 | breakfast | 08:00 | Pancakes         | Fluffy pancakes  | dessert  |
| 2023-12-15 | lunch     | 12:00 | Chicken Rice     | Healthy meal     | main     |
```

### 结构 2: 中文标题格式
```
| 日期       | 餐次      | 时间  | 菜名             | 描述             | 类别     |
|------------|-----------|-------|------------------|------------------|----------|
| 2023-12-15 | 早餐      | 08:00 | 煎饼             | 美味煎饼         | 主食     |
| 2023-12-15 | 午餐      | 12:00 | 鸡肉饭           | 健康餐           | 主菜     |
```

### 结构 3: 最简格式（仅日期和菜名）
```
| Date       | Food Name        |
|------------|------------------|
| 2023-12-15 | Pancakes         |
| 2023-12-15 | Chicken Rice     |
```

## 列检测

解析器使用两阶段方法来识别列：

1. **基于名称的检测**: 在列名中查找常见模式
2. **基于内容的检测**: 当名称不清楚时分析数据内容

### 支持的列名模式

- **日期**: `date`, `日期`, `时间`, `time`
- **餐次类型**: `meal`, `type`, `餐次`, `类型`
- **时间**: `time`, `时间`, `hour`
- **菜品名称**: `food`, `name`, `菜名`, `食物`, `dish`
- **描述**: `desc`, `描述`, `说明`, `detail`
- **类别**: `category`, `类别`, `分类`, `cat`

## 日期格式支持

解析器支持多种日期格式：

- ISO 格式: `2023-12-15`
- 美式格式: `12/15/2023`
- 欧式格式: `15/12/2023`
- 中文格式: `2023年12月15日`
- 中文简写: `12月15日`

## 餐次类型映射

解析器规范化各种餐次类型表示：

- **早餐**: `breakfast`, `早餐`, `早饭`, `早点`, `morning`
- **午餐**: `lunch`, `午餐`, `午饭`, `中餐`, `noon`, `midday`
- **晚餐**: `dinner`, `晚餐`, `晚饭`, `晚点`, `evening`, `supper`

## 错误处理

解析器为不同的失败场景提供具体的错误消息：

- **文件未找到**: 当指定的文件不存在时
- **无效格式**: 当文件不是有效的 Excel 文件时
- **空文件**: 当 Excel 文件不包含数据时
- **缺少列**: 当无法识别必需的列（日期、菜品名称）时
- **无效数据**: 当数据不符合验证要求时

## 与文件扫描器集成

Excel 解析器与文件扫描器集成：

```python
# 在 file_scanner.py 中
from .excel_parser import ExcelParser, ExcelParsingError

parser = ExcelParser()
menu_data_list = parser.parse_excel_file(filepath)
```

## 性能考虑

- 解析器使用pandas在内存中处理文件
- 大文件（>16MB）被上传大小限制拒绝
- 列检测优化为仅检查前10行进行内容分析
- 格式错误的行被跳过而不是导致完全失败

## 测试

解析器包含全面的测试，涵盖：

- 文件格式验证
- 各种格式的日期解析
- 餐次类型规范化
- 列检测算法
- 错误处理场景
- 完整的文件解析工作流

运行测试：
```bash
python -m pytest tests/test_excel_parser.py -v
```

## 未来增强

未来版本的潜在改进：

- 支持单个Excel文件中的多个工作表
- 多个文件的批处理
- 自定义列映射配置
- 高级数据验证规则
- 对非常大文件的性能优化