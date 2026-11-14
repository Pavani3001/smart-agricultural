"""
Pydantic schemas for weather data.

Defines response models for weather observations and fetch results.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class WeatherDataResponse(BaseModel):
    """Schema for a single weather observation returned in API responses."""

    id: int
    field_id: int
    temperature_celsius: Optional[float] = None
    humidity_percent: Optional[float] = None
    rainfall_mm: Optional[float] = 0.0
    wind_speed_ms: Optional[float] = None
    weather_condition: Optional[str] = None
    description: Optional[str] = None
    data_source: Optional[str] = "openweathermap"
    timestamp: datetime
    fetched_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class WeatherFetchResponse(BaseModel):
    """
    Schema for the result of a weather-fetch operation.

    Wraps the stored weather record with fetch metadata.
    """

    success: bool = Field(..., description="Whether the fetch succeeded")
    message: str = Field(..., description="Human-readable status message")
    data: Optional[WeatherDataResponse] = Field(None, description="The fetched weather data")
    is_stale: bool = Field(False, description="True if returning cached/last-known data after API failure")
