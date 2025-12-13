@echo off
REM 食堂菜单系统 GitHub 上传脚本 (Windows)

echo 🍽️  食堂菜单系统 GitHub 上传脚本
echo ==================================

REM 检查是否已配置Git用户信息
git config user.name >nul 2>&1
if errorlevel 1 (
    echo ⚠️  请先配置Git用户信息：
    echo git config --global user.name "你的GitHub用户名"
    echo git config --global user.email "你的GitHub邮箱"
    pause
    exit /b 1
)

REM 检查是否已初始化Git仓库
if not exist ".git" (
    echo 📁 初始化Git仓库...
    git init
)

REM 添加所有文件
echo 📦 添加文件到Git...
git add .

REM 提交更改
echo 💾 提交更改...
git commit -m "feat: 初始化食堂菜单系统项目" -m "- 完整的前后端分离架构" -m "- React + TypeScript 前端" -m "- Flask + Python 后端" -m "- Excel文件自动扫描和解析" -m "- 响应式菜单展示界面" -m "- Docker容器化部署" -m "- 完整的测试覆盖" -m "- 中文界面支持"

REM 提示用户创建GitHub仓库
echo.
echo 🌐 请在GitHub上创建新仓库：
echo 1. 访问 https://github.com/new
echo 2. 仓库名称: canteen-menu-system
echo 3. 描述: 🍽️ 现代化的食堂菜单管理和展示系统
echo 4. 选择 Public 或 Private
echo 5. 不要初始化 README、.gitignore 或 LICENSE
echo.

set /p username="创建完成后，请输入你的GitHub用户名: "
set /p repo_name="确认仓库名称 (默认: canteen-menu-system): "

REM 设置默认仓库名
if "%repo_name%"=="" set repo_name=canteen-menu-system

REM 添加远程仓库
echo 🔗 添加远程仓库...
git remote remove origin 2>nul
git remote add origin "https://github.com/%username%/%repo_name%.git"

REM 推送到GitHub
echo 🚀 推送到GitHub...
git branch -M main
git push -u origin main

echo.
echo ✅ 上传完成！
echo 🌐 仓库地址: https://github.com/%username%/%repo_name%
echo.
echo 📝 后续步骤：
echo 1. 访问仓库页面设置描述和标签
echo 2. 启用Issues和Discussions
echo 3. 更新README.md中的链接
echo 4. 配置GitHub Actions (如需要)
pause