# 🚀 部署指南

## Docker Hub 发布步骤

### 1. 准备工作

确保已安装：
- Docker Desktop
- Node.js 18+
- Git

### 2. 构建镜像

```bash
# 1. 克隆项目
git clone <your-repository-url>
cd canteen-menu-system

# 2. 构建前端
cd frontend
npm ci
npm run build
cd ..

# 3. 构建Docker镜像
docker build -t your-dockerhub-username/canteen-menu-system:latest .

# 4. 测试镜像
docker run -d --name test-canteen -p 5000:5000 your-dockerhub-username/canteen-menu-system:latest

# 5. 测试访问
curl http://localhost:5000/api/health

# 6. 停止测试容器
docker stop test-canteen
docker rm test-canteen
```

### 3. 发布到Docker Hub

```bash
# 1. 登录Docker Hub
docker login

# 2. 推送镜像
docker push your-dockerhub-username/canteen-menu-system:latest

# 3. 添加版本标签
docker tag your-dockerhub-username/canteen-menu-system:latest your-dockerhub-username/canteen-menu-system:v1.0.0
docker push your-dockerhub-username/canteen-menu-system:v1.0.0
```

### 4. 使用自动化脚本

**Linux/macOS:**
```bash
chmod +x build-and-push.sh
./build-and-push.sh
```

**Windows:**
```cmd
build-and-push.bat
```

## Docker Hub 页面配置

### 镜像描述

```markdown
# 🍽️ 食堂菜单系统

现代化的食堂菜单管理和展示系统，支持Excel文件自动扫描和响应式菜单展示。

## 特性

- 📅 智能日期选择 - 直观的月历界面
- 📱 响应式设计 - 完美适配移动端
- 📊 Excel文件支持 - 自动扫描和解析
- 🔄 实时刷新 - 一键刷新菜单数据
- 🎯 简洁界面 - 专注菜单展示

## 快速开始

```bash
# 创建菜单目录
mkdir -p ./menu

# 运行容器
docker run -d \
  --name canteen-menu \
  -p 5000:5000 \
  -v $(pwd)/menu:/app/menu \
  --restart unless-stopped \
  your-dockerhub-username/canteen-menu-system

# 访问系统
open http://localhost:5000
```

## 菜单文件管理

将Excel菜单文件放入挂载的 `menu` 目录，系统会自动扫描和加载。

## 文档

- [完整文档](https://github.com/your-repo/canteen-menu-system)
- [Docker部署指南](https://github.com/your-repo/canteen-menu-system/blob/main/DOCKER.md)
```

### 标签建议

- `canteen`
- `menu`
- `restaurant`
- `food`
- `excel`
- `flask`
- `react`
- `typescript`
- `responsive`
- `chinese`

## 用户使用指南

### 基本使用

1. **运行容器**
```bash
docker run -d \
  --name canteen-menu \
  -p 5000:5000 \
  -v $(pwd)/menu:/app/menu \
  your-dockerhub-username/canteen-menu-system
```

2. **添加菜单文件**
```bash
# 将Excel文件复制到menu目录
cp your-menu.xlsx ./menu/
```

3. **刷新菜单**
- 访问 http://localhost:5000
- 点击"刷新菜单"按钮

### 高级配置

**使用Docker Compose:**

```yaml
version: '3.8'
services:
  canteen-menu:
    image: your-dockerhub-username/canteen-menu-system:latest
    ports:
      - "5000:5000"
    volumes:
      - ./menu:/app/menu
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
```

**反向代理配置 (Nginx):**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 维护和更新

### 更新镜像

```bash
# 停止容器
docker stop canteen-menu

# 删除容器
docker rm canteen-menu

# 拉取最新镜像
docker pull your-dockerhub-username/canteen-menu-system:latest

# 重新运行
docker run -d \
  --name canteen-menu \
  -p 5000:5000 \
  -v $(pwd)/menu:/app/menu \
  --restart unless-stopped \
  your-dockerhub-username/canteen-menu-system:latest
```

### 备份数据

```bash
# 备份菜单文件
tar -czf menu-backup-$(date +%Y%m%d).tar.gz menu/
```

### 监控和日志

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs canteen-menu

# 实时日志
docker logs -f canteen-menu

# 进入容器
docker exec -it canteen-menu /bin/bash
```

## 故障排除

### 常见问题

1. **端口被占用**
```bash
# 检查端口使用
netstat -tulpn | grep :5000
# 或使用其他端口
docker run -p 8080:5000 ...
```

2. **菜单文件无法读取**
```bash
# 检查文件权限
ls -la ./menu/
# 修改权限
chmod 644 ./menu/*.xlsx
```

3. **容器无法启动**
```bash
# 查看详细错误
docker logs canteen-menu
```

## 性能优化

### 生产环境建议

1. **使用具体版本标签**
```bash
docker run ... your-dockerhub-username/canteen-menu-system:v1.0.0
```

2. **设置资源限制**
```bash
docker run --memory=512m --cpus=1 ...
```

3. **使用健康检查**
```bash
docker run --health-cmd="curl -f http://localhost:5000/api/health" ...
```

4. **配置日志轮转**
```bash
docker run --log-driver=json-file --log-opt max-size=10m --log-opt max-file=3 ...
```