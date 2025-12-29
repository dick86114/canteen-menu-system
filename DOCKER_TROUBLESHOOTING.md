# Docker部署问题排查指南

## 问题描述
Docker部署后午餐分类没有显示，可能的原因包括：
1. 菜单数据未正确加载
2. 容器环境路径问题
3. 前端静态文件问题
4. API端点访问问题

## 解决方案

### 1. 快速修复
运行修复脚本：
```bash
# Windows
fix-docker-deployment.bat

# Linux/Mac
./fix-docker-deployment.sh
```

### 2. 手动排查步骤

#### 步骤1：检查容器状态
```bash
docker ps -a | grep canteen-menu
```

#### 步骤2：查看容器日志
```bash
docker logs canteen-menu --tail 50
```

#### 步骤3：检查菜单文件挂载
```bash
# 检查本地menu目录
ls -la ./menu/

# 检查容器内menu目录
docker exec canteen-menu ls -la /app/menu/
```

#### 步骤4：测试API端点
```bash
# 健康检查
curl http://localhost:1214/api/health

# 扫描状态
curl http://localhost:1214/api/scanner/status

# 可用日期
curl http://localhost:1214/api/dates

# 档口特色日期
curl http://localhost:1214/api/specialty-dates
```

#### 步骤5：手动触发菜单扫描
```bash
curl -X POST http://localhost:1214/api/scanner/scan
```

### 3. 常见问题及解决方法

#### 问题1：菜单目录为空
**症状**：API返回空数据，容器内/app/menu目录为空
**解决**：
1. 确保本地menu目录存在且包含Excel文件
2. 检查docker-compose.yaml中的挂载配置
3. 重新启动容器

#### 问题2：Excel文件解析失败
**症状**：容器日志显示解析错误
**解决**：
1. 检查Excel文件格式是否正确
2. 确保文件没有损坏
3. 查看具体错误信息

#### 问题3：前端静态文件缺失
**症状**：访问根路径返回API响应而非前端页面
**解决**：
1. 重新构建镜像确保前端正确构建
2. 检查Dockerfile中的静态文件复制步骤

#### 问题4：API端点不响应
**症状**：curl请求超时或返回错误
**解决**：
1. 检查容器是否正常运行
2. 确认端口映射正确(1214:5000)
3. 检查防火墙设置

### 4. 诊断工具

#### 自动诊断脚本
```bash
# Windows
debug-docker.bat

# Linux/Mac
./debug-docker.sh
```

#### 手动诊断命令
```bash
# 进入容器查看
docker exec -it canteen-menu /bin/bash

# 在容器内检查
ls -la /app/menu/
python -c "from app.services.file_scanner import FileScanner; scanner = FileScanner(); print(scanner.get_scan_status())"
```

### 5. 重新部署流程

#### 完全重新部署
```bash
# 1. 停止并删除容器
docker stop canteen-menu
docker rm canteen-menu

# 2. 删除旧镜像
docker rmi ghcr.io/dick86114/canteen-menu-system:latest

# 3. 重新构建
docker build -t ghcr.io/dick86114/canteen-menu-system:latest .

# 4. 启动新容器
docker-compose up -d

# 5. 检查状态
docker logs canteen-menu --tail 20
curl http://localhost:1214/api/health
```

### 6. 验证部署成功

部署成功的标志：
1. 容器状态为running
2. 健康检查API返回healthy状态
3. 菜单数据API返回非空数据
4. 前端页面正常显示
5. 档口特色功能正常工作

### 7. 性能优化建议

1. **菜单文件管理**：定期清理旧的Excel文件
2. **容器资源**：根据需要调整内存和CPU限制
3. **日志管理**：配置日志轮转避免日志文件过大
4. **监控告警**：设置健康检查告警

### 8. 联系支持

如果以上步骤都无法解决问题，请提供：
1. 容器日志输出
2. API响应结果
3. 本地menu目录内容
4. 系统环境信息

## 更新记录

- 2024-12-29: 添加自动菜单加载功能
- 2024-12-29: 增强健康检查API
- 2024-12-29: 创建诊断和修复脚本