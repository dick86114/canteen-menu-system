# 🤝 贡献指南

感谢你对食堂菜单系统的关注！我们欢迎各种形式的贡献。

## 🚀 如何贡献

### 报告问题

如果你发现了bug或有功能建议：

1. 检查 [Issues](../../issues) 确保问题未被报告
2. 创建新的Issue，包含：
   - 清晰的标题和描述
   - 重现步骤（如果是bug）
   - 期望的行为
   - 实际的行为
   - 环境信息（操作系统、浏览器等）

### 提交代码

1. **Fork项目**
   ```bash
   # 点击GitHub页面右上角的Fork按钮
   ```

2. **克隆你的Fork**
   ```bash
   git clone https://github.com/你的用户名/canteen-menu-system.git
   cd canteen-menu-system
   ```

3. **创建功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **设置开发环境**
   ```bash
   # 后端
   cd backend
   python setup_venv.py
   python app.py
   
   # 前端
   cd frontend
   npm install
   npm run dev
   ```

5. **进行更改**
   - 遵循现有的代码风格
   - 添加必要的测试
   - 更新文档

6. **运行测试**
   ```bash
   # 后端测试
   cd backend
   python -m pytest tests/ -v
   
   # 前端测试
   cd frontend
   npm test
   ```

7. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加令人惊叹的功能"
   ```

8. **推送到你的Fork**
   ```bash
   git push origin feature/amazing-feature
   ```

9. **创建Pull Request**
   - 访问你的Fork页面
   - 点击"New Pull Request"
   - 填写详细的描述

## 📝 代码规范

### 前端 (React/TypeScript)

- 使用TypeScript严格模式
- 遵循ESLint配置
- 组件使用函数式组件和Hooks
- 使用有意义的变量和函数名
- 添加适当的注释

```typescript
// 好的例子
const MenuDisplay: React.FC<MenuDisplayProps> = ({ menuData, selectedDate }) => {
  const [loading, setLoading] = useState<boolean>(false);
  
  // 处理菜单数据加载
  const handleMenuLoad = useCallback(async () => {
    // 实现逻辑
  }, [selectedDate]);
  
  return (
    <div className="menu-display">
      {/* 组件内容 */}
    </div>
  );
};
```

### 后端 (Python/Flask)

- 遵循PEP 8规范
- 使用类型提示
- 添加文档字符串
- 使用有意义的变量和函数名

```python
def parse_excel_file(file_path: str) -> List[MenuData]:
    """
    解析Excel文件并提取菜单数据
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        菜单数据列表
        
    Raises:
        ValueError: 当文件格式不正确时
    """
    # 实现逻辑
    pass
```

## 🧪 测试指南

### 前端测试

- 为新组件添加单元测试
- 使用React Testing Library
- 测试用户交互和边界情况

```typescript
describe('MenuDisplay组件', () => {
  test('应该正确显示菜单数据', () => {
    render(<MenuDisplay menuData={mockData} selectedDate="2024-01-01" />);
    expect(screen.getByText('早餐')).toBeInTheDocument();
  });
});
```

### 后端测试

- 为新API端点添加测试
- 使用pytest框架
- 测试正常情况和错误情况

```python
def test_get_menu_by_date():
    """测试根据日期获取菜单"""
    response = client.get('/api/menu?date=2024-01-01')
    assert response.status_code == 200
    assert 'meals' in response.json
```

## 📚 文档

- 更新README.md（如果需要）
- 为新功能添加使用说明
- 更新API文档
- 保持中文文档的准确性

## 🎯 提交消息规范

使用约定式提交格式：

```
<类型>[可选范围]: <描述>

[可选正文]

[可选脚注]
```

类型：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 添加测试
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(menu): 添加菜单搜索功能

添加了按菜品名称搜索的功能，支持模糊匹配。

Closes #123
```

## 🔄 发布流程

1. 更新版本号
2. 更新CHANGELOG.md
3. 创建Git标签
4. 构建Docker镜像
5. 发布到Docker Hub

## 📞 获取帮助

如果你需要帮助：

1. 查看现有的[Issues](../../issues)和[Discussions](../../discussions)
2. 创建新的Discussion
3. 联系维护者

## 🙏 致谢

感谢所有贡献者的努力！你的贡献让这个项目变得更好。

---

再次感谢你的贡献！🎉