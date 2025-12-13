"""
In-memory storage for menu data.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from .menu import MenuData, Meal
import threading


class MenuStorage:
    """
    In-memory storage class for managing menu data.
    
    This class provides thread-safe operations for storing and retrieving
    menu data. It maintains data in memory and provides methods for
    CRUD operations on menu data.
    """
    
    def __init__(self):
        """Initialize the storage with empty data structures."""
        self._menu_data: Dict[str, MenuData] = {}
        self._uploaded_files: List[str] = []
        self._lock = threading.RLock()  # Reentrant lock for thread safety
    
    def store_menu_data(self, menu_data: MenuData) -> bool:
        """
        Store menu data for a specific date.
        
        Args:
            menu_data: MenuData object to store
            
        Returns:
            True if stored successfully, False if validation failed
        """
        if not menu_data.validate():
            return False
            
        with self._lock:
            self._menu_data[menu_data.date] = menu_data
            return True
    
    def get_menu_by_date(self, date_str: str) -> Optional[MenuData]:
        """
        Retrieve menu data for a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            MenuData object if found, None otherwise
        """
        with self._lock:
            return self._menu_data.get(date_str)
    
    def get_available_dates(self) -> List[str]:
        """
        Get list of all available menu dates.
        
        Returns:
            Sorted list of date strings in YYYY-MM-DD format
        """
        with self._lock:
            dates = list(self._menu_data.keys())
            return sorted(dates)
    
    def get_date_range(self) -> Optional[Tuple[str, str]]:
        """
        Get the date range of available menus.
        
        Returns:
            Tuple of (start_date, end_date) or None if no data
        """
        dates = self.get_available_dates()
        if not dates:
            return None
        return (dates[0], dates[-1])
    
    def get_most_recent_menu(self) -> Optional[MenuData]:
        """
        Get the most recent menu data available.
        
        Returns:
            MenuData object for the most recent date, None if no data
        """
        dates = self.get_available_dates()
        if not dates:
            return None
        
        most_recent_date = dates[-1]
        return self.get_menu_by_date(most_recent_date)
    
    def get_menu_or_fallback(self, date_str: str) -> Optional[MenuData]:
        """
        Get menu for specific date, or fallback to most recent if not found.
        
        Args:
            date_str: Requested date in YYYY-MM-DD format
            
        Returns:
            MenuData object for requested date or most recent available
        """
        menu = self.get_menu_by_date(date_str)
        if menu is not None:
            return menu
        
        # Fallback to most recent menu
        return self.get_most_recent_menu()
    
    def update_menu_data(self, date_str: str, meals: List[Meal]) -> bool:
        """
        Update menu data for a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            meals: List of Meal objects
            
        Returns:
            True if updated successfully, False otherwise
        """
        menu_data = MenuData(date=date_str, meals=meals)
        return self.store_menu_data(menu_data)
    
    def delete_menu_data(self, date_str: str) -> bool:
        """
        Delete menu data for a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            True if deleted, False if date not found
        """
        with self._lock:
            if date_str in self._menu_data:
                del self._menu_data[date_str]
                return True
            return False
    
    def clear_all_data(self) -> None:
        """Clear all stored menu data."""
        with self._lock:
            self._menu_data.clear()
            self._uploaded_files.clear()
    
    def add_uploaded_file(self, filename: str) -> None:
        """
        Track an uploaded file.
        
        Args:
            filename: Name of the uploaded file
        """
        with self._lock:
            if filename not in self._uploaded_files:
                self._uploaded_files.append(filename)
    
    def get_uploaded_files(self) -> List[str]:
        """
        Get list of uploaded files.
        
        Returns:
            List of uploaded file names
        """
        with self._lock:
            return self._uploaded_files.copy()
    
    def get_menu_count(self) -> int:
        """
        Get total number of stored menus.
        
        Returns:
            Number of menu dates stored
        """
        with self._lock:
            return len(self._menu_data)
    
    def has_menu_for_date(self, date_str: str) -> bool:
        """
        Check if menu exists for a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            True if menu exists for the date, False otherwise
        """
        with self._lock:
            return date_str in self._menu_data
    
    def get_all_menu_data(self) -> Dict[str, MenuData]:
        """
        Get all stored menu data.
        
        Returns:
            Dictionary mapping dates to MenuData objects
        """
        with self._lock:
            return self._menu_data.copy()


# Global storage instance
menu_storage = MenuStorage()