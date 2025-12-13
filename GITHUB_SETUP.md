# 📚 GitHub上传指南

## 🔧 配置Git用户信息

```bash
# 配置全局用户信息
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的GitHub邮箱"

# 或者只为当前项目配置
git config user.name "你的GitHub用户名"
git config user.email "你的GitHub邮箱"
```

## 🚀 上传到GitHub

### 1. 在GitHub创建新仓库

1. 访问 [GitHub](https://github.com)
2. 点击右上角的 "+" 按钮
3. 选择 "New repository"
4. 填写仓库信息：
   - Repository name: `canteen-menu-system`
   - Description: `🍽️ 现代化的食堂菜单管理和展示系统`
   - 选择 Public 或 Private
   - 不要初始化README、.gitignore或LICENSE（我们已经有了）

### 2. 提交并推送代码

```bash
# 如果还没有提交
git add .
git commit -m "feat: 初始化食堂菜单系统项目"

# 添加远程仓库
git remote add origin https://github.com/你的用户名/canteen-menu-system.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 3. 配置GitHub Actions（可选）

如果要启用自动Docker构建，需要在GitHub仓库设置中添加Secrets：

1. 进入仓库 Settings > Secrets and variables > Actions
2. 添加以下Secrets：
   - `DOCKER_USERNAME`: 你的Docker Hub用户名
   - `DOCKER_PASSWORD`: 你的Docker Hub密码或访问令牌

## 📝 后续步骤

1. **更新README.md中的链接**
2. **设置仓库描述和标签**
3. **启用Issues和Discussions**
4. **配置分支保护规则**