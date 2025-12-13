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
    
    # Configure file upload settings and size limits
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'xlsx'}
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize Flask-RESTX API
    api = Api(
        app,
        version='1.0',
        title='Canteen Menu System API',
        description='API for managing and displaying canteen menus',
        doc='/api/docs/'
    )
    
    # Register blueprints
    from app.api import menu_bp, upload_bp
    from app.api.health import health_bp
    from app.api.scanner import scanner_bp
    app.register_blueprint(menu_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(scanner_bp)
    
    # 静态文件服务（生产环境）
    static_folder = os.path.join(os.path.dirname(__file__), '..', 'static')
    
    # 确保静态文件目录存在
    if not os.path.exists(static_folder):
        print(f"WARNING: 静态文件目录不存在: {static_folder}")
        os.makedirs(static_folder, exist_ok=True)
    
    # 注册静态文件路由 - 必须在API路由之后注册
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
    
    # 根路径路由 - 最高优先级
    @app.route('/')
    def serve_index():
        """服务前端主页"""
        index_path = os.path.join(static_folder, 'index.html')
        print(f"DEBUG: 尝试服务index.html: {index_path}")
        print(f"DEBUG: 文件存在: {os.path.exists(index_path)}")
        
        if os.path.exists(index_path):
            print("DEBUG: 返回index.html文件")
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


def allowed_file(filename: str) -> bool:
    """
    Check if uploaded file has allowed extension.
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        True if file extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'xlsx'}