"""
BluedonuLab API Module
REST API 엔드포인트
"""

from . import personality_routes
from . import matching_routes
from . import report_routes

__all__ = [
    'personality_routes',
    'matching_routes',
    'report_routes'
]
