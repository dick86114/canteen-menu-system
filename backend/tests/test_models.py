"""
Tests for menu data models.
"""

import pytest
from app.models.menu import MenuItem, Meal, MenuData
from app.models.storage import MenuStorage
from datetime import datetime


class TestMenuItem:
    """Test cases for MenuItem class."""
    
    def test_menu_item_creation(self):
        """Test basic MenuItem creation."""
        item = MenuItem(name="Chicken Rice", description="Delicious chicken with rice")
        assert item.name == "Chicken Rice"
        assert item.description == "Delicious chicken with rice"
        assert item.category is None
        assert item.price is None
    
    def test_menu_item_validation_valid(self):
        """Test MenuItem validation with valid data."""
        item = MenuItem(name="Beef Noodles", price=12.50)
        assert item.validate() is True
    
    def test_menu_item_validation_invalid_name(self):
        """Test MenuItem validation with invalid name."""
        item = MenuItem(name="")
        assert item.validate() is False
        
        item = MenuItem(name="   ")
        assert item.validate() is False
    
    def test_menu_item_validation_invalid_price(self):
        """Test MenuItem validation with invalid price."""
        item = MenuItem(name="Test Item", price=-5.0)
        assert item.validate() is False
    
    def test_menu_item_serialization(self):
        """Test MenuItem to_dict and from_dict."""
        item = MenuItem(name="Fish Curry", description="Spicy fish curry", category="main", price=15.0)
        item_dict = item.to_dict()
        
        expected = {
            'name': 'Fish Curry',
            'description': 'Spicy fish curry',
            'category': 'main',
            'price': 15.0
        }
        assert item_dict == expected
        
        # Test round trip
        restored_item = MenuItem.from_dict(item_dict)
        assert restored_item.name == item.name
        assert restored_item.description == item.description
        assert restored_item.category == item.category
        assert restored_item.price == item.price


class TestMeal:
    """Test cases for Meal class."""
    
    def test_meal_creation(self):
        """Test basic Meal creation."""
        meal = Meal(type="lunch", time="12:00")
        assert meal.type == "lunch"
        assert meal.time == "12:00"
        assert len(meal.items) == 0
    
    def test_meal_validation_valid(self):
        """Test Meal validation with valid data."""
        meal = Meal(type="breakfast", time="08:30")
        assert meal.validate() is True
    
    def test_meal_validation_invalid_type(self):
        """Test Meal validation with invalid type."""
        meal = Meal(type="snack", time="15:00")
        assert meal.validate() is False
    
    def test_meal_validation_invalid_time(self):
        """Test Meal validation with invalid time format."""
        meal = Meal(type="dinner", time="25:00")
        assert meal.validate() is False
        
        meal = Meal(type="dinner", time="invalid")
        assert meal.validate() is False
    
    def test_meal_add_item(self):
        """Test adding items to meal."""
        meal = Meal(type="lunch", time="12:00")
        item = MenuItem(name="Pasta")
        
        meal.add_item(item)
        assert len(meal.items) == 1
        assert meal.items[0].name == "Pasta"
    
    def test_meal_remove_item(self):
        """Test removing items from meal."""
        meal = Meal(type="lunch", time="12:00")
        item1 = MenuItem(name="Pasta")
        item2 = MenuItem(name="Salad")
        
        meal.add_item(item1)
        meal.add_item(item2)
        assert len(meal.items) == 2
        
        # Remove existing item
        result = meal.remove_item("Pasta")
        assert result is True
        assert len(meal.items) == 1
        assert meal.items[0].name == "Salad"
        
        # Try to remove non-existing item
        result = meal.remove_item("Pizza")
        assert result is False
        assert len(meal.items) == 1


class TestMenuData:
    """Test cases for MenuData class."""
    
    def test_menu_data_creation(self):
        """Test basic MenuData creation."""
        menu = MenuData(date="2023-12-15")
        assert menu.date == "2023-12-15"
        assert len(menu.meals) == 0
    
    def test_menu_data_validation_valid(self):
        """Test MenuData validation with valid data."""
        menu = MenuData(date="2023-12-15")
        assert menu.validate() is True
    
    def test_menu_data_validation_invalid_date(self):
        """Test MenuData validation with invalid date."""
        menu = MenuData(date="invalid-date")
        assert menu.validate() is False
        
        menu = MenuData(date="2023-13-01")  # Invalid month
        assert menu.validate() is False
    
    def test_menu_data_add_meal(self):
        """Test adding meals to menu data."""
        menu = MenuData(date="2023-12-15")
        meal = Meal(type="breakfast", time="08:00")
        
        menu.add_meal(meal)
        assert len(menu.meals) == 1
        assert menu.meals[0].type == "breakfast"
    
    def test_menu_data_get_meal_by_type(self):
        """Test getting meal by type."""
        menu = MenuData(date="2023-12-15")
        breakfast = Meal(type="breakfast", time="08:00")
        lunch = Meal(type="lunch", time="12:00")
        
        menu.add_meal(breakfast)
        menu.add_meal(lunch)
        
        found_breakfast = menu.get_meal_by_type("breakfast")
        assert found_breakfast is not None
        assert found_breakfast.type == "breakfast"
        
        found_dinner = menu.get_meal_by_type("dinner")
        assert found_dinner is None


class TestMenuStorage:
    """Test cases for MenuStorage class."""
    
    def test_storage_initialization(self):
        """Test MenuStorage initialization."""
        storage = MenuStorage()
        assert storage.get_menu_count() == 0
        assert len(storage.get_available_dates()) == 0
    
    def test_store_and_retrieve_menu(self):
        """Test storing and retrieving menu data."""
        storage = MenuStorage()
        menu = MenuData(date="2023-12-15")
        meal = Meal(type="lunch", time="12:00")
        menu.add_meal(meal)
        
        # Store menu
        result = storage.store_menu_data(menu)
        assert result is True
        assert storage.get_menu_count() == 1
        
        # Retrieve menu
        retrieved = storage.get_menu_by_date("2023-12-15")
        assert retrieved is not None
        assert retrieved.date == "2023-12-15"
        assert len(retrieved.meals) == 1
    
    def test_get_available_dates(self):
        """Test getting available dates."""
        storage = MenuStorage()
        
        # Add multiple menus
        dates = ["2023-12-15", "2023-12-14", "2023-12-16"]
        for date in dates:
            menu = MenuData(date=date)
            storage.store_menu_data(menu)
        
        available_dates = storage.get_available_dates()
        assert len(available_dates) == 3
        assert available_dates == sorted(dates)  # Should be sorted
    
    def test_get_most_recent_menu(self):
        """Test getting most recent menu."""
        storage = MenuStorage()
        
        # Add menus in random order
        dates = ["2023-12-14", "2023-12-16", "2023-12-15"]
        for date in dates:
            menu = MenuData(date=date)
            storage.store_menu_data(menu)
        
        most_recent = storage.get_most_recent_menu()
        assert most_recent is not None
        assert most_recent.date == "2023-12-16"  # Latest date
    
    def test_get_menu_or_fallback(self):
        """Test fallback menu retrieval."""
        storage = MenuStorage()
        
        # Add a menu
        menu = MenuData(date="2023-12-15")
        storage.store_menu_data(menu)
        
        # Request existing date
        result = storage.get_menu_or_fallback("2023-12-15")
        assert result is not None
        assert result.date == "2023-12-15"
        
        # Request non-existing date (should fallback)
        result = storage.get_menu_or_fallback("2023-12-20")
        assert result is not None
        assert result.date == "2023-12-15"  # Fallback to available menu
    
    def test_clear_all_data(self):
        """Test clearing all data."""
        storage = MenuStorage()
        
        # Add some data
        menu = MenuData(date="2023-12-15")
        storage.store_menu_data(menu)
        storage.add_uploaded_file("test.xlsx")
        
        assert storage.get_menu_count() == 1
        assert len(storage.get_uploaded_files()) == 1
        
        # Clear all data
        storage.clear_all_data()
        assert storage.get_menu_count() == 0
        assert len(storage.get_uploaded_files()) == 0