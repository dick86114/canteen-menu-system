# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个食堂菜单管理和展示系统，采用前后端分离架构，支持自动扫描 Excel 文件并展示菜单。

### 技术栈
- **前端**: React 18 + TypeScript + Vite + Bootstrap 5
- **后端**: Flask 2.3.3 + Flask-RESTX + pandas
- **Excel处理**: pandas + openpyxl + xlrd
- **部署**: Docker + Docker Compose

---

## 常用命令

### 前端开发 (frontend/ 目录)
```bash
pnpm install              # 安装依赖 (使用 pnpm)
pnpm run dev             # 启动开发服务器 (http://localhost:3000)
pnpm run build           # 生产构建
pnpm run lint            # ESLint 检查
pnpm run lint:fix        # ESLint 自动修复
pnpm run format          # Prettier 格式化
pnpm run format:check    # Prettier 检查
pnpm test                # 运行测试
pnpm test:coverage       # 测试覆盖率
```

### 后端开发 (backend/ 目录)
```bash
python setup_venv.py     # 创建虚拟环境并安装依赖
python app.py            # 启动开发服务器 (http://localhost:5000)
python startup.py        # 启动生产服务器（带数据加载）

# 测试
python -m pytest tests/ -v                # 运行测试
python -m pytest tests/ --cov=app         # 测试覆盖率

# 代码质量
python -m black app/                      # 格式化代码
python -m flake8 app/                     # 代码检查
python -m mypy app/                       # 类型检查
```

### Docker 部署
```bash
docker build -t canteen-menu-system .              # 构建镜像
docker run -d -p 1214:5000 -v $(pwd)/menu:/app/menu canteen-menu-system
docker-compose up -d                               # 使用 Docker Compose 启动
```

---

## 代码架构

### 项目结构
```
mtMenu/
├── frontend/                 # React TypeScript 前端
│   └── src/
│       ├── components/      # UI 组件（MenuDisplay, DateSelector 等）
│       ├── services/        # API 服务层
│       ├── types/           # TypeScript 类型定义
│       └── hooks/           # 自定义 React Hooks
├── backend/                 # Flask Python 后端
│   ├── app/
│   │   ├── api/            # API 蓝图（menu, health, scanner）
│   │   ├── models/         # 数据模型（menu, storage）
│   │   ├── services/       # 业务逻辑（Excel 解析、文件扫描、餐次识别）
│   │   └── utils/          # 工具函数（时区处理）
│   └── static/             # 生产构建后的前端静态文件
└── menu/                   # 菜单 Excel 文件存放目录
```

### 核心架构设计

#### 1. 前后端分离架构
- 前端独立开发使用 Vite 开发服务器（端口 3000）
- 后端 Flask API 服务（端口 5000）
- 生产环境：前端构建到 `backend/static/`，由 Flask 统一服务

#### 2. Flask 应用工厂模式
- [app/__init__.py](backend/app/__init__.py) 中的 `create_app()` 函数创建应用实例
- 支持 development 和 production 两种配置环境
- 应用启动时自动调用 `auto_load_menu_data()` 扫描 `menu/` 目录
- 静态文件路由优先级高于 API 路由

#### 3. 数据流设计
- **数据源**: `menu/` 目录下的 Excel 文件（.xlsx, .xls, .et, .csv）
- **扫描器**: [app/services/file_scanner.py](backend/app/services/file_scanner.py) 自动扫描文件
- **解析器**: [app/services/excel_parser.py](backend/app/services/excel_parser.py) 解析 Excel 数据
- **餐次识别**: [app/services/meal_segment_identifier.py](backend/app/services/meal_segment_identifier.py) 识别餐次分类
- **存储**: [app/models/storage.py](backend/app/models/storage.py) 内存存储（单例模式）
- **API**: [app/api/menu.py](backend/app/api/menu.py) RESTful API 端点

#### 4. 前端状态管理
- 组件级状态管理，未使用 Redux 等全局状态库
- API 调用集中在 [src/services/api.ts](frontend/src/services/api.ts)
- 错误边界处理：[src/components/ErrorBoundary.tsx](frontend/src/components/ErrorBoundary.tsx)
- 网络状态监控：[src/hooks/useNetworkStatus.ts](frontend/src/hooks/useNetworkStatus.ts)

#### 5. CORS 配置
- 开发环境：允许 `localhost:3000` 和 `localhost:3001`
- 生产环境：允许所有来源 (`origins="*"`)
- 在 [app/__init__.py](backend/app/__init__.py:24-27) 中配置

---

## 重要开发注意事项

### 1. 静态文件服务路由优先级
Flask 路由注册顺序很重要，在 [app/__init__.py](backend/app/__init__.py) 中：
- 根路径 `/` 和静态资源路由必须在 API 蓝图注册**之前**
- SPA 路由回退必须在**最后**
- 确保前端构建文件正确生成到 `backend/static/`

### 2. 数据自动加载机制
应用启动时会自动检查是否有菜单数据：
- 如果无数据，自动扫描 `menu/` 目录
- 如果已有数据，跳过扫描
- 手动刷新调用 `/api/scanner/refresh` 端点

### 3. Excel 文件格式
系统支持灵活的 Excel 格式：
- 支持中文列名（日期、餐次、菜品等）
- 自动识别列结构
- 横向格式菜单（档口特色标记）
- 多餐次支持（早餐、午餐、晚餐）

### 4. 生产构建流程
```bash
# 1. 构建前端
cd frontend && pnpm run build

# 2. 复制到后端静态目录
#（构建脚本自动处理，前端构建到 frontend/dist，后端配置指向 backend/static）

# 3. 启动后端（会自动服务前端静态文件）
cd backend && python app.py
```

### 5. 时区处理
- 使用 `TZ` 环境变量配置时区（默认 `Asia/Shanghai`）
- 时区处理工具：[app/utils/timezone.py](backend/app/utils/timezone.py)
- Docker 部署时通过 `-e TZ=Asia/Shanghai` 配置

---

## API 端点说明

### 主要端点
- `GET /api/health` - 健康检查
- `GET /api/menu?date=YYYY-MM-DD` - 获取指定日期菜单
- `GET /api/dates` - 获取所有可用日期
- `GET /api/scanner/auto-load` - 自动扫描并加载菜单
- `POST /api/scanner/scan` - 手动触发扫描
- `GET /api/scanner/status` - 获取扫描状态
- `POST /api/scanner/refresh` - 刷新菜单（清除缓存后重新扫描）
- `GET /api/docs/` - Swagger API 文档

### API 文档
Flask-RESTX 提供的交互式 API 文档：`http://localhost:5000/api/docs/`

---

## 环境变量配置

创建 `backend/.env` 文件：
```
FLASK_ENV=production        # development 或 production
TZ=Asia/Shanghai           # 时区配置
```

---

## 测试策略

### 后端测试
- 框架：pytest
- 覆盖率：pytest-cov
- 属性测试：hypothesis
- 测试文件位于 [backend/tests/](backend/tests/)

### 前端测试
- 框架：Jest + React Testing Library
- 属性测试：fast-check
- 测试文件与组件同目录（`.test.tsx` 或 `.spec.tsx`）

---

## Docker 部署要点

### 多阶段构建
1. **前端构建阶段**: Node.js 18 Alpine 镜像，构建前端资源
2. **后端运行阶段**: Python 3.11 Slim 镜像，复制前端构建产物并运行 Flask

### 端口映射
- 容器内部：5000
- 宿主机：1214（通过 compose.yaml 配置）

### 数据持久化
```bash
-v $(pwd)/menu:/app/menu    # 挂载菜单文件目录
```

### 健康检查
- 端点：`/api/health`
- 间隔：30 秒
- 重启策略：`unless-stopped`

---

## 常见问题排查

### 前端无法连接后端
- 检查 CORS 配置（[app/__init__.py](backend/app/__init__.py:24-27)）
- 检查 Vite 代理配置（[frontend/vite.config.ts](frontend/vite.config.ts)）
- 确认后端运行在端口 5000

### 静态文件 404
- 确认前端已构建：`pnpm run build`
- 检查 `backend/static/` 目录是否存在 `index.html`
- 查看 Flask 路由注册顺序

### 菜单数据未加载
- 检查 `menu/` 目录是否有 Excel 文件
- 查看应用启动日志中的自动加载信息
- 调用 `/api/scanner/status` 检查扫描状态
- 手动触发 `/api/scanner/refresh`

### Docker 容器重启后数据丢失
- 确保使用了 `-v $(pwd)/menu:/app/menu` 挂载菜单目录
- 菜单数据存储在内存中，容器重启后会自动重新扫描

---

## 开发规范

### 前端
- 使用 TypeScript 严格模式
- 遵循 React Hooks 最佳实践
- 组件使用函数式组件
- 样式使用 Bootstrap 5 类名

### 后端
- 遵循 PEP 8 代码规范
- 使用类型注解
- API 端点使用 Blueprint 组织
- 数据验证使用 marshmallow

### Git 提交
- 使用中文提交信息
- 遵循 Conventional Commits 规范（feat, fix, docs 等）
