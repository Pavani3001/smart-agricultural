"""
Sensor data ingestion and query router.

Provides endpoints for:
- Ingesting single and batch sensor readings
- Querying historical readings with time filters
- Triggering sensor simulation for testing without physical hardware
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.sensor import Sensor
from ..schemas.sensor_reading import (
    SensorReadingCreate,
    SensorReadingBatchCreate,
    SensorReadingResponse,
)
from ..services.sensor_service import (
    ingest_single_reading,
    ingest_batch_readings,
    get_sensor_readings,
    get_field_readings,
)
from ..services.simulator import generate_simulated_readings
from ..utils.exceptions import ResourceNotFoundError

router = APIRouter(prefix="/sensor-data", tags=["Sensor Data Ingestion"])


@router.post("/", response_model=SensorReadingResponse, status_code=status.HTTP_201_CREATED)
def ingest_reading(reading_in: SensorReadingCreate, db: Session = Depends(get_db)):
    """
    Ingest a single sensor reading.
    Validates physical limits, checks for duplicates, normalizes values,
    and updates the sensor's last_reading_at timestamp.
    """
    try:
        return ingest_single_reading(db, reading_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/batch", response_model=List[SensorReadingResponse], status_code=status.HTTP_201_CREATED)
def ingest_batch(batch_in: SensorReadingBatchCreate, db: Session = Depends(get_db)):
    """
    Ingest a batch of sensor readings using pandas cleaning and normalization.
    """
    try:
        return ingest_batch_readings(db, batch_in.readings)
    except Exception as e:
        import logging
        logging.getLogger("smart_irrigation").exception("Error in batch ingestion:")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{sensor_id}", response_model=List[SensorReadingResponse])
def get_readings_by_sensor(
    sensor_id: str,
    start_time: Optional[datetime] = Query(None, description="Start timestamp (UTC)"),
    end_time: Optional[datetime] = Query(None, description="End timestamp (UTC)"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Query historical readings for a specific sensor.
    Supports start_time and end_time filtering.
    """
    readings = get_sensor_readings(db, sensor_id, start_time, end_time)
    return readings[:limit]


@router.get("/field/{field_id}", response_model=List[SensorReadingResponse])
def get_readings_by_field(
    field_id: int,
    start_time: Optional[datetime] = Query(None, description="Start timestamp (UTC)"),
    end_time: Optional[datetime] = Query(None, description="End timestamp (UTC)"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Query historical readings across all sensors in a field.
    """
    readings = get_field_readings(db, field_id, start_time, end_time)
    return readings[:limit]


@router.post("/simulate/{sensor_id}", response_model=List[SensorReadingResponse])
def simulate_sensor_data(
    sensor_id: str,
    days: int = Query(7, ge=1, le=30, description="Number of past days to simulate"),
    interval_minutes: int = Query(15, ge=5, le=120, description="Minutes between readings"),
    db: Session = Depends(get_db),
):
    """
    Generate realistic synthetic sensor readings for a sensor.
    Uses random-walk simulation with diurnal temperature cycle.
    All records are marked with is_simulated=True and quality_flag='SIMULATED'.
    """
    sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
    if not sensor:
        raise ResourceNotFoundError("Sensor", sensor_id)

    readings = generate_simulated_readings(
        db=db,
        sensor_id_str=sensor_id,
        days=days,
        interval_minutes=interval_minutes,
    )
    return readings[:100]  # Return preview of the generated readings
