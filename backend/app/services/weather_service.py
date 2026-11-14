"""
OpenWeatherMap integration service.

Fetches current weather data for a given location using the OpenWeatherMap
Current Weather API. Uses httpx for async HTTP and tenacity for retry logic.
Falls back to the last stored weather record if the API is unreachable.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from sqlalchemy.orm import Session

from ..config import settings
from ..models.weather_data import WeatherData

logger = logging.getLogger(__name__)

# OpenWeatherMap Current Weather API endpoint
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# HTTP timeout for weather API requests (seconds)
HTTP_TIMEOUT = 10.0


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    reraise=True,
)
async def _fetch_from_owm(lat: float, lon: float) -> dict:
    """
    Call OpenWeatherMap Current Weather API with retry logic.

    Retries up to 3 times with exponential backoff on HTTP errors.

    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.

    Returns:
        Parsed JSON response dictionary from the API.

    Raises:
        httpx.HTTPError: If the request fails after all retries.
        ValueError: If the API returns an unexpected response structure.
    """
    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.OPENWEATHERMAP_API_KEY,
        "units": "metric",  # Celsius, m/s
    }

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.get(OWM_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

    # Sanity-check the response structure
    if "main" not in data or "weather" not in data:
        raise ValueError(f"Unexpected OWM response structure: {list(data.keys())}")

    return data


def _parse_owm_response(data: dict, field_id: int) -> WeatherData:
    """
    Parse the raw OpenWeatherMap JSON into a WeatherData ORM instance.

    Args:
        data: Raw JSON dict from OWM API.
        field_id: The field this weather data belongs to.

    Returns:
        A WeatherData instance (not yet committed to DB).
    """
    now_utc = datetime.now(timezone.utc)

    # Extract rainfall — OWM puts rain under 'rain.1h' or 'rain.3h'
    rain_data = data.get("rain", {})
    rainfall_mm = rain_data.get("1h", rain_data.get("3h", 0.0))

    # Primary weather condition
    weather_list = data.get("weather", [{}])
    condition = weather_list[0].get("main", "Unknown") if weather_list else "Unknown"
    description = weather_list[0].get("description", "") if weather_list else ""

    return WeatherData(
        field_id=field_id,
        temperature_celsius=data.get("main", {}).get("temp"),
        humidity_percent=data.get("main", {}).get("humidity"),
        rainfall_mm=rainfall_mm,
        wind_speed_ms=data.get("wind", {}).get("speed"),
        weather_condition=condition,
        description=description,
        data_source="openweathermap",
        timestamp=now_utc,
        fetched_at=now_utc,
    )


async def fetch_weather_for_field(
    db: Session,
    field_id: int,
    latitude: float,
    longitude: float,
) -> tuple[WeatherData, bool]:
    """
    Fetch current weather from OpenWeatherMap and store it.

    On API failure after all retries, falls back to the most recent
    stored weather record for this field (marked as STALE).

    Args:
        db: Active database session.
        field_id: ID of the field to fetch weather for.
        latitude: Field latitude.
        longitude: Field longitude.

    Returns:
        Tuple of (weather_record, is_stale):
            - weather_record: The WeatherData instance (stored in DB).
            - is_stale: True if the data came from cache due to API failure.
    """
    try:
        # Attempt to fetch live data
        raw_data = await _fetch_from_owm(latitude, longitude)
        weather = _parse_owm_response(raw_data, field_id)

        # Persist to database
        db.add(weather)
        db.commit()
        db.refresh(weather)

        logger.info(
            "Weather fetched for field %d: %s, %.1f°C",
            field_id,
            weather.weather_condition,
            weather.temperature_celsius or 0.0,
        )
        return weather, False

    except Exception as e:
        logger.warning(
            "Failed to fetch weather for field %d after retries: %s. "
            "Falling back to last known record.",
            field_id,
            str(e),
        )
        # Fall back to the most recent stored weather for this field
        return _get_last_known_weather(db, field_id)


def _get_last_known_weather(
    db: Session, field_id: int
) -> tuple[Optional[WeatherData], bool]:
    """
    Retrieve the most recent weather record for a field.

    Args:
        db: Active database session.
        field_id: ID of the field.

    Returns:
        Tuple of (weather_record_or_None, True).
        is_stale is always True for fallback data.
    """
    last_record = (
        db.query(WeatherData)
        .filter(WeatherData.field_id == field_id)
        .order_by(WeatherData.timestamp.desc())
        .first()
    )
    return last_record, True


def get_weather_history(
    db: Session,
    field_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> list[WeatherData]:
    """
    Query stored weather records for a field within a time range.

    Args:
        db: Active database session.
        field_id: ID of the field.
        start_time: Inclusive start of the time range (UTC).
        end_time: Inclusive end of the time range (UTC).

    Returns:
        List of WeatherData records, ordered by timestamp descending.
    """
    query = db.query(WeatherData).filter(WeatherData.field_id == field_id)

    if start_time:
        query = query.filter(WeatherData.timestamp >= start_time)
    if end_time:
        query = query.filter(WeatherData.timestamp <= end_time)

    return query.order_by(WeatherData.timestamp.desc()).all()


def get_latest_weather(db: Session, field_id: int) -> Optional[WeatherData]:
    """
    Get the single most recent weather record for a field.

    Args:
        db: Active database session.
        field_id: ID of the field.

    Returns:
        The most recent WeatherData record, or None.
    """
    return (
        db.query(WeatherData)
        .filter(WeatherData.field_id == field_id)
        .order_by(WeatherData.timestamp.desc())
        .first()
    )
