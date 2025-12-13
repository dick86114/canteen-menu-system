"""
Models package for the Canteen Menu System.
"""

from .menu import MenuItem, Meal, MenuData
from .storage import MenuStorage

# 创建全局存储实例（单例模式）
_storage_instance = None

def get_storage() -> MenuStorage:
    """
    获取全局存储实例（单例模式）
    
    Returns:
        MenuStorage: 全局存储实例
    """
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = MenuStorage()
    return _storage_instance

__all__ = ['MenuItem', 'Meal', 'MenuData', 'MenuStorage', 'get_storage']