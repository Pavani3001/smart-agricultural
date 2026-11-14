"""
Sensor registry router.

Provides CRUD endpoints for registering hardware/virtual sensors
associated with specific agricultural fields.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.sensor import Sensor
from ..models.field import Field
from ..schemas.sensor import SensorCreate, SensorUpdate, SensorResponse
from ..utils.exceptions import ResourceNotFoundError, DuplicateResourceError

router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.post("/", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
def register_sensor(sensor_in: SensorCreate, db: Session = Depends(get_db)):
    """Register a new sensor associated with a field."""
    field = db.query(Field).filter(Field.id == sensor_in.field_id).first()
    if not field:
        raise ResourceNotFoundError("Field", sensor_in.field_id)

    existing = db.query(Sensor).filter(Sensor.sensor_id == sensor_in.sensor_id).first()
    if existing:
        raise DuplicateResourceError("Sensor", f"Sensor with ID '{sensor_in.sensor_id}' is already registered")

    sensor = Sensor(**sensor_in.model_dump())
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return sensor


@router.get("/", response_model=List[SensorResponse])
def list_sensors(
    field_id: Optional[int] = Query(None, description="Filter sensors by field ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all registered sensors, optionally filtered by field ID."""
    query = db.query(Sensor)
    if field_id is not None:
        query = query.filter(Sensor.field_id == field_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{sensor_id}", response_model=SensorResponse)
def get_sensor(sensor_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a specific sensor by its string identifier."""
    sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
    if not sensor:
        raise ResourceNotFoundError("Sensor", sensor_id)
    return sensor


@router.put("/{sensor_id}", response_model=SensorResponse)
def update_sensor(sensor_id: str, sensor_in: SensorUpdate, db: Session = Depends(get_db)):
    """Update sensor configuration or status."""
    sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
    if not sensor:
        raise ResourceNotFoundError("Sensor", sensor_id)

    update_data = sensor_in.model_dump(exclude_unset=True)

    if "field_id" in update_data and update_data["field_id"] is not None:
        field = db.query(Field).filter(Field.id == update_data["field_id"]).first()
        if not field:
            raise ResourceNotFoundError("Field", update_data["field_id"])

    for key, value in update_data.items():
        setattr(sensor, key, value)

    db.commit()
    db.refresh(sensor)
    return sensor


@router.delete("/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sensor(sensor_id: str, db: Session = Depends(get_db)):
    """Delete a sensor from the registry."""
    sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
    if not sensor:
        raise ResourceNotFoundError("Sensor", sensor_id)

    db.delete(sensor)
    db.commit()
    return None

