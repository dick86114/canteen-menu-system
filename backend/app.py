"""
Main application entry point for the Canteen Menu System backend.
"""

import os
from app import create_app

# 根据环境变量确定配置
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == "__main__":
    # 生产环境不使用debug模式
    debug_mode = config_name != 'production'
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)