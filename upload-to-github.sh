#!/bin/bash

# 食堂菜单系统 GitHub 上传脚本

echo "🍽️  食堂菜单系统 GitHub 上传脚本"
echo "=================================="

# 检查是否已配置Git用户信息
if ! git config user.name > /dev/null; then
    echo "⚠️  请先配置Git用户信息："
    echo "git config --global user.name \"你的GitHub用户名\""
    echo "git config --global user.email \"你的GitHub邮箱\""
    exit 1
fi

# 检查是否已初始化Git仓库
if [ ! -d ".git" ]; then
    echo "📁 初始化Git仓库..."
    git init
fi

# 添加所有文件
echo "📦 添加文件到Git..."
git add .

# 检查是否有更改需要提交
if git diff --staged --quiet; then
    echo "ℹ️  没有新的更改需要提交"
else
    echo "💾 提交更改..."
    git commit -m "feat: 初始化食堂菜单系统项目

- 完整的前后端分离架构
- React + TypeScript 前端
- Flask + Python 后端  
- Excel文件自动扫描和解析
- 响应式菜单展示界面
- Docker容器化部署
- 完整的测试覆盖
- 中文界面支持"
fi

# 提示用户创建GitHub仓库
echo ""
echo "🌐 请在GitHub上创建新仓库："
echo "1. 访问 https://github.com/new"
echo "2. 仓库名称: canteen-menu-system"
echo "3. 描述: 🍽️ 现代化的食堂菜单管理和展示系统"
echo "4. 选择 Public 或 Private"
echo "5. 不要初始化 README、.gitignore 或 LICENSE"
echo ""

read -p "创建完成后，请输入你的GitHub用户名: " username
read -p "确认仓库名称 (默认: canteen-menu-system): " repo_name

# 设置默认仓库名
if [ -z "$repo_name" ]; then
    repo_name="canteen-menu-system"
fi

# 添加远程仓库
echo "🔗 添加远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$username/$repo_name.git"

# 推送到GitHub
echo "🚀 推送到GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ 上传完成！"
echo "🌐 仓库地址: https://github.com/$username/$repo_name"
echo ""
echo "📝 后续步骤："
echo "1. 访问仓库页面设置描述和标签"
echo "2. 启用Issues和Discussions"
echo "3. 更新README.md中的链接"
echo "4. 配置GitHub Actions (如需要)"