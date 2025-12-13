"""
文件扫描API端点
"""
from flask import Blueprint, jsonify
from flask_restx import Api, Resource, fields
import logging

from ..services.file_scanner import FileScanner

logger = logging.getLogger(__name__)

# 创建蓝图
scanner_bp = Blueprint('scanner', __name__, url_prefix='/api/scanner')
api = Api(scanner_bp, doc='/scanner/', title='文件扫描API', description='自动扫描和加载菜单文件')

# 创建文件扫描器实例
file_scanner = FileScanner()

# API模型定义
scan_result_model = api.model('ScanResult', {
    'success': fields.Boolean(required=True, description='扫描是否成功'),
    'message': fields.String(required=True, description='扫描结果消息'),
    'loaded_files': fields.List(fields.Raw, description='成功加载的文件列表'),
    'failed_files': fields.List(fields.Raw, description='加载失败的文件列表'),
    'total_menus': fields.Integer(description='总共加载的菜单数量')
})

scan_status_model = api.model('ScanStatus', {
    'menu_directory': fields.String(description='菜单文件目录'),
    'directory_exists': fields.Boolean(description='目录是否存在'),
    'excel_files_count': fields.Integer(description='Excel文件数量'),
    'excel_files': fields.List(fields.String, description='Excel文件列表'),
    'loaded_menus_count': fields.Integer(description='已加载菜单数量'),
    'available_dates': fields.List(fields.String, description='可用日期列表')
})


@api.route('/scan')
class ScanFiles(Resource):
    @api.doc('scan_files')
    @api.marshal_with(scan_result_model)
    def post(self):
        """扫描并加载menu目录下的所有Excel文件"""
        try:
            logger.info("开始扫描菜单文件...")
            result = file_scanner.scan_and_load_files()
            
            status_code = 200 if result['success'] else 400
            return result, status_code
            
        except Exception as e:
            error_msg = f"扫描文件时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'loaded_files': [],
                'failed_files': [],
                'total_menus': 0
            }, 500


@api.route('/status')
class ScanStatus(Resource):
    @api.doc('scan_status')
    @api.marshal_with(scan_status_model)
    def get(self):
        """获取文件扫描状态"""
        try:
            status = file_scanner.get_scan_status()
            return status, 200
            
        except Exception as e:
            error_msg = f"获取扫描状态时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                'menu_directory': '',
                'directory_exists': False,
                'excel_files_count': 0,
                'excel_files': [],
                'loaded_menus_count': 0,
                'available_dates': []
            }, 500


@api.route('/auto-load')
class AutoLoad(Resource):
    @api.doc('auto_load')
    @api.marshal_with(scan_result_model)
    def get(self):
        """自动加载菜单文件（如果还没有数据的话）"""
        try:
            # 检查是否已有数据
            status = file_scanner.get_scan_status()
            
            if status['loaded_menus_count'] > 0:
                return {
                    'success': True,
                    'message': f"已有 {status['loaded_menus_count']} 天菜单数据，无需重新加载",
                    'loaded_files': [],
                    'failed_files': [],
                    'total_menus': status['loaded_menus_count']
                }, 200
            
            # 如果没有数据，自动扫描加载
            logger.info("检测到无菜单数据，自动扫描加载...")
            result = file_scanner.scan_and_load_files()
            
            status_code = 200 if result['success'] else 400
            return result, status_code
            
        except Exception as e:
            error_msg = f"自动加载时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'loaded_files': [],
                'failed_files': [],
                'total_menus': 0
            }, 500


@api.route('/clear-cache')
class ClearCache(Resource):
    @api.doc('clear_cache')
    def post(self):
        """清除所有缓存的菜单数据"""
        try:
            logger.info("开始清除菜单缓存...")
            file_scanner.clear_cache()
            
            return {
                'success': True,
                'message': '菜单缓存已清除'
            }, 200
            
        except Exception as e:
            error_msg = f"清除缓存时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }, 500


@api.route('/refresh')
class RefreshMenus(Resource):
    @api.doc('refresh_menus')
    @api.marshal_with(scan_result_model)
    def post(self):
        """清除缓存并重新扫描加载菜单文件"""
        try:
            logger.info("开始刷新菜单数据...")
            
            # 先清除缓存
            file_scanner.clear_cache()
            logger.info("缓存已清除")
            
            # 重新扫描加载
            result = file_scanner.scan_and_load_files()
            
            if result['success']:
                result['message'] = f"刷新成功：{result['message']}"
            
            status_code = 200 if result['success'] else 400
            return result, status_code
            
        except Exception as e:
            error_msg = f"刷新菜单时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'loaded_files': [],
                'failed_files': [],
                'total_menus': 0
            }, 500