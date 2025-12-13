"""
Menu API endpoints for retrieving menu data and available dates.
"""

from flask import Blueprint, jsonify, request
from flask_restx import Api, Resource, fields
from typing import Dict, Any, Optional
from app.models import get_storage
from datetime import datetime

menu_bp = Blueprint('menu', __name__, url_prefix='/api')
api = Api(menu_bp, doc=False)  # Disable docs for individual blueprints

# API models for documentation
menu_item_model = api.model('MenuItem', {
    'name': fields.String(required=True, description='Food item name'),
    'description': fields.String(description='Food item description'),
    'category': fields.String(description='Food category'),
    'price': fields.Float(description='Item price')
})

meal_model = api.model('Meal', {
    'type': fields.String(required=True, description='Meal type (breakfast/lunch/dinner)'),
    'time': fields.String(required=True, description='Meal time in HH:MM format'),
    'items': fields.List(fields.Nested(menu_item_model), required=True)
})

menu_response_model = api.model('MenuResponse', {
    'date': fields.String(required=True, description='Menu date in YYYY-MM-DD format'),
    'meals': fields.List(fields.Nested(meal_model), required=True),
    'requestedDate': fields.String(description='Originally requested date (if different from returned date)'),
    'fallback': fields.Boolean(description='Whether this is a fallback menu'),
    'message': fields.String(description='Additional information about the response')
})

dates_response_model = api.model('DatesResponse', {
    'dates': fields.List(fields.String, required=True, description='Available menu dates'),
    'count': fields.Integer(required=True, description='Number of available dates'),
    'dateRange': fields.Raw(description='Date range with start and end dates'),
    'currentDate': fields.String(description='Current date in YYYY-MM-DD format'),
    'hasCurrentDate': fields.Boolean(description='Whether current date has menu data'),
    'mostRecentDate': fields.String(description='Most recent date with menu data')
})


@api.route('/menu')
class MenuResource(Resource):
    """Menu data retrieval endpoint."""
    
    @api.doc('get_menu')
    @api.param('date', 'Menu date in YYYY-MM-DD format', type='string')
    @api.marshal_with(menu_response_model)
    def get(self) -> Dict[str, Any]:
        """
        Get menu data for a specific date.
        
        Returns menu data for the requested date, or the most recent
        available menu if no date is specified or data doesn't exist.
        """
        date_param = request.args.get('date')
        
        if date_param:
            # Validate date format
            try:
                datetime.strptime(date_param, '%Y-%m-%d')
            except ValueError:
                return {
                    'status': 'error',
                    'message': 'Invalid date format. Use YYYY-MM-DD.'
                }, 400
            
            # Get menu for specific date
            storage = get_storage()
            menu_data = storage.get_menu_by_date(date_param)
            
            # If no menu for specific date, implement fallback logic
            if menu_data is None:
                fallback_menu = storage.get_most_recent_menu()
                if fallback_menu is not None:
                    # Return fallback menu but indicate the actual date requested
                    result = fallback_menu.to_dict()
                    result['requestedDate'] = date_param
                    result['fallback'] = True
                    result['message'] = f'No menu found for {date_param}, showing most recent menu from {fallback_menu.date}'
                    return result
                else:
                    # No data available at all
                    return {
                        'date': date_param,
                        'meals': [],
                        'message': 'No menu data available'
                    }
            
            return menu_data.to_dict()
        else:
            # Get current date menu or most recent if no date specified
            storage = get_storage()
            current_date = datetime.now().strftime('%Y-%m-%d')
            menu_data = storage.get_menu_by_date(current_date)
            
            if menu_data is None:
                # Fallback to most recent menu
                menu_data = storage.get_most_recent_menu()
                if menu_data is not None:
                    result = menu_data.to_dict()
                    result['fallback'] = True
                    result['message'] = f'No menu for today ({current_date}), showing most recent menu from {menu_data.date}'
                    return result
                else:
                    return {
                        'date': current_date,
                        'meals': [],
                        'message': 'No menu data available'
                    }
            
            return menu_data.to_dict()


@api.route('/dates')
class DatesResource(Resource):
    """Available dates endpoint."""
    
    @api.doc('get_dates')
    @api.marshal_with(dates_response_model)
    def get(self) -> Dict[str, Any]:
        """
        Get list of available menu dates.
        
        Returns all dates for which menu data is available,
        along with metadata about the date range and count.
        """
        storage = get_storage()
        dates = storage.get_available_dates()
        date_range = storage.get_date_range()
        
        response = {
            'dates': dates,
            'count': len(dates),
            'dateRange': {
                'start': date_range[0] if date_range else None,
                'end': date_range[1] if date_range else None
            }
        }
        
        # Add current date information
        current_date = datetime.now().strftime('%Y-%m-%d')
        response['currentDate'] = current_date
        response['hasCurrentDate'] = current_date in dates
        
        # Add most recent date information
        if dates:
            response['mostRecentDate'] = dates[-1]
        
        return response