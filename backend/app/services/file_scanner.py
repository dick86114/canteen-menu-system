"""
文件扫描服务 - 自动扫描和加载menu目录下的Excel文件
"""
import os
import glob
from typing import List, Dict, Any
from datetime import datetime
import logging

from .excel_parser import ExcelParser
from ..models import get_storage

logger = logging.getLogger(__name__)


class FileScanner:
    """文件扫描器 - 自动扫描和处理Excel菜单文件"""
    
    def __init__(self, menu_directory: str = None):
        """
        初始化文件扫描器
        
        Args:
            menu_directory: 菜单文件目录路径，默认为/app/menu
        """
        if menu_directory is None:
            # 检查环境变量，支持本地开发和容器环境
            menu_directory = os.environ.get('MENU_DIRECTORY')
            
            if menu_directory is None:
                # 自动检测环境
                # 检查是否在Docker容器中（通过检查特定的容器环境标识）
                is_container = (
                    os.path.exists('/app') and 
                    os.path.exists('/app/menu') and
                    not os.path.exists('./backend')  # 本地开发环境会有backend目录
                )
                
                if is_container:
                    # 容器环境
                    menu_directory = '/app/menu'
                else:
                    # 本地开发环境，从backend目录向上找到项目根目录的menu文件夹
                    # 当前文件路径: backend/app/services/file_scanner.py
                    # 项目根目录: ../../../
                    # menu目录: ../../../menu
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.join(current_dir, '..', '..', '..')
                    menu_directory = os.path.join(project_root, 'menu')
                    menu_directory = os.path.abspath(menu_directory)
            
            # 如果路径是 /menu，修正为 /app/menu（容器环境修复）
            if menu_directory == '/menu':
                menu_directory = '/app/menu'
        
        self.menu_directory = menu_directory
        self.excel_parser = ExcelParser()
        self.storage = get_storage()
        
        logger.info(f"文件扫描器初始化，扫描目录: {self.menu_directory}")
    
    def scan_and_load_files(self) -> Dict[str, Any]:
        """
        扫描menu目录并加载所有Excel文件
        
        Returns:
            Dict: 包含加载结果的字典
        """
        result = {
            'success': True,
            'loaded_files': [],
            'failed_files': [],
            'total_menus': 0,
            'message': ''
        }
        
        try:
            # 检查目录是否存在
            if not os.path.exists(self.menu_directory):
                result['success'] = False
                result['message'] = f"菜单目录不存在: {self.menu_directory}"
                logger.error(result['message'])
                return result
            
            # 扫描Excel文件
            excel_files = self._find_excel_files()
            
            if not excel_files:
                result['message'] = f"在目录 {self.menu_directory} 中未找到Excel文件"
                logger.info(result['message'])
                return result
            
            logger.info(f"找到 {len(excel_files)} 个Excel文件")
            
            # 清空现有数据
            self.storage.clear_all_data()
            
            # 处理每个文件
            for file_path in excel_files:
                try:
                    self._process_excel_file(file_path, result)
                except Exception as e:
                    error_msg = f"处理文件 {os.path.basename(file_path)} 时出错: {str(e)}"
                    logger.error(error_msg)
                    result['failed_files'].append({
                        'file': os.path.basename(file_path),
                        'error': str(e)
                    })
            
            # 生成结果消息
            total_files = len(excel_files)
            success_count = len(result['loaded_files'])
            failed_count = len(result['failed_files'])
            
            if success_count > 0:
                result['message'] = f"成功加载 {success_count}/{total_files} 个文件，共 {result['total_menus']} 天菜单"
                if failed_count > 0:
                    result['message'] += f"，{failed_count} 个文件加载失败"
            else:
                result['success'] = False
                result['message'] = f"所有 {total_files} 个文件都加载失败"
            
            logger.info(result['message'])
            
        except Exception as e:
            result['success'] = False
            result['message'] = f"扫描文件时出错: {str(e)}"
            logger.error(result['message'])
        
        return result
    
    def _find_excel_files(self) -> List[str]:
        """
        查找目录下的所有Excel文件
        
        Returns:
            List[str]: Excel文件路径列表
        """
        excel_patterns = [
            os.path.join(self.menu_directory, '*.xlsx'),
            os.path.join(self.menu_directory, '*.xls'),
            os.path.join(self.menu_directory, '*.csv')  # 临时支持CSV文件用于本地测试
        ]
        
        excel_files = []
        for pattern in excel_patterns:
            files = glob.glob(pattern)
            # 过滤掉临时文件（以~$开头的文件）
            valid_files = [f for f in files if not os.path.basename(f).startswith('~$')]
            excel_files.extend(valid_files)
        
        # 按文件名排序
        excel_files.sort()
        
        logger.info(f"找到有效Excel文件: {[os.path.basename(f) for f in excel_files]}")
        
        return excel_files
    
    def _process_excel_file(self, file_path: str, result: Dict[str, Any]):
        """
        处理单个Excel文件
        
        Args:
            file_path: Excel文件路径
            result: 结果字典，用于记录处理结果
        """
        file_name = os.path.basename(file_path)
        logger.info(f"正在处理文件: {file_name}")
        
        try:
            # 解析Excel文件
            menu_data_list = self.excel_parser.parse_excel_file(file_path)
            
            if not menu_data_list:
                raise ValueError("文件中没有找到有效的菜单数据")
            
            # 存储菜单数据
            stored_count = 0
            for menu_data in menu_data_list:
                self.storage.store_menu_data(menu_data)
                stored_count += 1
            
            # 记录成功结果
            dates = []
            for menu in menu_data_list:
                if hasattr(menu.date, 'strftime'):
                    dates.append(menu.date.strftime('%Y-%m-%d'))
                else:
                    dates.append(str(menu.date))
            
            result['loaded_files'].append({
                'file': file_name,
                'menus_count': stored_count,
                'dates': dates
            })
            result['total_menus'] += stored_count
            
            logger.info(f"文件 {file_name} 处理成功，加载了 {stored_count} 天菜单")
            
        except Exception as e:
            raise Exception(f"解析文件失败: {str(e)}")
    
    def clear_cache(self):
        """
        清除所有缓存的菜单数据
        """
        logger.info("清除菜单缓存...")
        self.storage.clear_all_data()
        logger.info("菜单缓存已清除")
    
    def get_scan_status(self) -> Dict[str, Any]:
        """
        获取当前扫描状态
        
        Returns:
            Dict: 扫描状态信息
        """
        excel_files = self._find_excel_files()
        available_dates = self.storage.get_available_dates()
        
        # 处理日期格式
        formatted_dates = []
        for date in available_dates:
            if hasattr(date, 'strftime'):
                formatted_dates.append(date.strftime('%Y-%m-%d'))
            else:
                formatted_dates.append(str(date))
        
        return {
            'menu_directory': self.menu_directory,
            'directory_exists': os.path.exists(self.menu_directory),
            'excel_files_count': len(excel_files),
            'excel_files': [os.path.basename(f) for f in excel_files],
            'loaded_menus_count': len(available_dates),
            'available_dates': formatted_dates
        }