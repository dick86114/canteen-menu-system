#!/bin/bash

echo "🔍 诊断菜单目录路径问题..."
echo "================================"

echo "📁 检查本地menu目录:"
if [ -d "./menu" ]; then
    echo "✅ 本地menu目录存在"
    echo "📋 目录内容:"
    ls -la ./menu/
else
    echo "❌ 本地menu目录不存在"
    echo "📁 创建menu目录..."
    mkdir -p ./menu
fi

echo ""
echo "🐳 检查容器状态:"
if docker ps | grep -q "canteen-menu"; then
    echo "✅ 容器正在运行"
    
    echo ""
    echo "📂 检查容器内的目录结构:"
    echo "容器内/app目录:"
    docker exec canteen-menu ls -la /app/
    
    echo ""
    echo "容器内/app/menu目录:"
    if docker exec canteen-menu test -d /app/menu; then
        echo "✅ /app/menu目录存在"
        docker exec canteen-menu ls -la /app/menu/
    else
        echo "❌ /app/menu目录不存在"
    fi
    
    echo ""
    echo "🔍 检查是否有其他menu目录:"
    docker exec canteen-menu find / -name "menu" -type d 2>/dev/null || echo "未找到其他menu目录"
    
    echo ""
    echo "🧪 测试API状态:"
    echo "健康检查:"
    curl -s http://localhost:1214/api/health | jq . 2>/dev/null || curl -s http://localhost:1214/api/health
    
    echo ""
    echo "扫描状态:"
    curl -s http://localhost:1214/api/scanner/status | jq . 2>/dev/null || curl -s http://localhost:1214/api/scanner/status
    
else
    echo "❌ 容器未运行"
    echo "启动容器..."
    docker-compose -f compose.yaml up -d
    echo "等待容器启动..."
    sleep 10
fi

echo ""
echo "📝 创建测试菜单文件..."
cat > ./menu/test-menu-$(date +%Y%m%d).csv << 'EOF'
日期,餐次,时间,菜品名称,价格
2025-12-14,早餐,07:00-09:00,小笼包,8
2025-12-14,早餐,07:00-09:00,豆浆,3
2025-12-14,午餐,11:30-13:30,红烧肉,15
2025-12-14,午餐,11:30-13:30,米饭,2
2025-12-15,早餐,07:00-09:00,煎蛋,6
2025-12-15,早餐,07:00-09:00,牛奶,4
EOF

echo "✅ 测试文件已创建: ./menu/test-menu-$(date +%Y%m%d).csv"

echo ""
echo "🔄 重启容器以应用最新修复:"
docker-compose -f compose.yaml pull
docker-compose -f compose.yaml down
docker-compose -f compose.yaml up -d

echo "⏳ 等待容器启动..."
sleep 15

echo ""
echo "🔄 测试刷新功能:"
curl -X POST http://localhost:1214/api/scanner/refresh

echo ""
echo "================================"
echo "🎯 诊断完成！"
echo "如果仍有问题，请将以上输出发送给开发者。"