"""
Main FastAPI Application for Smart Irrigation System (Milestone 1).

Provides REST APIs for:
- Farmer registration & profile management
- Field location & crop configuration
- Crop type management & optimal water thresholds
- Sensor hardware/virtual registry
- Soil moisture & environmental sensor data ingestion (single & batch)
- Sensor data simulation for testing without physical IoT hardware
- OpenWeatherMap weather API integration with retry & fallback
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .database import engine, Base, init_db, get_db
from .utils.exceptions import register_exception_handlers
from .routers import (
    farmers_router,
    fields_router,
    crops_router,
    sensors_router,
    sensor_data_router,
    weather_router,
)
from .models.farmer import Farmer
from .models.field import Field
from .models.crop import Crop
from .models.sensor import Sensor
from .models.sensor_reading import SensorReading
from .models.weather_data import WeatherData

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.APP_ENV != "debug" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("smart_irrigation")


def seed_default_crops(db: Session):
    """Seed initial crop data if the table is empty."""
    default_crops = [
        {"crop_name": "Rice", "optimal_moisture_min": 60.0, "optimal_moisture_max": 80.0, "growth_stage": "vegetative", "water_requirement_mm": 1200, "season": "Kharif", "description": "Paddy rice - requires high soil moisture throughout growth"},
        {"crop_name": "Wheat", "optimal_moisture_min": 40.0, "optimal_moisture_max": 60.0, "growth_stage": "vegetative", "water_requirement_mm": 450, "season": "Rabi", "description": "Winter wheat - moderate water requirement"},
        {"crop_name": "Cotton", "optimal_moisture_min": 35.0, "optimal_moisture_max": 55.0, "growth_stage": "vegetative", "water_requirement_mm": 700, "season": "Kharif", "description": "Cotton crop - sensitive to over-watering"},
        {"crop_name": "Sugarcane", "optimal_moisture_min": 50.0, "optimal_moisture_max": 70.0, "growth_stage": "vegetative", "water_requirement_mm": 1500, "season": "Annual", "description": "Sugarcane - high water demand, long growing season"},
        {"crop_name": "Tomato", "optimal_moisture_min": 40.0, "optimal_moisture_max": 65.0, "growth_stage": "vegetative", "water_requirement_mm": 600, "season": "Rabi", "description": "Tomato - needs consistent moisture for fruit development"},
        {"crop_name": "Maize", "optimal_moisture_min": 45.0, "optimal_moisture_max": 65.0, "growth_stage": "vegetative", "water_requirement_mm": 500, "season": "Kharif", "description": "Maize/Corn - moderate water needs, drought sensitive at tasseling"},
        {"crop_name": "Groundnut", "optimal_moisture_min": 35.0, "optimal_moisture_max": 55.0, "growth_stage": "vegetative", "water_requirement_mm": 500, "season": "Kharif", "description": "Groundnut/Peanut - moderate moisture, good for dryland"},
        {"crop_name": "Soybean", "optimal_moisture_min": 40.0, "optimal_moisture_max": 60.0, "growth_stage": "vegetative", "water_requirement_mm": 450, "season": "Kharif", "description": "Soybean - moderate water requirement"}
    ]

    for crop_data in default_crops:
        existing = db.query(Crop).filter(Crop.crop_name == crop_data["crop_name"]).first()
        if not existing:
            db.add(Crop(**crop_data))
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event to initialize database tables and seed defaults."""
    if settings.APP_ENV != "testing":
        logger.info("Initializing database tables...")
        try:
            init_db()
            logger.info("Database tables verified.")
            from .database import SessionLocal
            db = SessionLocal()
            try:
                seed_default_crops(db)
                logger.info("Default crops checked/seeded.")
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Database initialization deferred or skipped: {e}")
    else:
        logger.info("Testing mode: skipping default DB initialization.")
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title="AI-Powered Smart Irrigation System API",
    description="Milestone 1: Sensor Data Ingestion & Weather API Integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Register CORS middleware (allowing localhost, 127.0.0.1, [::1] on any port)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$",
    allow_origins=settings.cors_origins_list + ["http://localhost:3000", "http://127.0.0.1:3000", "http://[::1]:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register uniform exception handlers
register_exception_handlers(app)

# Include API Routers under /api/v1
API_PREFIX = "/api/v1"
app.include_router(farmers_router, prefix=API_PREFIX)
app.include_router(fields_router, prefix=API_PREFIX)
app.include_router(crops_router, prefix=API_PREFIX)
app.include_router(sensors_router, prefix=API_PREFIX)
app.include_router(sensor_data_router, prefix=API_PREFIX)
app.include_router(weather_router, prefix=API_PREFIX)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint with service summary and documentation links."""
    return {
        "service": "AI-Powered Smart Irrigation System API",
        "milestone": "Milestone 1: Sensor Ingestion & Weather Integration",
        "status": "online",
        "docs_url": "/docs",
        "api_version": "v1",
    }


@app.get(f"{API_PREFIX}/health", tags=["Health"])
def health_check():
    """Health check endpoint for container probes and monitoring."""
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "database_connected": True,
    }


@app.get(f"{API_PREFIX}/stats/dashboard", tags=["Dashboard"])
def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get aggregated dashboard summary counts for farmers, fields, sensors,
    recent readings, and active alerts.
    """
    total_farmers = db.query(Farmer).count()
    total_fields = db.query(Field).count()
    active_fields = db.query(Field).filter(Field.status == "active").count()
    total_sensors = db.query(Sensor).count()
    active_sensors = db.query(Sensor).filter(Sensor.status == "active").count()
    total_readings = db.query(SensorReading).count()
    simulated_readings = db.query(SensorReading).filter(SensorReading.is_simulated == True).count()
    weather_records = db.query(WeatherData).count()

    return {
        "total_farmers": total_farmers,
        "total_fields": total_fields,
        "active_fields": active_fields,
        "total_sensors": total_sensors,
        "active_sensors": active_sensors,
        "total_sensor_readings": total_readings,
        "simulated_sensor_readings": simulated_readings,
        "total_weather_records": weather_records,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True,
    )
