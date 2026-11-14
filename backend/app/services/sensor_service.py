"""
Sensor data ingestion service.

Handles single and batch ingestion of sensor readings, applying data
cleaning/validation before storage. Also provides historical query methods.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from ..models.sensor import Sensor
from ..models.sensor_reading import SensorReading
from ..schemas.sensor_reading import SensorReadingCreate
from .data_cleaning import (
    validate_sensor_reading,
    detect_duplicates,
    normalize_reading,
    clean_batch,
    FLAG_INVALID,
)

logger = logging.getLogger(__name__)


def ingest_single_reading(
    db: Session,
    reading_data: SensorReadingCreate,
) -> SensorReading:
    """
    Ingest a single sensor reading after validation and cleaning.

    Steps:
        1. Validate the reading values against physical limits.
        2. Check for duplicates (same sensor + timestamp within 1 s).
        3. Normalize values to correct ranges.
        4. Store the reading and update the sensor's last_reading_at.

    Args:
        db: Active database session.
        reading_data: The incoming sensor reading data.

    Returns:
        The persisted SensorReading ORM instance.

    Raises:
        ValueError: If the reading is a duplicate.
    """
    # Step 1: Validate
    is_valid, quality_flag, reason = validate_sensor_reading(
        reading_data.soil_moisture_percent,
        reading_data.temperature_celsius,
    )

    # Preserve existing quality_flag if provided (e.g., SIMULATED)
    final_flag = reading_data.quality_flag or quality_flag
    if not is_valid and final_flag == "VALID":
        final_flag = FLAG_INVALID
        logger.warning("Invalid reading for sensor %s: %s", reading_data.sensor_id, reason)

    # Step 2: Check for duplicates
    existing_timestamps = _get_recent_timestamps(db, reading_data.sensor_id)
    if detect_duplicates(reading_data.sensor_id, reading_data.timestamp, existing_timestamps):
        raise ValueError(
            f"Duplicate reading detected for sensor {reading_data.sensor_id} "
            f"at {reading_data.timestamp}"
        )

    # Step 3: Normalize
    norm_moisture, norm_temp = normalize_reading(
        reading_data.soil_moisture_percent,
        reading_data.temperature_celsius,
    )

    # Step 4: Create and store the reading
    db_reading = SensorReading(
        sensor_id=reading_data.sensor_id,
        field_id=reading_data.field_id,
        soil_moisture_percent=norm_moisture,
        temperature_celsius=norm_temp,
        is_simulated=reading_data.is_simulated,
        quality_flag=final_flag,
        timestamp=reading_data.timestamp,
    )
    db.add(db_reading)

    # Update the sensor's last_reading_at timestamp
    _update_sensor_last_reading(db, reading_data.sensor_id, reading_data.timestamp)

    db.commit()
    db.refresh(db_reading)

    logger.info(
        "Ingested reading for sensor %s: moisture=%.1f%%, temp=%.1f°C, flag=%s",
        reading_data.sensor_id,
        norm_moisture or 0,
        norm_temp or 0,
        final_flag,
    )
    return db_reading


def ingest_batch_readings(
    db: Session,
    readings: List[SensorReadingCreate],
) -> List[SensorReading]:
    """
    Ingest a batch of sensor readings with pandas-based cleaning.

    Steps:
        1. Convert to DataFrame for batch processing.
        2. Run the full cleaning pipeline (validate, normalize, gap detection).
        3. Store all cleaned readings.
        4. Update each sensor's last_reading_at.

    Args:
        db: Active database session.
        readings: List of sensor reading data objects.

    Returns:
        List of persisted SensorReading ORM instances.
    """
    if not readings:
        return []

    # Convert to DataFrame for batch cleaning
    records = [
        {
            "sensor_id": r.sensor_id,
            "field_id": r.field_id,
            "soil_moisture_percent": r.soil_moisture_percent,
            "temperature_celsius": r.temperature_celsius,
            "is_simulated": r.is_simulated,
            "quality_flag": r.quality_flag or "VALID",
            "timestamp": r.timestamp,
        }
        for r in readings
    ]
    df = pd.DataFrame(records)

    # Run batch cleaning
    df = clean_batch(df)

    # Store all cleaned readings
    db_readings: List[SensorReading] = []
    # Track latest timestamp per sensor for batch update
    latest_ts: dict[str, datetime] = {}

    for _, row in df.iterrows():
        db_reading = SensorReading(
            sensor_id=row["sensor_id"],
            field_id=int(row["field_id"]),
            soil_moisture_percent=row["soil_moisture_percent"],
            temperature_celsius=row["temperature_celsius"],
            is_simulated=bool(row["is_simulated"]),
            quality_flag=row["quality_flag"],
            timestamp=row["timestamp"],
        )
        db.add(db_reading)
        db_readings.append(db_reading)

        # Track the most recent timestamp per sensor
        sid = row["sensor_id"]
        ts = row["timestamp"]
        if sid not in latest_ts or ts > latest_ts[sid]:
            latest_ts[sid] = ts

    # Batch-update sensor last_reading_at
    for sid, ts in latest_ts.items():
        _update_sensor_last_reading(db, sid, ts)

    db.commit()

    # Refresh all to get DB-generated fields (id, ingested_at)
    for r in db_readings:
        db.refresh(r)

    logger.info("Batch ingested %d readings across %d sensor(s)", len(db_readings), len(latest_ts))
    return db_readings


def get_sensor_readings(
    db: Session,
    sensor_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> List[SensorReading]:
    """
    Query historical readings for a specific sensor.

    Args:
        db: Active database session.
        sensor_id: External sensor identifier.
        start_time: Inclusive start of the time range (UTC).
        end_time: Inclusive end of the time range (UTC).

    Returns:
        List of SensorReading records ordered by timestamp descending.
    """
    query = db.query(SensorReading).filter(SensorReading.sensor_id == sensor_id)

    if start_time:
        query = query.filter(SensorReading.timestamp >= start_time)
    if end_time:
        query = query.filter(SensorReading.timestamp <= end_time)

    return query.order_by(SensorReading.timestamp.desc()).all()


def get_field_readings(
    db: Session,
    field_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> List[SensorReading]:
    """
    Query all sensor readings for a field.

    Args:
        db: Active database session.
        field_id: The field ID.
        start_time: Inclusive start of the time range (UTC).
        end_time: Inclusive end of the time range (UTC).

    Returns:
        List of SensorReading records ordered by timestamp descending.
    """
    query = db.query(SensorReading).filter(SensorReading.field_id == field_id)

    if start_time:
        query = query.filter(SensorReading.timestamp >= start_time)
    if end_time:
        query = query.filter(SensorReading.timestamp <= end_time)

    return query.order_by(SensorReading.timestamp.desc()).all()


# ── Private helpers ────────────────────────────────────────────────────────


def _get_recent_timestamps(db: Session, sensor_id: str, limit: int = 10) -> List[datetime]:
    """
    Fetch the most recent timestamps for a sensor (for duplicate detection).

    Args:
        db: Active database session.
        sensor_id: External sensor identifier.
        limit: Max number of recent timestamps to return.

    Returns:
        List of datetime timestamps.
    """
    rows = (
        db.query(SensorReading.timestamp)
        .filter(SensorReading.sensor_id == sensor_id)
        .order_by(SensorReading.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [row.timestamp for row in rows]


def _update_sensor_last_reading(
    db: Session, sensor_id: str, timestamp: datetime
) -> None:
    """
    Update the sensor's last_reading_at to the given timestamp,
    only if the new timestamp is more recent.

    Args:
        db: Active database session.
        sensor_id: External sensor identifier.
        timestamp: Timestamp to potentially set.
    """
    sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
    if sensor:
        if sensor.last_reading_at is None:
            sensor.last_reading_at = timestamp
        else:
            ts = pd.to_datetime(timestamp).to_pydatetime()
            last_ts = pd.to_datetime(sensor.last_reading_at).to_pydatetime()
            if ts.tzinfo is not None and last_ts.tzinfo is None:
                last_ts = last_ts.replace(tzinfo=timezone.utc)
            elif ts.tzinfo is None and last_ts.tzinfo is not None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts > last_ts:
                sensor.last_reading_at = timestamp
