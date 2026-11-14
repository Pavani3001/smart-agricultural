"""
Pydantic schemas for sensor readings (time-series data).

Supports single-reading creation, batch ingestion, and response formatting.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SensorReadingCreate(BaseModel):
    """Schema for ingesting a single sensor reading."""

    sensor_id: str = Field(..., min_length=1, max_length=50, description="External sensor identifier")
    field_id: int = Field(..., description="Field ID where reading was taken")
    soil_moisture_percent: Optional[float] = Field(None, ge=0, le=100, description="Soil moisture %")
    temperature_celsius: Optional[float] = Field(None, ge=-50, le=60, description="Temperature in °C")
    is_simulated: bool = Field(False, description="Whether this is simulator-generated data")
    quality_flag: Optional[str] = Field("VALID", pattern="^(VALID|SIMULATED|INTERPOLATED|STALE|INVALID)$")
    timestamp: datetime = Field(..., description="UTC timestamp of the reading")


class SensorReadingBatchCreate(BaseModel):
    """Schema for batch-ingesting multiple sensor readings at once."""

    readings: List[SensorReadingCreate] = Field(
        ..., min_length=1, description="List of sensor readings to ingest"
    )


class SensorReadingResponse(BaseModel):
    """Schema for sensor reading data returned in API responses."""

    id: int
    sensor_id: str
    field_id: int
    soil_moisture_percent: Optional[float] = None
    temperature_celsius: Optional[float] = None
    is_simulated: bool = False
    quality_flag: Optional[str] = None
    timestamp: datetime
    ingested_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
