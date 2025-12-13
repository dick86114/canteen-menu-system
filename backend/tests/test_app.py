"""
Tests for Flask application setup and configuration.
"""

import pytest
from app import create_app


class TestAppConfiguration:
    """Test cases for Flask app configuration."""
    
    def test_app_creation(self):
        """Test that Flask app can be created."""
        app = create_app()
        assert app is not None


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