# 🐳 Docker 部署指南

## 快速开始

### 1. 使用GitHub Container Registry镜像（推荐）

```bash
# 创建菜单文件目录
mkdir -p ./menu

# 运行容器
docker run -d \
  --name canteen-menu \
  -p 5000:5000 \
  -v $(pwd)/menu:/app/menu \
  --restart unless-stopped \
  ghcr.io/dick86114/canteen-menu-system:latest

# 访问系统
open http://localhost:5000
```

### 2. 使用Docker Hub镜像

```bash
# 创建菜单文件目录
mkdir -p ./menu

# 运行容器
docker run -d \
  --name canteen-menu \
  -p 5000:5000 \
  -v $(pwd)/menu:/app/menu \
  --restart unless-stopped \
  ghcr.io/dick86114/canteen-menu-system:latest

# 访问系统
open http://localhost:5000
```

### 3. 使用 Docker Compose

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  canteen-menu:
    image: ghcr.io/dick86114/canteen-menu-system:latest
    ports:
      - "5000:5000"
    volumes:
      - ./menu:/app/menu
    environment:
      - FLASK_ENV=production
      # 设置时区，可根据需要修改（如 America/New_York, Europe/London 等）
      - TZ=Asia/Shanghai
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

启动服务：
```bash
docker-compose up -d
```

## 菜单文件管理

### 添加菜单文件

1. 将Excel文件放入 `menu` 目录：
```bash
cp your-menu-file.xlsx ./menu/
```

2. 刷新菜单数据：
   - 方式1：重启容器 `docker restart canteen-menu`
   - 方式2：在界面点击"刷新菜单"按钮

### 支持的文件格式

- Excel文件 (.xlsx, .xls)
- 包含日期、餐次、菜品等信息
- 自动识别中文列名

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| FLASK_ENV | production | Flask运行环境 |
| FLASK_APP | app.py | Flask应用入口 |
| TZ | Asia/Shanghai | 时区设置 |

## 端口说明

- `5000`: Web服务端口

## 数据持久化

- `/app/menu`: 菜单文件目录（需要挂载）

## 健康检查

容器内置健康检查，检查API服务状态：
```bash
curl -f http://localhost:5000/api/health
```

## 日志查看

```bash
# 查看容器日志
docker logs canteen-menu

# 实时查看日志
docker logs -f canteen-menu

# Docker Compose 查看日志
docker-compose logs -f canteen-menu
```

## 故障排除

### 1. 容器无法启动

检查端口是否被占用：
```bash
netstat -tulpn | grep :5000
```

### 2. 菜单文件无法加载

检查文件权限和路径：
```bash
ls -la ./menu/
docker exec canteen-menu ls -la /app/menu/
```

### 3. 网络连接问题

检查容器网络：
```bash
docker network ls
docker inspect canteen-menu
```

### 4. 时区问题

如果发现时间显示不正确，可以设置正确的时区：
```bash
# 在docker-compose.yml中设置时区
environment:
  - TZ=Asia/Shanghai      # 中国标准时间
  - TZ=America/New_York   # 美国东部时间
  - TZ=Europe/London      # 英国时间
  - TZ=Asia/Tokyo         # 日本标准时间
```

常用时区列表：
- `Asia/Shanghai` - 中国标准时间 (UTC+8)
- `America/New_York` - 美国东部时间
- `Europe/London` - 英国时间
- `Asia/Tokyo` - 日本标准时间
- `UTC` - 协调世界时

## 更新镜像

```bash
# 停止容器
docker stop canteen-menu

# 删除容器
docker rm canteen-menu

# 拉取最新镜像
docker pull ghcr.io/dick86114/canteen-menu-system:latest

# 重新运行
docker run -d \
  --name canteen-menu \
  -p 5000:5000 \
  -v $(pwd)/menu:/app/menu \
  --restart unless-stopped \
  ghcr.io/dick86114/canteen-menu-system:latest
```

## 自定义构建

如需自定义构建：

```bash
# 克隆项目
git clone https://github.com/dick86114/canteen-menu-system.git
cd canteen-menu-system

# 构建镜像
docker build -t my-canteen-menu .

# 运行自定义镜像
docker run -d \
  --name canteen-menu \
  -p 5000:5000 \
  -v $(pwd)/menu:/app/menu \
  my-canteen-menu
```