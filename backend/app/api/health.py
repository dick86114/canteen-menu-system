"""
Health check API endpoint for monitoring application status.
"""

from flask import Blueprint, jsonify
from flask_restx import Api, Resource, fields
from datetime import datetime
from typing import Dict, Any

health_bp = Blueprint('health', __name__, url_prefix='/api')
api = Api(health_bp, doc=False)  # Disable docs for individual blueprints

# API models for documentation
health_response_model = api.model('HealthResponse', {
    'status': fields.String(required=True, description='Health status (healthy/unhealthy)'),
    'timestamp': fields.String(required=True, description='Current server timestamp'),
    'version': fields.String(description='Application version'),
    'uptime': fields.String(description='Server uptime information'),
    'services': fields.Raw(description='Status of dependent services')
})


@api.route('/health')
class HealthResource(Resource):
    """Health check endpoint."""
    
    @api.doc('health_check')
    @api.marshal_with(health_response_model)
    def get(self) -> Dict[str, Any]:
        """
        Get application health status.
        
        Returns basic health information including timestamp,
        version, and status of dependent services.
        """
        try:
            # Basic health check
            from ..utils.timezone import now
            from ..models import get_storage
            current_time = now()
            
            # 检查菜单数据状态
            storage = get_storage()
            available_dates = storage.get_available_dates()
            menu_status = 'healthy' if available_dates else 'no_data'
            
            # Check dependent services (can be extended)
            services_status = {
                'storage': 'healthy',  # In-memory storage is always available
                'excel_parser': 'healthy',  # Excel parser service
                'menu_data': menu_status,  # 菜单数据状态
            }
            
            # 添加菜单数据信息
            menu_info = {
                'total_dates': len(available_dates),
                'date_range': {
                    'start': available_dates[0] if available_dates else None,
                    'end': available_dates[-1] if available_dates else None
                }
            }
            
            # Determine overall health
            overall_status = 'healthy' if all(
                status in ['healthy', 'no_data'] for status in services_status.values()
            ) else 'unhealthy'
            
            return {
                'status': overall_status,
                'timestamp': current_time.isoformat(),
                'version': '1.0.0',  # Can be read from config or environment
                'uptime': 'Available',  # Can be calculated from start time
                'services': services_status,
                'menu_info': menu_info
            }
            
        except Exception as e:
            from ..utils.timezone import format_datetime
            return {
                'status': 'unhealthy',
                'timestamp': format_datetime(),
                'error': str(e)
            }, 500


@api.route('/ping')
class PingResource(Resource):
    """Simple ping endpoint for basic connectivity check."""
    
    @api.doc('ping')
    def get(self) -> Dict[str, str]:
        """
        Simple ping endpoint.
        
        Returns a basic pong response for connectivity testing.
        """
        from ..utils.timezone import format_datetime
        return {
            'message': 'pong',
            'timestamp': format_datetime()
        }