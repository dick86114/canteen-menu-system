"""
Integration tests for API endpoints.
"""

import pytest
import tempfile
import os
from app import create_app
from app.models import get_storage
from app.models.menu import MenuData, Meal, MenuItem


class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client with clean storage."""
        app = create_app()
        app.config['TESTING'] = True
        
        # Clear storage before each test
        storage = get_storage()
        storage.clear_all_data()
        
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def sample_menu_data(self):
        """Create sample menu data for testing."""
        menu_item = MenuItem(
            name="Test Food",
            description="Test Description",
            category="Main Course"
        )
        
        meal = Meal(
            type="lunch",
            time="12:00",
            items=[menu_item]
        )
        
        menu_data = MenuData(
            date="2023-12-15",
            meals=[meal]
        )
        
        return menu_data
    
    def test_menu_retrieval_with_stored_data(self, client, sample_menu_data):
        """Test menu retrieval when data exists."""
        # Store sample data
        storage = get_storage()
        storage.store_menu_data(sample_menu_data)
        
        # Test specific date retrieval
        response = client.get('/api/menu?date=2023-12-15')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['date'] == '2023-12-15'
        assert len(data['meals']) == 1
        assert data['meals'][0]['type'] == 'lunch'
        assert data['meals'][0]['items'][0]['name'] == 'Test Food'
    
    def test_menu_fallback_behavior(self, client, sample_menu_data):
        """Test menu fallback to most recent when requested date not found."""
        # Store sample data
        storage = get_storage()
        storage.store_menu_data(sample_menu_data)
        
        # Request different date (should fallback)
        response = client.get('/api/menu?date=2023-12-20')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['date'] == '2023-12-15'  # Fallback date
        assert data.get('fallback') is True
        assert data.get('requestedDate') == '2023-12-20'
        assert 'most recent menu' in data.get('message', '')
    
    def test_dates_endpoint_with_data(self, client, sample_menu_data):
        """Test dates endpoint when data exists."""
        # Store sample data
        storage = get_storage()
        storage.store_menu_data(sample_menu_data)
        
        response = client.get('/api/dates')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['count'] == 1
        assert '2023-12-15' in data['dates']
        assert data['dateRange']['start'] == '2023-12-15'
        assert data['dateRange']['end'] == '2023-12-15'
        assert data['mostRecentDate'] == '2023-12-15'
    
    def test_empty_storage_behavior(self, client):
        """Test API behavior when no data is stored."""
        # Test menu endpoint with empty storage
        response = client.get('/api/menu')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['meals'] == []
        assert 'No menu data available' in data.get('message', '')
        
        # Test dates endpoint with empty storage
        response = client.get('/api/dates')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['count'] == 0
        assert data['dates'] == []
        assert data['dateRange']['start'] is None
        assert data['dateRange']['end'] is None