"""
Flask application factory and configuration.
"""

from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
from flask_restx import Api
import os


def create_app(config_name: str = "development") -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configure CORS - 生产环境允许所有来源
    if config_name == "production":
        CORS(app, origins="*")
    else:
        CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"])
    

    
    # 静态文件服务（生产环境）- 必须在API之前注册
    static_folder = os.path.join(os.path.dirname(__file__), '..', 'static')
    
    # 确保静态文件目录存在
    if not os.path.exists(static_folder):
        print(f"WARNING: 静态文件目录不存在: {static_folder}")
        os.makedirs(static_folder, exist_ok=True)
    
    # 根路径路由 - 最高优先级，必须在API注册之前
    @app.route('/')
    def serve_index():
        """服务前端主页"""
        index_path = os.path.join(static_folder, 'index.html')
        print(f"DEBUG: 根路径请求，尝试服务index.html: {index_path}")
        print(f"DEBUG: 文件存在: {os.path.exists(index_path)}")
        
        if os.path.exists(index_path):
            print("DEBUG: 成功返回index.html文件")
            return send_from_directory(static_folder, 'index.html')
        else:
            print("DEBUG: index.html不存在，返回调试信息")
            return {
                "message": "食堂菜单系统后端服务运行中", 
                "status": "ok",
                "debug": {
                    "static_folder": static_folder,
                    "static_exists": os.path.exists(static_folder),
                    "static_contents": os.listdir(static_folder) if os.path.exists(static_folder) else "目录不存在",
                    "index_path": index_path
                }
            }, 200
    
    # 静态资源路由
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        """服务静态资源文件"""
        assets_path = os.path.join(static_folder, 'assets')
        if os.path.exists(os.path.join(assets_path, filename)):
            return send_from_directory(assets_path, filename)
        return {"error": "Asset not found"}, 404
    
    @app.route('/favicon.ico')
    def serve_favicon():
        """服务favicon"""
        favicon_path = os.path.join(static_folder, 'favicon.ico')
        if os.path.exists(favicon_path):
            return send_from_directory(static_folder, 'favicon.ico')
        return "", 204
    
    # 注册API蓝图 - 在静态文件路由之后
    from app.api import menu_bp
    from app.api.health import health_bp
    from app.api.scanner import scanner_bp
    app.register_blueprint(menu_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(scanner_bp)
    
    # Initialize Flask-RESTX API - 在蓝图注册之后
    api = Api(
        app,
        version='1.0',
        title='Canteen Menu System API',
        description='API for managing and displaying canteen menus',
        doc='/api/docs/'
    )
    
    # SPA路由处理 - 最低优先级，捕获所有其他路径
    @app.route('/<path:path>')
    def serve_spa(path):
        """服务SPA路由，但排除API路径"""
        print(f"DEBUG: SPA路由处理: {path}")
        
        # 排除API路径
        if path.startswith('api/'):
            return {"error": "API endpoint not found"}, 404
            
        # 检查是否是静态文件
        static_file_path = os.path.join(static_folder, path)
        if os.path.exists(static_file_path):
            print(f"DEBUG: 返回静态文件: {path}")
            return send_from_directory(static_folder, path)
        else:
            # SPA路由回退到index.html
            index_path = os.path.join(static_folder, 'index.html')
            if os.path.exists(index_path):
                print(f"DEBUG: SPA回退到index.html")
                return send_from_directory(static_folder, 'index.html')
            else:
                print(f"DEBUG: 文件未找到: {path}")
                return {"error": "File not found", "path": path}, 404
    
    return app


