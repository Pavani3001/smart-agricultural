"""
API routers package.
"""

from .farmers import router as farmers_router
from .fields import router as fields_router
from .crops import router as crops_router
from .sensors import router as sensors_router
from .sensor_data import router as sensor_data_router
from .weather import router as weather_router

__all__ = [
    "farmers_router",
    "fields_router",
    "crops_router",
    "sensors_router",
    "sensor_data_router",
    "weather_router",
]

