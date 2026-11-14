"""
SQLAlchemy model for the WeatherData entity.

Maps to the 'weather_data' hypertable defined in init_db.sql.
Stores time-series weather data fetched from OpenWeatherMap.
"""

from sqlalchemy import Column, BigInteger, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from datetime import datetime, timezone

from ..database import Base


class WeatherData(Base):
    """
    ORM model for a weather observation record.

    This table is a TimescaleDB hypertable partitioned by `timestamp`.

    Attributes:
        id: Auto-incrementing big integer PK.
        field_id: The field this weather data applies to.
        temperature_celsius: Air temperature in °C.
        humidity_percent: Relative humidity percentage.
        rainfall_mm: Precipitation in millimetres.
        wind_speed_ms: Wind speed in metres per second.
        weather_condition: Short weather label (e.g. 'Clear', 'Rain').
        description: Extended weather description from the API.
        data_source: Provider of the data (default: 'openweathermap').
        timestamp: UTC timestamp of the observation.
        fetched_at: UTC timestamp when the data was stored.
    """

    __tablename__ = "weather_data"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    field_id = Column(Integer, nullable=False, index=True)
    temperature_celsius = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)
    rainfall_mm = Column(Float, default=0.0)
    wind_speed_ms = Column(Float, nullable=True)
    weather_condition = Column(String(50), nullable=True)
    description = Column(String(200), nullable=True)
    data_source = Column(String(50), default="openweathermap")
    timestamp = Column(DateTime(timezone=True), nullable=False)
    fetched_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<WeatherData(id={self.id}, field_id={self.field_id}, "
            f"temp={self.temperature_celsius}°C, ts={self.timestamp})>"
        )
