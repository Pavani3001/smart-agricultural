"""
SQLAlchemy model for the Field entity.

Maps to the 'fields' table defined in init_db.sql.
Represents a physical agricultural field with GPS coordinates,
linked to a farmer (owner) and optionally a crop.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone

from ..database import Base


class Field(Base):
    """
    ORM model representing an agricultural field.

    Attributes:
        id: Auto-incrementing primary key.
        farmer_id: Foreign key to the owning farmer.
        crop_id: Optional foreign key to the planted crop.
        field_name: Human-readable name for the field.
        latitude: GPS latitude (double precision).
        longitude: GPS longitude (double precision).
        area_hectares: Field area in hectares.
        crop_type: Legacy/free-text crop type string.
        soil_type: Soil classification (loamy, clay, sandy, etc.).
        status: Field status — active, inactive, or fallow.
        created_at: Record creation timestamp (UTC).
        updated_at: Last update timestamp (UTC).
    """

    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farmer_id = Column(
        Integer,
        ForeignKey("farmers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crop_id = Column(
        Integer,
        ForeignKey("crops.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    field_name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    area_hectares = Column(Float, nullable=False, default=1.0)
    crop_type = Column(String(100), nullable=True)
    soil_type = Column(String(50), default="loamy")
    status = Column(String(20), default="active")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        default=lambda: datetime.now(timezone.utc),
    )

    # Check constraint matching the SQL schema
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'fallow')",
            name="ck_fields_status",
        ),
    )

    # Relationships
    farmer = relationship("Farmer", back_populates="fields")
    crop = relationship("Crop", back_populates="fields")
    sensors = relationship("Sensor", back_populates="field", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Field(id={self.id}, field_name='{self.field_name}', farmer_id={self.farmer_id})>"
