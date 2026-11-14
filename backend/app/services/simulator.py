"""
Sensor data simulator service.

Generates realistic synthetic sensor readings using a random-walk model
for soil moisture and temperature. All simulated data is clearly marked
with is_simulated=True and quality_flag='SIMULATED'.
"""

import logging
import random
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.orm import Session

from ..models.sensor import Sensor
from ..models.sensor_reading import SensorReading
from ..schemas.sensor_reading import SensorReadingCreate
from .sensor_service import ingest_batch_readings

logger = logging.getLogger(__name__)

# ── Simulation parameters ──────────────────────────────────────────────────

# Soil moisture range
MOISTURE_MIN = 20.0
MOISTURE_MAX = 85.0

# Temperature range
TEMP_BASE_MIN = 15.0
TEMP_BASE_MAX = 40.0

# Random walk step sizes
MOISTURE_STEP_MAX = 2.5  # Max % change per 15-min interval
TEMP_STEP_MAX = 0.5  # Max °C change per 15-min interval

# Default simulation period
DEFAULT_DAYS = 7
INTERVAL_MINUTES = 15


def generate_simulated_readings(
    db: Session,
    sensor_id_str: str,
    days: int = DEFAULT_DAYS,
    interval_minutes: int = INTERVAL_MINUTES,
) -> List[SensorReading]:
    """
    Generate and ingest realistic simulated sensor data for the past N days.

    Uses a random-walk model to create gradual, realistic changes in
    soil moisture and temperature. Includes a daily temperature cycle
    pattern for added realism.

    All generated readings have:
        - is_simulated = True
        - quality_flag = 'SIMULATED'

    Args:
        db: Active database session.
        sensor_id_str: External sensor identifier to simulate for.
        days: Number of past days to generate data for (default 7).
        interval_minutes: Minutes between consecutive readings (default 15).

    Returns:
        List of persisted SensorReading ORM instances.

    Raises:
        ValueError: If the sensor_id does not exist in the database.
    """
    # Look up the sensor to get its field_id
    sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id_str).first()
    if not sensor:
        raise ValueError(f"Sensor '{sensor_id_str}' not found")

    field_id = sensor.field_id
    logger.info(
        "Generating %d days of simulated data for sensor %s (field %d)",
        days,
        sensor_id_str,
        field_id,
    )

    # Calculate time range
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=days)

    # Initialize random walk starting values
    current_moisture = random.uniform(MOISTURE_MIN + 10, MOISTURE_MAX - 10)
    current_temp = random.uniform(TEMP_BASE_MIN + 5, TEMP_BASE_MAX - 5)

    readings: List[SensorReadingCreate] = []
    current_time = start_time

    while current_time <= now:
        # Random-walk for soil moisture — gradual changes
        moisture_delta = random.uniform(-MOISTURE_STEP_MAX, MOISTURE_STEP_MAX)
        current_moisture += moisture_delta
        # Clamp to valid range and add slight mean reversion
        if current_moisture < MOISTURE_MIN + 5:
            current_moisture += abs(moisture_delta)  # Push up
        elif current_moisture > MOISTURE_MAX - 5:
            current_moisture -= abs(moisture_delta)  # Push down
        current_moisture = max(MOISTURE_MIN, min(MOISTURE_MAX, current_moisture))

        # Temperature with daily cycle: warmer during day (6-18h), cooler at night
        hour = current_time.hour
        # Sinusoidal daily pattern: peaks at ~14:00, low at ~02:00
        daily_offset = 5.0 * _daily_temp_factor(hour)
        temp_delta = random.uniform(-TEMP_STEP_MAX, TEMP_STEP_MAX)
        current_temp += temp_delta
        # Clamp temperature
        current_temp = max(TEMP_BASE_MIN, min(TEMP_BASE_MAX, current_temp))
        display_temp = current_temp + daily_offset

        reading = SensorReadingCreate(
            sensor_id=sensor_id_str,
            field_id=field_id,
            soil_moisture_percent=round(current_moisture, 2),
            temperature_celsius=round(display_temp, 2),
            is_simulated=True,
            quality_flag="SIMULATED",
            timestamp=current_time,
        )
        readings.append(reading)

        current_time += timedelta(minutes=interval_minutes)

    logger.info("Generated %d simulated readings", len(readings))

    # Use the batch ingestion service (applies cleaning pipeline)
    stored_readings = ingest_batch_readings(db, readings)
    return stored_readings


def _daily_temp_factor(hour: int) -> float:
    """
    Compute a daily temperature factor based on hour of day.

    Returns a value between -1.0 (coldest, ~02:00) and +1.0 (warmest, ~14:00)
    using a simple sinusoidal approximation.

    Args:
        hour: Hour of the day (0-23).

    Returns:
        Temperature adjustment factor.
    """
    import math

    # Peak at hour 14, trough at hour 2
    # Shift: sin((hour - 8) * pi / 12) gives peak at 14, trough at 2
    return math.sin((hour - 8) * math.pi / 12)
