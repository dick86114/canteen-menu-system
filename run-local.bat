@echo off
chcp 65001 >nul
echo 🚀 本地运行食堂菜单系统

echo.
echo 1. 启动后端...
cd backend
start "后端服务" cmd /k "python app.py"

echo.
echo 2. 等待后端启动...
timeout /t 5

echo.
echo 3. 启动前端开发服务器...
cd ..\frontend
start "前端服务" cmd /k "npm run dev"

echo.
echo 4. 等待服务启动...
timeout /t 10

echo.
echo 5. 打开浏览器...
start http://localhost:3000

echo.
echo ✅ 服务已启动！
echo 前端: http://localhost:3000
echo 后端: http://localhost:5000
echo API文档: http://localhost:5000/api/docs

pause