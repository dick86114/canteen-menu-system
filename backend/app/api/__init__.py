"""
API blueprints for the Canteen Menu System.
"""

from .menu import menu_bp
from .upload import upload_bp

__all__ = ['menu_bp', 'upload_bp']