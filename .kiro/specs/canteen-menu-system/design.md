# 设计文档 - 食堂菜单系统

## 概述

食堂菜单系统是一个全栈Web应用程序，使管理员能够上传包含每周菜单的Excel文件，并允许用户通过直观的基于日期的界面浏览每日菜单。该系统由用于用户交互的React前端和用于文件处理和数据管理的Flask后端组成。

## 架构

系统遵循客户端-服务器架构，具有清晰的关注点分离：

### 前端 (React)
- **用户界面层**: 用于文件上传、菜单显示和日期导航的React组件
- **状态管理**: 用于管理应用程序状态和API交互的React hooks
- **响应式设计**: 使用Bootstrap的CSS Grid/Flexbox实现跨设备兼容性

### 后端 (Flask)
- **API层**: 用于文件上传和菜单数据检索的RESTful端点
- **文件处理层**: 使用pandas和openpyxl进行Excel解析
- **数据层**: 内存存储，可选数据库持久化

### 通信
- **HTTP/REST API**: 前端和后端之间基于JSON的通信
- **文件上传**: 用于Excel文件传输的多部分表单数据

## 组件和接口

### 前端组件

#### 菜单上传组件 (MenuUpload)
- **目的**: 处理Excel文件选择和上传
- **属性**: onUploadSuccess回调函数
- **状态**: uploadStatus, selectedFile, uploadProgress
- **方法**: handleFileSelect(), uploadFile(), validateFile()

#### 菜单显示组件 (MenuDisplay)
- **目的**: 渲染包含食物项的每日菜单卡片
- **属性**: menuData, selectedDate
- **状态**: displayMode (card/list)
- **方法**: renderMenuCard(), formatMealTime(), groupByMealType()

#### 日期选择器组件 (DateSelector)
- **目的**: 提供日期导航和选择
- **属性**: selectedDate, onDateChange, availableDates
- **状态**: calendarVisible, dateRange
- **方法**: handleDateChange(), navigateDate(), checkDateAvailability()

#### 应用主组件 (App)
- **目的**: 主应用程序容器和状态管理
- **状态**: currentDate, menuData, uploadedFiles, loading
- **方法**: fetchMenuData(), handleDateChange(), handleUploadSuccess()

### 后端接口

#### 文件上传API
```python
POST /api/upload
Content-Type: multipart/form-data
Response: {
  "status": "success|error",
  "message": "string",
  "data": MenuData[]
}
```

#### 菜单检索API
```python
GET /api/menu?date=YYYY-MM-DD
Response: {
  "date": "YYYY-MM-DD",
  "meals": [
    {
      "type": "breakfast|lunch|dinner",
      "time": "HH:MM",
      "items": [
        {
          "name": "string",
          "description": "string",
          "category": "string"
        }
      ]
    }
  ]
}
```

#### 可用日期API
```python
GET /api/dates
Response: {
  "dates": ["YYYY-MM-DD"],
  "dateRange": {
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD"
  }
}
```

## 数据模型

### 菜单数据模型
```typescript
interface MenuData {
  date: string;           // ISO日期格式 YYYY-MM-DD
  meals: Meal[];
}

interface Meal {
  type: 'breakfast' | 'lunch' | 'dinner';
  time: string;           // HH:MM格式
  items: MenuItem[];
}

interface MenuItem {
  name: string;
  description?: string;
  category?: string;
  price?: number;
  order: number;          // 菜品在Excel中的顺序
  category_order: number; // 分类在Excel中的顺序
}
```

### Excel数据结构
支持多种Excel格式：

**标准列格式**:
- A列: 日期 (YYYY-MM-DD或可识别的日期格式)
- B列: 餐次类型 (breakfast/lunch/dinner)
- C列: 时间 (HH:MM)
- D列: 菜品名称
- E列: 描述
- F列: 类别 (可选)

**星期格式**:
- 第一列: 分类名称或菜品名称
- 后续列: 星期一、星期二、星期三等，包含对应日期的菜品
- 支持从文件名解析日期范围（如：12月29-31）
- 支持智能餐次推断（基于"类别"行出现次数）

**WPS表格格式(.et)**:
- 支持与Excel相同的数据结构
- 使用多种解析策略：pandas直接读取、xlrd引擎、格式转换、CSV方式
- 自动回退到兼容性最好的解析方法

### 存储模型
```python
class MenuStorage:
    def __init__(self):
        self.menu_data: Dict[str, List[Meal]] = {}
        self.uploaded_files: List[str] = []
    
    def store_menu_data(self, date: str, meals: List[Meal]) -> None
    def get_menu_by_date(self, date: str) -> Optional[List[Meal]]
    def get_available_dates(self) -> List[str]
    def clear_data(self) -> None

class MenuItem:
    """菜单项数据模型，包含排序信息"""
    def __init__(self, name: str, description: str = None, 
                 category: str = None, price: float = None,
                 order: int = 0, category_order: int = 0):
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.order = order              # 菜品在Excel中的顺序
        self.category_order = category_order  # 分类在Excel中的顺序
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于序列化时按顺序排序"""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'order': self.order,
            'category_order': self.category_order
        }
```

## 正确性属性

*属性是在系统的所有有效执行中应该保持为真的特征或行为——本质上是关于系统应该做什么的正式声明。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

基于预工作分析，已识别出以下正确性属性：

**属性 1: 文件格式验证一致性**
*对于任何*上传的文件，系统应当且仅当文件具有.xlsx扩展名时接受该文件，拒绝所有其他格式并显示适当的错误消息
**验证: 需求 1.1, 1.4, 5.1**

**属性 2: Excel解析完整性**
*对于任何*包含菜单数据的有效Excel文件，解析器应提取所有存在的数据字段（日期、菜品名称、描述、餐次类型）而不丢失
**验证: 需求 1.2**

**属性 3: 数据存储往返**
*对于任何*解析的菜单数据，存储然后检索数据应返回等效的菜单信息
**验证: 需求 1.3**

**属性 4: 文件大小限制执行**
*对于任何*文件上传尝试，超过大小限制的文件应被一致拒绝，无论内容或格式如何
**验证: 需求 1.5, 5.4**

**属性 5: 回退菜单选择**
*对于任何*没有菜单数据的日期，系统应显示存储数据中最近可用的菜单
**验证: 需求 2.2**

**属性 6: 菜单显示完整性**
*对于任何*有效的菜单数据，显示应在渲染输出中包含所有必需字段（菜品名称、描述、用餐时间）
**验证: 需求 2.3**

**属性 7: 空日期处理**
*对于任何*没有菜单数据的日期，系统应显示一致的"无可用数据"消息
**验证: 需求 2.4**

**属性 8: 餐次组织一致性**
*对于任何*包含多个餐次的菜单数据，显示应按餐次类型分组项目并按时间段排序
**验证: 需求 2.5**

**属性 9: 日期选择同步**
*对于任何*日期选择，菜单显示应更新以显示该特定日期的相应菜单数据
**验证: 需求 3.2**

**属性 10: 日期状态持久性**
*对于任何*用户会话期间的日期选择，所选日期应保持活动状态，直到用户明确更改
**验证: 需求 3.5**

**属性 11: Excel解析健壮性**
*对于任何*格式错误或损坏的Excel文件，解析器应优雅地处理错误而不会导致系统崩溃，并提供有意义的错误消息
**验证: 需求 5.2, 5.5**

**属性 12: UI样式一致性**
*对于任何*渲染的菜单卡片，样式类和排版应在所有卡片中一致应用
**验证: 需求 6.2**

**属性 13: WPS文件格式支持**
*对于任何*有效的.et格式文件，系统应能够使用多种解析策略成功提取菜单数据
**验证: 需求 7.1, 7.2, 7.3**

**属性 14: 菜单顺序保持**
*对于任何*解析的Excel文件，显示的分类和菜品顺序应与原始Excel表格中的顺序完全一致
**验证: 需求 8.1, 8.2, 8.3, 8.4**

**属性 15: 星期格式识别**
*对于任何*包含星期信息的Excel文件，系统应正确识别星期格式并映射到具体日期
**验证: 需求 9.1, 9.2**

**属性 16: 餐次智能推断**
*对于任何*缺少明确餐次标识的菜单文件，系统应基于"类别"行正确推断早餐、午餐、晚餐分组
**验证: 需求 9.3, 9.4**

**属性 17: 时区处理一致性**
*对于任何*日期和时间操作，系统应使用统一的时区处理避免时区偏移问题
**验证: 需求 10.1, 10.2, 10.3, 10.4**

## 错误处理

### 文件上传错误
- **无效格式**: 返回HTTP 400并附带描述性错误消息
- **文件过大**: 返回HTTP 413并附带大小限制信息
- **文件损坏**: 返回HTTP 422并附带解析错误详情
- **网络问题**: 实现指数退避的重试机制

### 数据处理错误
- **格式错误的Excel**: 记录错误详情，返回用户友好的消息
- **缺少必需列**: 验证结构，提供列映射指导
- **日期解析失败**: 使用回退日期格式，标记有问题的条目
- **空数据集**: 优雅处理，保持系统稳定性

### 前端错误处理
- **API失败**: 显示带有重试选项的错误通知
- **加载状态**: 在文件处理期间显示进度指示器
- **网络连接**: 检测离线状态，排队操作
- **无效用户输入**: 提供实时验证反馈

## 测试策略

### 双重测试方法

系统将采用单元测试和基于属性的测试来确保全面覆盖：

**单元测试**:
- 演示正确行为的具体示例
- 前端和后端组件之间的集成点
- 边界情况，如空文件、单日菜单、边界日期
- 错误条件和恢复场景

**基于属性的测试**:
- 应在所有输入中保持的通用属性
- 使用Hypothesis进行Python后端测试
- 使用fast-check进行JavaScript前端测试
- 每个基于属性的测试配置为运行最少100次迭代
- 每个测试标记格式：'**功能: canteen-menu-system, 属性 {编号}: {属性文本}**'

**测试框架选择**:
- **后端**: pytest配合Hypothesis进行基于属性的测试
- **前端**: Jest配合fast-check进行基于属性的测试
- **集成**: Cypress进行端到端测试场景

**基于属性的测试要求**:
- 每个正确性属性必须由单个基于属性的测试实现
- 测试必须引用相应的设计文档属性
- 每个属性测试最少100次迭代以确保统计置信度
- 智能生成器，智能约束输入空间（有效的Excel结构、现实的菜单数据）

### 测试数据生成

**Excel文件生成器**:
- 具有不同日期范围的有效菜单结构
- 缺少列或格式错误数据的文件
- 空文件和仅包含标题的文件
- 具有不同日期格式和餐次类型的文件

**菜单数据生成器**:
- 随机但现实的菜品名称和描述
- 各种餐次类型和时间组合
- 边界情况，如单餐或全天菜单
- 不同的日期范围和可用性模式

## 实现技术

### 前端技术栈
- **框架**: React 18配合TypeScript
- **样式**: Bootstrap 5配合自定义CSS模块
- **日期处理**: react-datepicker用于日期选择
- **HTTP客户端**: Axios用于API通信
- **状态管理**: React hooks (useState, useEffect, useContext)
- **构建工具**: Vite用于快速开发和构建

### 后端技术栈
- **框架**: Flask 2.3配合Python 3.9+
- **Excel处理**: pandas和openpyxl用于文件解析
- **文件处理**: Werkzeug用于安全文件上传
- **API文档**: Flask-RESTX用于OpenAPI文档
- **跨域**: Flask-CORS用于跨域请求
- **验证**: marshmallow用于请求/响应验证

### 开发工具
- **测试**: pytest (后端), Jest (前端)
- **属性测试**: Hypothesis (后端), fast-check (前端)
- **代码质量**: ESLint, Prettier (前端), Black, flake8 (后端)
- **类型检查**: TypeScript (前端), mypy (后端)

## 已实现的增强功能

### WPS表格文件支持
系统现已支持WPS Office创建的.et格式表格文件：
- **多策略解析**: 使用pandas直接读取、xlrd引擎、格式转换、CSV方式等多种策略
- **自动回退**: 当一种方法失败时自动尝试其他解析方法
- **兼容性**: 与Excel文件保持相同的数据完整性和解析逻辑

### 时区处理系统
实现了统一的时区处理机制：
- **Docker环境变量**: 支持TZ环境变量配置时区（默认Asia/Shanghai）
- **统一时区工具**: 创建了`backend/app/utils/timezone.py`模块
- **前端时区修复**: 修复了月历日期标记错位问题

### 智能Excel解析
增强了Excel文件解析能力：
- **星期格式支持**: 自动识别基于星期的菜单格式
- **智能餐次推断**: 基于"类别"行数量自动推断早餐、午餐、晚餐
- **分类延续机制**: 正确处理跨多行的分类数据
- **顺序保持**: 完全按照Excel表格中的原始顺序显示分类和菜品

### 改进的分类识别
实现了更智能的分类识别算法：
- **已知分类白名单**: 预定义常见分类名称
- **智能特征识别**: 基于长度、关键词等特征判断分类
- **NaN值处理**: 正确处理pandas的空值，保持分类连续性