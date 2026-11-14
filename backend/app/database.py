"""
Database connection and session management module.

Provides SQLAlchemy engine, session factory, declarative base, and a FastAPI
dependency generator for database sessions.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from .config import settings

# Create the SQLAlchemy engine using the DATABASE_URL from config.
# If SQLite is specified, omit PostgreSQL connection pool parameters.
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=(settings.APP_ENV == "development"),
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
        echo=(settings.APP_ENV == "development"),
    )

# Session factory — each call produces a new Session bound to our engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for all ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.

    Automatically closes the session when the request is done,
    ensuring connections are returned to the pool.

    Yields:
        Session: An active SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all tables defined by ORM models.

    This imports all models to ensure they are registered with `Base.metadata`
    before calling `create_all`. Safe to call multiple times — existing tables
    are not recreated.
    """
    # Import all models so they register with Base.metadata
    from .models import (  # noqa: F401
        Farmer,
        Crop,
        Field,
        Sensor,
        SensorReading,
        WeatherData,
    )
    Base.metadata.create_all(bind=engine)
