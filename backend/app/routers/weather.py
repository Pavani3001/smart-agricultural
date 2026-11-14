"""
Weather data router.

Provides endpoints for:
- Fetching live weather data from OpenWeatherMap for a registered field
- Fetching live weather for all fields in batch
- Querying historical weather observations
- Getting the latest recorded weather for a field
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.field import Field
from ..schemas.weather import WeatherDataResponse, WeatherFetchResponse
from ..services.weather_service import (
    fetch_weather_for_field,
    get_weather_history,
    get_latest_weather,
)
from ..utils.exceptions import ResourceNotFoundError

router = APIRouter(prefix="/weather", tags=["Weather Integration"])


@router.post("/fetch/{field_id}", response_model=WeatherFetchResponse)
async def fetch_weather_endpoint(field_id: int, db: Session = Depends(get_db)):
    """
    Fetch current weather from OpenWeatherMap for a specific field's GPS location.
    Persists the reading to the database. If OpenWeatherMap is unreachable,
    falls back to the last recorded weather with is_stale=True.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise ResourceNotFoundError("Field", field_id)

    weather, is_stale = await fetch_weather_for_field(
        db=db,
        field_id=field.id,
        latitude=field.latitude,
        longitude=field.longitude,
    )

    if not weather:
        return WeatherFetchResponse(
            success=False,
            message="No weather data available (API error and no cached data).",
            data=None,
            is_stale=False,
        )

    return WeatherFetchResponse(
        success=True,
        message="Weather fetched successfully" if not is_stale else "Weather API unavailable; returned cached data",
        data=weather,
        is_stale=is_stale,
    )


@router.post("/fetch-all", response_model=List[WeatherFetchResponse])
async def fetch_weather_all_fields(db: Session = Depends(get_db)):
    """
    Fetch current weather for all active fields in the system.
    """
    fields = db.query(Field).filter(Field.status == "active").all()
    results = []

    for field in fields:
        weather, is_stale = await fetch_weather_for_field(
            db=db,
            field_id=field.id,
            latitude=field.latitude,
            longitude=field.longitude,
        )
        if weather:
            results.append(
                WeatherFetchResponse(
                    success=True,
                    message=f"Fetched for field '{field.field_name}'",
                    data=weather,
                    is_stale=is_stale,
                )
            )
        else:
            results.append(
                WeatherFetchResponse(
                    success=False,
                    message=f"Failed for field '{field.field_name}'",
                    data=None,
                    is_stale=False,
                )
            )

    return results


@router.get("/{field_id}", response_model=List[WeatherDataResponse])
def get_field_weather_history(
    field_id: int,
    start_time: Optional[datetime] = Query(None, description="Start timestamp (UTC)"),
    end_time: Optional[datetime] = Query(None, description="End timestamp (UTC)"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    Retrieve historical weather observations for a field.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise ResourceNotFoundError("Field", field_id)

    history = get_weather_history(db, field_id, start_time, end_time)
    return history[:limit]


@router.get("/current/{field_id}", response_model=Optional[WeatherDataResponse])
def get_current_weather(field_id: int, db: Session = Depends(get_db)):
    """
    Get the most recent weather observation recorded for a field.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise ResourceNotFoundError("Field", field_id)

    return get_latest_weather(db, field_id)

