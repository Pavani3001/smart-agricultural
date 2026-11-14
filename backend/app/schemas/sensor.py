"""
Pydantic schemas for the Sensor entity.

Defines request/response models for sensor CRUD operations.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SensorCreate(BaseModel):
    """Schema for registering a new sensor."""

    sensor_id: str = Field(..., min_length=1, max_length=50, description="Unique hardware sensor identifier")
    field_id: int = Field(..., description="ID of the field where the sensor is installed")
    sensor_type: Optional[str] = Field("soil_moisture", max_length=50)
    status: Optional[str] = Field("active", pattern="^(active|inactive|maintenance|error)$")


class SensorUpdate(BaseModel):
    """Schema for updating a sensor. All fields optional."""

    field_id: Optional[int] = None
    sensor_type: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, pattern="^(active|inactive|maintenance|error)$")


class SensorResponse(BaseModel):
    """Schema for sensor data returned in API responses."""

    id: int
    sensor_id: str
    field_id: int
    sensor_type: Optional[str] = None
    status: Optional[str] = None
    last_reading_at: Optional[datetime] = None
    installed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
