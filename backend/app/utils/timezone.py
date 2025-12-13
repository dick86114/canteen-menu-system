"""
时区处理工具模块

提供统一的时区处理功能，支持Docker环境变量配置
"""

import os
from datetime import datetime, timezone
from typing import Optional
import pytz


def get_timezone() -> pytz.BaseTzInfo:
    """
    获取当前时区
    
    优先级：
    1. 环境变量 TZ
    2. 默认使用 Asia/Shanghai
    
    Returns:
        pytz时区对象
    """
    tz_name = os.environ.get('TZ', 'Asia/Shanghai')
    try:
        return pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        # 如果时区名称无效，回退到上海时区
        return pytz.timezone('Asia/Shanghai')


def now() -> datetime:
    """
    获取当前时区的当前时间
    
    Returns:
        带时区信息的当前时间
    """
    tz = get_timezone()
    return datetime.now(tz)


def today_str() -> str:
    """
    获取当前日期的字符串表示（YYYY-MM-DD格式）
    
    Returns:
        当前日期字符串
    """
    return now().strftime('%Y-%m-%d')


def current_year() -> int:
    """
    获取当前年份
    
    Returns:
        当前年份
    """
    return now().year


def format_datetime(dt: Optional[datetime] = None) -> str:
    """
    格式化日期时间为ISO字符串
    
    Args:
        dt: 要格式化的日期时间，如果为None则使用当前时间
        
    Returns:
        ISO格式的日期时间字符串
    """
    if dt is None:
        dt = now()
    elif dt.tzinfo is None:
        # 如果没有时区信息，假设是当前时区
        tz = get_timezone()
        dt = tz.localize(dt)
    
    return dt.isoformat()


def parse_date_with_timezone(date_str: str) -> datetime:
    """
    解析日期字符串并添加当前时区信息
    
    Args:
        date_str: 日期字符串（YYYY-MM-DD格式）
        
    Returns:
        带时区信息的日期时间对象
    """
    # 解析日期字符串
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    
    # 添加当前时区信息
    tz = get_timezone()
    return tz.localize(dt)