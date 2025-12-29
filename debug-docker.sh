#!/bin/bash
# Docker部署诊断脚本

echo "=== 食堂菜单系统 Docker 诊断 ==="
echo

# 检查容器状态
echo "1. 检查容器状态..."
docker ps -a | grep canteen-menu
echo

# 检查容器日志
echo "2. 查看容器启动日志..."
docker logs canteen-menu --tail 50
echo

# 检查菜单文件挂载
echo "3. 检查菜单文件挂载..."
echo "本地menu目录内容:"
ls -la ./menu/
echo
echo "容器内menu目录内容:"
docker exec canteen-menu ls -la /app/menu/ 2>/dev/null || echo "无法访问容器内目录"
echo

# 检查API状态
echo "4. 检查API状态..."
echo "健康检查:"
curl -s http://localhost:1214/api/health | python -m json.tool 2>/dev/null || echo "API不可访问"
echo
echo "扫描状态:"
curl -s http://localhost:1214/api/scanner/status | python -m json.tool 2>/dev/null || echo "扫描API不可访问"
echo

# 检查可用日期
echo "5. 检查可用日期..."
curl -s http://localhost:1214/api/dates | python -m json.tool 2>/dev/null || echo "日期API不可访问"
echo

# 检查档口特色日期
echo "6. 检查档口特色日期..."
curl -s http://localhost:1214/api/specialty-dates | python -m json.tool 2>/dev/null || echo "档口特色API不可访问"
echo

# 手动触发扫描
echo "7. 手动触发菜单扫描..."
curl -s -X POST http://localhost:1214/api/scanner/scan | python -m json.tool 2>/dev/null || echo "扫描触发失败"
echo

echo "=== 诊断完成 ==="
echo "如果发现问题，请检查:"
echo "1. menu目录是否正确挂载"
echo "2. 容器内是否有Excel文件"
echo "3. 容器日志中是否有错误信息"
echo "4. API端点是否正常响应"