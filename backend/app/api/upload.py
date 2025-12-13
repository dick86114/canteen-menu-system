"""
File upload API endpoints for Excel menu files.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_restx import Api, Resource, fields
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from typing import Dict, Any, List
import os
import tempfile

from ..services.excel_parser import ExcelParser, ExcelParsingError
from ..models import get_storage

upload_bp = Blueprint('upload', __name__, url_prefix='/api')
api = Api(upload_bp, doc=False)  # Disable docs for individual blueprints

# API models for documentation
upload_response_model = api.model('UploadResponse', {
    'status': fields.String(required=True, description='Upload status (success/error)'),
    'message': fields.String(required=True, description='Status message'),
    'data': fields.Raw(description='Parsed menu data (on success)')
})


@api.route('/upload')
class UploadResource(Resource):
    """File upload endpoint for Excel menu files."""
    
    @api.doc('upload_file')
    @api.expect(api.parser().add_argument('file', location='files', type=FileStorage, required=True))
    @api.marshal_with(upload_response_model)
    def post(self) -> Dict[str, Any]:
        """
        Upload and process Excel menu file.
        
        Accepts .xlsx files containing menu data and processes them
        for storage and display.
        """
        # Check if file is present in request
        if 'file' not in request.files:
            return {
                'status': 'error',
                'message': 'No file provided in request'
            }, 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return {
                'status': 'error',
                'message': 'No file selected'
            }, 400
        
        # Validate file extension
        if not self._allowed_file(file.filename):
            return {
                'status': 'error',
                'message': 'Invalid file format. Only .xlsx files are allowed.'
            }, 400
        
        # Additional security validation - check file size explicitly
        file.seek(0, 2)  # Seek to end of file
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if file_size > max_size:
            return {
                'status': 'error',
                'message': f'File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)'
            }, 413
        
        # Security validation - check for empty files
        if file_size == 0:
            return {
                'status': 'error',
                'message': 'Empty file not allowed'
            }, 400
        
        # Use temporary file for security
        try:
            # Create temporary file and ensure it's closed before use
            temp_fd, temp_filepath = tempfile.mkstemp(suffix='.xlsx')
            # Close the file descriptor to avoid Windows file locking issues
            os.close(temp_fd)
            
            # Save file to temporary location
            file.save(temp_filepath)
            
            # Parse Excel file using ExcelParser
            parser = ExcelParser()
            
            try:
                # Parse the uploaded Excel file
                menu_data_list = parser.parse_excel_file(temp_filepath)
                
                # Store parsed data using global storage instance
                storage = get_storage()
                stored_count = 0
                for menu_data in menu_data_list:
                    if storage.store_menu_data(menu_data):
                        stored_count += 1
                
                # Track uploaded file
                storage.add_uploaded_file(secure_filename(file.filename))
                
                # Convert menu data to JSON-serializable format
                parsed_data = [menu_data.to_dict() for menu_data in menu_data_list]
                
                return {
                    'status': 'success',
                    'message': f'File uploaded and parsed successfully. Found {len(menu_data_list)} menu dates, stored {stored_count}.',
                    'data': parsed_data
                }
                
            except ExcelParsingError as e:
                return {
                    'status': 'error',
                    'message': f'Excel parsing failed: {str(e)}'
                }, 422
            
            finally:
                # Clean up temporary file
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'File upload failed: {str(e)}'
            }, 500
    
    def _allowed_file(self, filename: str) -> bool:
        """
        Check if uploaded file has allowed extension.
        
        Args:
            filename: Name of the uploaded file
            
        Returns:
            True if file extension is allowed, False otherwise
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']