#!/bin/bash

# 远程服务器容器诊断脚本
# 请将此脚本上传到远程服务器并执行

echo "🔍 远程容器诊断脚本"
echo "=================================="

# 服务器信息
echo "📋 服务器信息:"
echo "主机名: $(hostname)"
echo "时间: $(date)"
echo "用户: $(whoami)"
echo ""

# 检查Docker服务
echo "🐳 检查Docker服务状态:"
systemctl is-active docker || echo "Docker服务未运行"
echo ""

# 检查容器状态
echo "📦 检查容器状态:"
docker ps -a | grep canteen-menu || echo "未找到canteen-menu容器"
echo ""

# 检查容器日志
echo "📝 容器日志（最后20行）:"
docker logs --tail 20 canteen-menu 2>/dev/null || echo "无法获取容器日志"
echo ""

# 检查端口占用
echo "🌐 检查端口1214占用情况:"
netstat -tlnp | grep :1214 || echo "端口1214未被占用"
echo ""

# 检查容器内部
echo "📁 检查容器内静态文件:"
docker exec canteen-menu ls -la /app/static/ 2>/dev/null || echo "无法访问容器内部"
echo ""

# 检查容器内进程
echo "🔧 检查容器内Python进程:"
docker exec canteen-menu ps aux | grep python 2>/dev/null || echo "无法检查容器进程"
echo ""

# 测试本地API
echo "🧪 测试本地API:"
curl -s http://localhost:1214/api/health || echo "API测试失败"
echo ""

# 测试根路径
echo "🏠 测试根路径:"
curl -s -I http://localhost:1214/ || echo "根路径测试失败"
echo ""

echo "✅ 诊断完成！"