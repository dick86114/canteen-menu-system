# 🍽️ 食堂菜单系统

[![Docker Build](https://github.com/dick86114/canteen-menu-system/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/dick86114/canteen-menu-system/actions/workflows/docker-publish.yml)
[![GitHub release](https://img.shields.io/github/release/dick86114/canteen-menu-system.svg)](https://github.com/dick86114/canteen-menu-system/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个现代化的食堂菜单管理和展示系统，支持自动扫描Excel文件和响应式菜单展示。

## 🆕 新功能特性

- 📁 **自动文件扫描** - 系统启动时自动扫描 `menu` 目录下的Excel文件
- 🔄 **一键刷新** - 点击"刷新菜单"按钮重新扫描文件
- 📂 **无需手动上传** - 将Excel文件放入 `menu` 目录即可自动加载
- 📅 日期导航和菜单查看
- 📱 响应式设计，支持移动设备
- 🎨 现代化UI设计
- 🌐 中文界面支持

## 使用方法

### 方式一：自动扫描（推荐）
1. 将Excel菜单文件放入项目根目录的 `menu` 文件夹
2. 启动系统，会自动扫描并加载所有Excel文件
3. 点击导航栏的"刷新菜单"按钮可重新扫描文件

### 方式二：手动上传
1. 访问系统界面
2. 点击"上传文件"按钮
3. 选择Excel文件上传

## 技术栈

### 前端
- React 18 + TypeScript
- Bootstrap 5 + Bootstrap Icons
- Axios (HTTP客户端)
- Vite (构建工具)

### 后端
- Flask + Flask-RESTX
- pandas + openpyxl (Excel处理)
- Python 3.11+

## 🚀 快速开始

### 🐳 Docker 部署（推荐）

**使用 GitHub Container Registry 镜像（推荐）**
```bash
# 1. 创建菜单文件目录
mkdir -p ./menu

# 2. 运行容器
docker run -d \
  --name canteen-menu \
  -p 5000:5000 \
  -v $(pwd)/menu:/app/menu \
  -e TZ=Asia/Shanghai \
  --restart unless-stopped \
  ghcr.io/dick86114/canteen-menu-system:latest

# 3. 访问系统
# 打开浏览器访问 http://localhost:5000
```

> 🔗 **GitHub Packages**: [ghcr.io/dick86114/canteen-menu-system](https://github.com/dick86114/canteen-menu-system/pkgs/container/canteen-menu-system)

**使用 Docker Compose**
```bash
# 1. 下载配置文件
wget https://raw.githubusercontent.com/dick86114/canteen-menu-system/main/compose.yaml

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f canteen-menu
```

**自己构建镜像**
```bash
# 1. 克隆项目
git clone https://github.com/dick86114/canteen-menu-system.git
cd canteen-menu-system

# 2. 构建镜像
docker build -t canteen-menu-system .

# 3. 运行容器
docker run -d \
  --name canteen-menu \
  -p 5000:5000 \
  -v $(pwd)/menu:/app/menu \
  -e TZ=Asia/Shanghai \
  canteen-menu-system
```

### 📁 菜单文件管理

将Excel菜单文件放入 `menu` 目录：
```bash
# 复制菜单文件到menu目录
cp your-menu-file.xlsx ./menu/

# 重启容器以重新扫描文件
docker restart canteen-menu

# 或者通过界面点击"刷新菜单"按钮
```

### 🌍 时区配置

系统支持自定义时区设置，确保时间显示正确：

```bash
# 设置中国标准时间（默认）
docker run -e TZ=Asia/Shanghai ...

# 设置美国东部时间
docker run -e TZ=America/New_York ...

# 设置欧洲伦敦时间
docker run -e TZ=Europe/London ...

# 设置日本标准时间
docker run -e TZ=Asia/Tokyo ...
```

**Docker Compose 时区配置：**
```yaml
environment:
  - TZ=Asia/Shanghai  # 根据需要修改时区
```

### 💻 本地开发部署

#### 环境要求
- Node.js 16+
- Python 3.11+
- npm 或 yarn

#### 安装和运行

1. **克隆项目**
```bash
git clone https://github.com/dick86114/canteen-menu-system.git
cd canteen-menu-system
```

2. **准备菜单文件**
```bash
# 将Excel菜单文件放入menu目录
mkdir menu  # 如果不存在
# 复制你的Excel文件到menu目录
```

3. **后端设置**
```bash
cd backend
python setup_venv.py  # 创建虚拟环境并安装依赖
python app.py          # 启动后端服务 (http://localhost:5000)
```

4. **前端设置**
```bash
cd frontend
npm install            # 安装依赖
npm run dev           # 启动开发服务器 (http://localhost:3001)
```

5. **访问系统**
- 打开浏览器访问 http://localhost:3001
- 系统会自动扫描并加载menu目录下的Excel文件
- 如果没有文件，可以使用上传功能

## Excel文件格式要求

支持的文件格式：
- Excel文件 (.xlsx, .xls)
- WPS表格文件 (.et)
- CSV文件 (.csv)
- 包含日期、餐次、时间、菜品名称等列
- 支持中文列名
- 自动识别列结构

示例列名：
- 日期：`日期`、`Date`
- 餐次：`餐次`、`Meal`、`早餐`、`午餐`、`晚餐`
- 时间：`时间`、`Time`
- 菜品：`菜品`、`Food`、`菜名`

## API文档

### 主要端点

- `GET /api/health` - 健康检查
- `GET /api/scanner/auto-load` - 自动扫描并加载菜单文件
- `POST /api/scanner/scan` - 手动扫描菜单文件
- `GET /api/scanner/status` - 获取扫描状态
- `POST /api/upload` - 上传Excel文件
- `GET /api/menu?date=YYYY-MM-DD` - 获取指定日期菜单
- `GET /api/dates` - 获取可用日期列表

### 新增扫描API

**自动加载菜单文件**
```bash
GET /api/scanner/auto-load
```

**手动扫描菜单文件**
```bash
POST /api/scanner/scan
```

**获取扫描状态**
```bash
GET /api/scanner/status
```

响应示例：
```json
{
  "success": true,
  "message": "成功加载 2/2 个文件，共 10 天菜单",
  "loaded_files": [
    {
      "file": "菜单文件.xlsx",
      "menus_count": 5,
      "dates": ["2025-12-08", "2025-12-09", "2025-12-10", "2025-12-11", "2025-12-12"]
    }
  ],
  "failed_files": [],
  "total_menus": 10
}
```

## 开发

### 运行测试

**后端测试**
```bash
cd backend
python -m pytest tests/ -v
```

**前端测试**
```bash
cd frontend
npm test
```

### 代码格式化

**后端**
```bash
cd backend
python -m black app/
python -m flake8 app/
```

**前端**
```bash
cd frontend
npm run lint
```

## 部署

### 生产构建

**前端**
```bash
cd frontend
npm run build
```

**后端**
```bash
cd backend
# 配置生产环境变量
export FLASK_ENV=production
python app.py
```

## 项目结构

```
canteen-menu-system/
├── frontend/                 # React TypeScript 前端
│   ├── src/
│   │   ├── components/      # React 组件
│   │   ├── services/        # API 服务
│   │   └── types/          # TypeScript 类型定义
│   ├── public/             # 静态资源
│   └── package.json        # 前端依赖
├── backend/                 # Flask Python 后端
│   ├── app/
│   │   ├── api/            # API 端点
│   │   ├── models/         # 数据模型
│   │   └── services/       # 业务逻辑
│   ├── tests/              # 后端测试
│   └── requirements.txt    # Python 依赖
└── menu/                   # 菜单文件目录（自动扫描）
    ├── 省投食堂菜单；12月15-19.xlsx
    └── 省投食堂菜单；12月8-12.xlsx
```

## 贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如有问题或建议，请创建 [Issue](../../issues)。