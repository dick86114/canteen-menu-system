"""
Tests for Flask application setup and configuration.
"""

import pytest
import os
import tempfile
from app import create_app


class TestAppConfiguration:
    """Test cases for Flask app configuration."""
    
    def test_app_creation(self):
        """Test that Flask app can be created."""
        app = create_app()
        assert app is not None
        assert app.config['MAX_CONTENT_LENGTH'] == 16 * 1024 * 1024  # 16MB
        assert 'xlsx' in app.config['ALLOWED_EXTENSIONS']
    
    def test_upload_folder_creation(self):
        """Test that upload folder is created."""
        app = create_app()
        upload_folder = app.config['UPLOAD_FOLDER']
        assert os.path.exists(upload_folder)
    
    def test_allowed_file_function(self):
        """Test the allowed_file function."""
        from app import allowed_file
        
        # Valid files
        assert allowed_file('menu.xlsx') is True
        assert allowed_file('test_file.xlsx') is True
        
        # Invalid files
        assert allowed_file('menu.xls') is False
        assert allowed_file('menu.csv') is False
        assert allowed_file('menu.txt') is False
        assert allowed_file('menu') is False
        assert allowed_file('') is False


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_menu_endpoint_exists(self, client):
        """Test that menu endpoint exists and responds."""
        response = client.get('/api/menu')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'date' in data
        assert 'meals' in data
    
    def test_dates_endpoint_exists(self, client):
        """Test that dates endpoint exists and responds."""
        response = client.get('/api/dates')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'dates' in data
        assert 'count' in data
        assert 'dateRange' in data
        assert 'currentDate' in data
        assert 'hasCurrentDate' in data
    
    def test_upload_endpoint_exists(self, client):
        """Test that upload endpoint exists."""
        # Test without file (should return error)
        response = client.post('/api/upload')
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'No file provided' in data['message']
    
    def test_upload_endpoint_file_validation(self, client):
        """Test upload endpoint file validation."""
        # Test with invalid file type
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'test content')
            tmp.flush()
            tmp.close()  # Close file before opening again
            
            with open(tmp.name, 'rb') as test_file:
                response = client.post('/api/upload', data={
                    'file': (test_file, 'test.txt')
                })
            
            # Clean up after response is received
            try:
                os.unlink(tmp.name)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Invalid file format' in data['message']
    
    def test_upload_endpoint_empty_file(self, client):
        """Test upload endpoint with empty file."""
        # Test with empty file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            # Don't write anything to create empty file
            tmp.flush()
            tmp.close()  # Close file before opening again
            
            with open(tmp.name, 'rb') as test_file:
                response = client.post('/api/upload', data={
                    'file': (test_file, 'empty.xlsx')
                })
            
            # Clean up after response is received
            try:
                os.unlink(tmp.name)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Empty file not allowed' in data['message']
    
    def test_menu_endpoint_with_date_parameter(self, client):
        """Test menu endpoint with date parameter."""
        response = client.get('/api/menu?date=2023-12-15')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'date' in data
        assert 'meals' in data
    
    def test_menu_endpoint_invalid_date_format(self, client):
        """Test menu endpoint with invalid date format."""
        response = client.get('/api/menu?date=invalid-date')
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'status' in data or 'message' in data
        if 'status' in data:
            assert data['status'] == 'error'
        if 'message' in data:
            assert 'Invalid date format' in data['message']