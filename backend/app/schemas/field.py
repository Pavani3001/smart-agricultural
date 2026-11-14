"""
Pydantic schemas for the Field entity.

Defines request/response models for field CRUD operations.
The FieldResponse includes nested sensor data for convenience.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from .sensor import SensorResponse


class FieldCreate(BaseModel):
    """Schema for creating a new field."""

    farmer_id: int = Field(..., description="Owning farmer's ID")
    crop_id: Optional[int] = Field(None, description="Planted crop ID")
    field_name: str = Field(..., min_length=1, max_length=100, description="Human-readable field name")
    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")
    area_hectares: float = Field(1.0, gt=0, description="Field area in hectares")
    crop_type: Optional[str] = Field(None, max_length=100)
    soil_type: Optional[str] = Field("loamy", max_length=50)
    status: Optional[str] = Field("active", pattern="^(active|inactive|fallow)$")


class FieldUpdate(BaseModel):
    """Schema for updating a field. All fields optional."""

    farmer_id: Optional[int] = None
    crop_id: Optional[int] = None
    field_name: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    area_hectares: Optional[float] = Field(None, gt=0)
    crop_type: Optional[str] = Field(None, max_length=100)
    soil_type: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, pattern="^(active|inactive|fallow)$")


class FieldResponse(BaseModel):
    """Schema for field data returned in API responses, includes nested sensors."""

    id: int
    farmer_id: int
    crop_id: Optional[int] = None
    field_name: str
    latitude: float
    longitude: float
    area_hectares: float
    crop_type: Optional[str] = None
    soil_type: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    sensors: List[SensorResponse] = []

    model_config = {"from_attributes": True}
