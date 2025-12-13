@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🍽️  食堂菜单系统部署状态检查
echo ==================================

REM 检查是否在Git仓库中
if not exist ".git" (
    echo ❌ 当前目录不是Git仓库
    pause
    exit /b 1
)

REM 获取仓库信息
for /f "tokens=*" %%i in ('git config --get remote.origin.url') do set repo_url=%%i

if "!repo_url!" == "" (
    echo ❌ 未找到远程仓库URL
    pause
    exit /b 1
)

echo 📋 仓库信息:
echo   远程URL: !repo_url!
echo.

REM 检查GitHub Actions工作流文件
echo 🔍 检查GitHub Actions配置...

if exist ".github\workflows\docker-publish.yml" (
    echo ✅ Docker构建工作流已配置
) else (
    echo ❌ 缺少Docker构建工作流文件
)

if exist ".github\workflows\release.yml" (
    echo ✅ 发布工作流已配置
) else (
    echo ❌ 缺少发布工作流文件
)

REM 检查Dockerfile
if exist "Dockerfile" (
    echo ✅ Dockerfile已存在
) else (
    echo ❌ 缺少Dockerfile
)

REM 检查docker-compose.yml
if exist "docker-compose.yml" (
    echo ✅ Docker Compose配置已存在
) else (
    echo ❌ 缺少Docker Compose配置
)

echo.
echo 📝 下一步操作:
echo 1. 推送代码到GitHub仓库
echo 2. 检查Actions页面确认工作流运行
echo 3. 创建Release发布新版本
echo 4. 使用GHCR镜像部署应用
echo.
echo 🐳 镜像拉取命令示例:
echo docker pull ghcr.io/dick86114/canteen-menu-system:latest
echo.
echo ✅ 检查完成！

pause