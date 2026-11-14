"""
SQLAlchemy model for the Crop entity.

Maps to the 'crops' table defined in init_db.sql.
Stores crop configuration with optimal moisture ranges and water requirements.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone

from ..database import Base


class Crop(Base):
    """
    ORM model representing a crop type and its water requirements.

    Attributes:
        id: Auto-incrementing primary key.
        crop_name: Unique name of the crop (e.g. 'Rice', 'Wheat').
        optimal_moisture_min: Minimum optimal soil moisture percentage.
        optimal_moisture_max: Maximum optimal soil moisture percentage.
        growth_stage: Current growth stage (vegetative, flowering, etc.).
        water_requirement_mm: Total water requirement in millimetres per season.
        season: Growing season (Kharif, Rabi, Annual).
        description: Detailed description of the crop and its needs.
        created_at: Timestamp when the record was created (UTC).
    """

    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    crop_name = Column(String(100), unique=True, nullable=False, index=True)
    optimal_moisture_min = Column(Float, nullable=False, default=30.0)
    optimal_moisture_max = Column(Float, nullable=False, default=70.0)
    growth_stage = Column(String(50), default="vegetative")
    water_requirement_mm = Column(Integer, default=500)
    season = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # A crop type can be planted in many fields
    fields = relationship("Field", back_populates="crop")

    def __repr__(self) -> str:
        return f"<Crop(id={self.id}, crop_name='{self.crop_name}')>"
