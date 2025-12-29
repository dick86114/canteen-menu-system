#!/usr/bin/env python3
"""
应用启动脚本 - 确保菜单数据正确加载
"""

import os
import sys
import time
import logging
from app import create_app
from app.services.file_scanner import FileScanner
from app.models import get_storage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_menu_directory():
    """检查菜单目录状态"""
    menu_dir = '/app/menu'
    logger.info(f"检查菜单目录: {menu_dir}")
    
    if not os.path.exists(menu_dir):
        logger.error(f"菜单目录不存在: {menu_dir}")
        return False
    
    files = os.listdir(menu_dir)
    excel_files = [f for f in files if f.endswith(('.xlsx', '.xls', '.et', '.csv'))]
    
    logger.info(f"菜单目录存在，包含 {len(files)} 个文件")
    logger.info(f"其中 {len(excel_files)} 个Excel文件: {excel_files}")
    
    return len(excel_files) > 0

def load_menu_data():
    """加载菜单数据"""
    try:
        logger.info("开始加载菜单数据...")
        
        # 检查是否已有数据
        storage = get_storage()
        available_dates = storage.get_available_dates()
        
        if available_dates:
            logger.info(f"已有 {len(available_dates)} 天菜单数据，跳过加载")
            return True
        
        # 扫描并加载菜单文件
        scanner = FileScanner()
        result = scanner.scan_and_load_files()
        
        if result['success']:
            logger.info(f"菜单数据加载成功: {result['message']}")
            
            # 验证加载结果
            available_dates = storage.get_available_dates()
            logger.info(f"验证: 现在有 {len(available_dates)} 天菜单数据")
            
            # 检查档口特色
            specialty_count = 0
            for date_str in available_dates:
                menu_data = storage.get_menu_by_date(date_str)
                if menu_data:
                    has_specialty = any(
                        item.category == '档口特色'
                        for meal in menu_data.meals
                        for item in meal.items
                    )
                    if has_specialty:
                        specialty_count += 1
            
            logger.info(f"其中 {specialty_count} 天有档口特色菜品")
            return True
        else:
            logger.error(f"菜单数据加载失败: {result['message']}")
            return False
            
    except Exception as e:
        logger.error(f"加载菜单数据时出错: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("=== 食堂菜单系统启动 ===")
    
    # 检查菜单目录
    if not check_menu_directory():
        logger.warning("菜单目录检查失败，但继续启动应用")
    
    # 创建应用
    config_name = os.getenv('FLASK_ENV', 'production')
    app = create_app(config_name)
    
    # 在应用上下文中加载菜单数据
    with app.app_context():
        load_menu_data()
    
    # 启动应用
    logger.info("启动Flask应用...")
    debug_mode = config_name != 'production'
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()