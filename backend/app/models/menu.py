"""
Menu data models for the Canteen Menu System.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class MenuItem:
    """
    Represents a single menu item (food dish).
    
    Attributes:
        name: Name of the food item
        description: Optional description of the item
        category: Optional category (e.g., 'main', 'side', 'dessert')
        price: Optional price of the item
        order: Order index for sorting (based on Excel position)
        category_order: Order index of the category for sorting
    """
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    order: int = 0
    category_order: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert MenuItem to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'order': self.order,
            'category_order': self.category_order
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MenuItem':
        """Create MenuItem from dictionary."""
        return cls(
            name=data['name'],
            description=data.get('description'),
            category=data.get('category'),
            price=data.get('price'),
            order=data.get('order', 0),
            category_order=data.get('category_order', 0)
        )
    
    def validate(self) -> bool:
        """
        Validate MenuItem data.
        
        Returns:
            True if valid, False otherwise
        """
        if not self.name or not isinstance(self.name, str) or not self.name.strip():
            return False
        
        if self.price is not None and (not isinstance(self.price, (int, float)) or self.price < 0):
            return False
            
        return True


@dataclass
class Meal:
    """
    Represents a meal (breakfast, lunch, dinner) with its items.
    
    Attributes:
        type: Type of meal ('breakfast', 'lunch', 'dinner')
        time: Time of the meal in HH:MM format
        items: List of MenuItem objects for this meal
    """
    type: str
    time: str
    items: List[MenuItem] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Meal to dictionary for serialization."""
        # 对菜品按分类顺序和菜品顺序排序
        sorted_items = sorted(self.items, key=lambda item: (item.category_order, item.order))
        
        return {
            'type': self.type,
            'time': self.time,
            'items': [item.to_dict() for item in sorted_items]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Meal':
        """Create Meal from dictionary."""
        items = [MenuItem.from_dict(item_data) for item_data in data.get('items', [])]
        return cls(
            type=data['type'],
            time=data['time'],
            items=items
        )
    
    def validate(self) -> bool:
        """
        Validate Meal data.
        
        Returns:
            True if valid, False otherwise
        """
        # Validate meal type
        valid_types = {'breakfast', 'lunch', 'dinner'}
        if self.type not in valid_types:
            return False
        
        # Validate time format (HH:MM)
        try:
            datetime.strptime(self.time, '%H:%M')
        except ValueError:
            return False
        
        # Validate all items
        for item in self.items:
            if not item.validate():
                return False
                
        return True
    
    def add_item(self, item: MenuItem) -> None:
        """Add a menu item to this meal."""
        if item.validate():
            self.items.append(item)
    
    def remove_item(self, item_name: str) -> bool:
        """
        Remove a menu item by name.
        
        Args:
            item_name: Name of the item to remove
            
        Returns:
            True if item was found and removed, False otherwise
        """
        for i, item in enumerate(self.items):
            if item.name == item_name:
                del self.items[i]
                return True
        return False


@dataclass
class MenuData:
    """
    Represents menu data for a specific date.
    
    Attributes:
        date: Date in YYYY-MM-DD format
        meals: List of Meal objects for this date
    """
    date: str
    meals: List[Meal] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert MenuData to dictionary for serialization."""
        # 对餐次按时间排序
        sorted_meals = sorted(self.meals, key=lambda meal: meal.time)
        
        return {
            'date': self.date,
            'meals': [meal.to_dict() for meal in sorted_meals]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MenuData':
        """Create MenuData from dictionary."""
        meals = [Meal.from_dict(meal_data) for meal_data in data.get('meals', [])]
        return cls(
            date=data['date'],
            meals=meals
        )
    
    def to_json(self) -> str:
        """Convert MenuData to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MenuData':
        """Create MenuData from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def validate(self) -> bool:
        """
        Validate MenuData.
        
        Returns:
            True if valid, False otherwise
        """
        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(self.date, '%Y-%m-%d')
        except ValueError:
            return False
        
        # Validate all meals
        for meal in self.meals:
            if not meal.validate():
                return False
                
        return True
    
    def add_meal(self, meal: Meal) -> None:
        """Add a meal to this menu date."""
        if meal.validate():
            self.meals.append(meal)
    
    def get_meal_by_type(self, meal_type: str) -> Optional[Meal]:
        """
        Get meal by type.
        
        Args:
            meal_type: Type of meal to find
            
        Returns:
            Meal object if found, None otherwise
        """
        for meal in self.meals:
            if meal.type == meal_type:
                return meal
        return None
    
    def get_meals_sorted_by_time(self) -> List[Meal]:
        """
        Get meals sorted by time.
        
        Returns:
            List of meals sorted by time
        """
        return sorted(self.meals, key=lambda meal: meal.time)