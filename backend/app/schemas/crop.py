"""
Pydantic schemas for the Crop entity.

Defines request/response models for crop CRUD operations.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CropCreate(BaseModel):
    """Schema for creating a new crop type."""

    crop_name: str = Field(..., min_length=1, max_length=100, description="Unique crop name")
    optimal_moisture_min: float = Field(30.0, ge=0, le=100, description="Min optimal soil moisture %")
    optimal_moisture_max: float = Field(70.0, ge=0, le=100, description="Max optimal soil moisture %")
    growth_stage: Optional[str] = Field("vegetative", max_length=50)
    water_requirement_mm: Optional[int] = Field(500, ge=0)
    season: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class CropUpdate(BaseModel):
    """Schema for updating a crop. All fields optional."""

    crop_name: Optional[str] = Field(None, min_length=1, max_length=100)
    optimal_moisture_min: Optional[float] = Field(None, ge=0, le=100)
    optimal_moisture_max: Optional[float] = Field(None, ge=0, le=100)
    growth_stage: Optional[str] = Field(None, max_length=50)
    water_requirement_mm: Optional[int] = Field(None, ge=0)
    season: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class CropResponse(BaseModel):
    """Schema for crop data returned in API responses."""

    id: int
    crop_name: str
    optimal_moisture_min: float
    optimal_moisture_max: float
    growth_stage: Optional[str] = None
    water_requirement_mm: Optional[int] = None
    season: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
