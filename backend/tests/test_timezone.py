"""
时区工具测试
"""

import os
import pytest
from datetime import datetime
from unittest.mock import patch
import pytz

from app.utils.timezone import (
    get_timezone,
    now,
    today_str,
    current_year,
    format_datetime,
    parse_date_with_timezone
)


class TestTimezone:
    """时区工具测试类"""
    
    def test_get_timezone_default(self):
        """测试默认时区获取"""
        with patch.dict(os.environ, {}, clear=True):
            tz = get_timezone()
            assert tz.zone == 'Asia/Shanghai'
    
    def test_get_timezone_from_env(self):
        """测试从环境变量获取时区"""
        with patch.dict(os.environ, {'TZ': 'America/New_York'}):
            tz = get_timezone()
            assert tz.zone == 'America/New_York'
    
    def test_get_timezone_invalid(self):
        """测试无效时区名称回退到默认"""
        with patch.dict(os.environ, {'TZ': 'Invalid/Timezone'}):
            tz = get_timezone()
            assert tz.zone == 'Asia/Shanghai'
    
    def test_now_returns_timezone_aware(self):
        """测试now()返回带时区信息的时间"""
        current_time = now()
        assert current_time.tzinfo is not None
        assert isinstance(current_time, datetime)
    
    def test_today_str_format(self):
        """测试today_str()返回正确格式"""
        today = today_str()
        # 验证格式为YYYY-MM-DD
        assert len(today) == 10
        assert today[4] == '-'
        assert today[7] == '-'
        # 验证可以解析为日期
        datetime.strptime(today, '%Y-%m-%d')
    
    def test_current_year(self):
        """测试current_year()返回当前年份"""
        year = current_year()
        assert isinstance(year, int)
        assert year >= 2023  # 假设测试在2023年之后运行
    
    def test_format_datetime_default(self):
        """测试format_datetime()默认参数"""
        formatted = format_datetime()
        # 验证返回ISO格式字符串
        assert isinstance(formatted, str)
        assert 'T' in formatted  # ISO格式包含T
    
    def test_format_datetime_with_param(self):
        """测试format_datetime()带参数"""
        # 创建一个带时区的时间
        tz = pytz.timezone('Asia/Shanghai')
        dt = tz.localize(datetime(2023, 12, 15, 10, 30, 0))
        
        formatted = format_datetime(dt)
        assert '2023-12-15T10:30:00' in formatted
    
    def test_format_datetime_naive(self):
        """测试format_datetime()处理无时区信息的时间"""
        # 创建无时区信息的时间
        dt = datetime(2023, 12, 15, 10, 30, 0)
        
        formatted = format_datetime(dt)
        assert '2023-12-15T10:30:00' in formatted
    
    def test_parse_date_with_timezone(self):
        """测试parse_date_with_timezone()"""
        date_str = '2023-12-15'
        dt = parse_date_with_timezone(date_str)
        
        assert dt.year == 2023
        assert dt.month == 12
        assert dt.day == 15
        assert dt.tzinfo is not None
    
    def test_timezone_consistency(self):
        """测试时区一致性"""
        # 确保所有函数使用相同的时区
        with patch.dict(os.environ, {'TZ': 'Europe/London'}):
            tz = get_timezone()
            current_time = now()
            parsed_date = parse_date_with_timezone('2023-12-15')
            
            assert current_time.tzinfo.zone == tz.zone
            assert parsed_date.tzinfo.zone == tz.zone