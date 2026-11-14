"""
SQLAlchemy model for the Sensor entity.

Maps to the 'sensors' table defined in init_db.sql.
Represents a physical sensor device installed in a field.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone

from ..database import Base


class Sensor(Base):
    """
    ORM model representing a sensor device.

    Uses a dual-id pattern:
      - `id`        — internal auto-incrementing primary key
      - `sensor_id` — external unique hardware identifier (e.g. 'SM-001')

    Attributes:
        id: Internal auto-incrementing PK.
        sensor_id: Unique hardware/external identifier for the sensor.
        field_id: Foreign key linking the sensor to a field.
        sensor_type: Type of measurement (soil_moisture, temperature, etc.).
        status: Operational status — active, inactive, maintenance, or error.
        last_reading_at: Timestamp of the most recent reading from this sensor.
        installed_at: When the sensor was physically installed.
        created_at: Record creation timestamp (UTC).
    """

    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sensor_id = Column(String(50), unique=True, nullable=False, index=True)
    field_id = Column(
        Integer,
        ForeignKey("fields.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sensor_type = Column(String(50), default="soil_moisture")
    status = Column(String(20), default="active")
    last_reading_at = Column(DateTime(timezone=True), nullable=True)
    installed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # Check constraint matching the SQL schema
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'maintenance', 'error')",
            name="ck_sensors_status",
        ),
    )

    # Relationships
    field = relationship("Field", back_populates="sensors")

    def __repr__(self) -> str:
        return f"<Sensor(id={self.id}, sensor_id='{self.sensor_id}', field_id={self.field_id})>"
