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
    
    @app.route('/')
    def serve_index():
        """服务前端主页"""
        print(f"DEBUG: 静态文件目录: {static_folder}")
        print(f"DEBUG: 目录是否存在: {os.path.exists(static_folder)}")
        if os.path.exists(static_folder):
            print(f"DEBUG: 目录内容: {os.listdir(static_folder)}")
        
        index_path = os.path.join(static_folder, 'index.html')
        print(f"DEBUG: index.html路径: {index_path}")
        print(f"DEBUG: index.html是否存在: {os.path.exists(index_path)}")
        
        if os.path.exists(index_path):
            return send_from_directory(static_folder, 'index.html')
        else:
            return {
                "message": "食堂菜单系统后端服务运行中", 
                "status": "ok",
                "debug": {
                    "static_folder": static_folder,
                    "static_exists": os.path.exists(static_folder),
                    "static_contents": os.listdir(static_folder) if os.path.exists(static_folder) else "目录不存在"
                }
            }, 200
    
    @app.route('/static/<path:filename>')
    def serve_static_files(filename):
        """服务静态资源文件"""
        return send_from_directory(static_folder, filename)
    
    @app.route('/<path:path>')
    def serve_spa(path):
        """服务SPA路由，但排除API路径"""
        # 排除API路径
        if path.startswith('api/'):
            return {"error": "API endpoint not found"}, 404
            
        # 检查是否是静态文件
        if os.path.exists(os.path.join(static_folder, path)):
            return send_from_directory(static_folder, path)
        else:
            # SPA路由回退到index.html
            if os.path.exists(os.path.join(static_folder, 'index.html')):
                return send_from_directory(static_folder, 'index.html')
            else:
                return {"error": "File not found"}, 404
    
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