# 食堂菜单系统 Docker 镜像
# 多阶段构建：前端构建 + 后端运行

# 阶段1：构建前端
FROM node:18-alpine AS frontend-builder

# 设置工作目录
WORKDIR /app/frontend

# 安装git（某些npm包可能需要）
RUN apk add --no-cache git

# 复制前端依赖文件
COPY frontend/package*.json ./

# 清理npm缓存并安装依赖
RUN npm cache clean --force && npm ci

# 复制前端源码
COPY frontend/ ./

# 构建前端
RUN echo "开始构建前端..." && \
    npm run build && \
    echo "前端构建完成，检查输出目录..." && \
    ls -la dist/

# 阶段2：后端运行环境  
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 复制后端依赖文件并安装
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 复制后端源码
COPY backend/ ./

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/frontend/dist ./static

# 验证静态文件复制
RUN echo "检查静态文件..." && \
    ls -la static/ || echo "静态文件目录不存在"

# 创建菜单文件目录
RUN mkdir -p /app/menu

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV TZ=Asia/Shanghai

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# 启动命令
CMD ["python", "startup.py"]