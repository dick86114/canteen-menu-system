# 📦 GitHub Container Registry (GHCR) 设置指南

## 🚀 自动构建和发布

项目已配置GitHub Actions自动构建和发布Docker镜像到GHCR。

### 触发条件

1. **推送到main分支** - 自动构建并推送 `latest` 标签
2. **创建Release** - 自动构建并推送版本标签
3. **手动触发** - 在Actions页面手动运行工作流

### 镜像标签策略

- `latest` - 最新的main分支构建
- `v1.0.0` - 具体版本号
- `main-abc1234` - 分支名+commit SHA

## 🔧 仓库设置

### 1. 启用GitHub Packages

1. 进入仓库 Settings > General
2. 滚动到 "Features" 部分
3. 确保 "Packages" 已启用

### 2. 设置包可见性

1. 进入仓库 Packages 页面
2. 点击包名进入包详情
3. 在 "Package settings" 中设置可见性：
   - **Public** - 任何人都可以拉取
   - **Private** - 只有仓库协作者可以拉取

### 3. 配置包权限

在包设置页面可以：
- 添加协作者
- 设置访问权限
- 管理包版本

## 📥 拉取镜像

### 公开镜像

```bash
# 拉取最新版本
docker pull ghcr.io/dick86114/canteen-menu-system:latest

# 拉取特定版本
docker pull ghcr.io/dick86114/canteen-menu-system:v1.0.0
```

### 私有镜像

```bash
# 1. 创建Personal Access Token
# 进入 GitHub Settings > Developer settings > Personal access tokens
# 创建token，勾选 read:packages 权限

# 2. 登录GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u dick86114 --password-stdin

# 3. 拉取镜像
docker pull ghcr.io/dick86114/canteen-menu-system:latest
```

## 🏷️ 发布新版本

### 方法1：创建GitHub Release

1. 进入仓库 Releases 页面
2. 点击 "Create a new release"
3. 填写标签版本（如 `v1.0.0`）
4. 填写发布说明
5. 点击 "Publish release"

GitHub Actions会自动构建并推送镜像。

### 方法2：手动触发工作流

1. 进入 Actions 页面
2. 选择 "发布新版本" 工作流
3. 点击 "Run workflow"
4. 输入版本号（如 `v1.0.0`）
5. 点击 "Run workflow"

## 📊 监控构建状态

### 查看构建日志

1. 进入 Actions 页面
2. 点击具体的工作流运行
3. 查看各个步骤的日志

### 构建状态徽章

在README.md中添加构建状态徽章：

```markdown
[![Docker Build](https://github.com/dick86114/canteen-menu-system/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/dick86114/canteen-menu-system/actions/workflows/docker-publish.yml)
```

## 🔍 故障排除

### 常见问题

1. **权限错误**
   ```
   Error: denied: permission_denied
   ```
   - 检查GITHUB_TOKEN权限
   - 确保仓库启用了Packages功能

2. **构建失败**
   - 查看Actions日志
   - 检查Dockerfile语法
   - 确保前端构建成功

3. **镜像拉取失败**
   - 检查镜像名称和标签
   - 确认包可见性设置
   - 验证登录凭据

### 调试命令

```bash
# 检查镜像信息
docker image inspect ghcr.io/dick86114/canteen-menu-system:latest

# 查看镜像层
docker history ghcr.io/dick86114/canteen-menu-system:latest

# 测试容器启动
docker run --rm -p 5000:5000 ghcr.io/dick86114/canteen-menu-system:latest
```

## 📈 最佳实践

### 版本管理

1. **语义化版本** - 使用 `v1.0.0` 格式
2. **预发布版本** - 使用 `v1.0.0-beta.1` 格式
3. **开发版本** - 使用分支名+SHA标签

### 安全考虑

1. **最小权限** - 只授予必要的包权限
2. **定期更新** - 及时更新基础镜像
3. **扫描漏洞** - 使用GitHub安全功能

### 性能优化

1. **多阶段构建** - 减小镜像大小
2. **构建缓存** - 利用GitHub Actions缓存
3. **并行构建** - 支持多架构构建

## 🛠️ 快速部署指南

### 完整部署流程

1. **推送代码到GitHub**
   ```bash
   git add .
   git commit -m "初始化食堂菜单系统"
   git push origin main
   ```

2. **等待自动构建**
   - 访问仓库的Actions页面
   - 查看"构建并发布Docker镜像"工作流状态
   - 等待构建完成（通常需要5-10分钟）

3. **使用镜像部署**
   ```bash
   # 创建菜单目录
   mkdir -p ./menu
   
   # 运行容器
   docker run -d \
     --name canteen-menu \
     -p 5000:5000 \
     -v $(pwd)/menu:/app/menu \
     --restart unless-stopped \
     ghcr.io/dick86114/canteen-menu-system:latest
   ```

4. **验证部署**
   ```bash
   # 检查容器状态
   docker ps | grep canteen-menu
   
   # 查看日志
   docker logs canteen-menu
   
   # 访问应用
   curl http://localhost:5000/api/health
   ```

### 使用检查脚本

项目提供了部署状态检查脚本：

**Linux/macOS:**
```bash
./scripts/check-deployment.sh
```

**Windows:**
```cmd
scripts\check-deployment.bat
```

## 🔗 相关链接

- [GitHub Packages文档](https://docs.github.com/en/packages)
- [GitHub Actions文档](https://docs.github.com/en/actions)
- [Docker官方文档](https://docs.docker.com/)
- [GitHub Container Registry指南](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)