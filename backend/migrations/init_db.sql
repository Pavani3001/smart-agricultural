-- ===========================================
-- Smart Irrigation System - Database Schema
-- PostgreSQL + TimescaleDB
-- Milestone 1: Sensor Data Ingestion & Weather API Integration
-- ===========================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ===========================================
-- 1. FARMERS TABLE
-- Stores farmer registration information
-- ===========================================
CREATE TABLE IF NOT EXISTS farmers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================================
-- 2. CROPS TABLE
-- Stores crop configuration and water requirements
-- ===========================================
CREATE TABLE IF NOT EXISTS crops (
    id SERIAL PRIMARY KEY,
    crop_name VARCHAR(100) UNIQUE NOT NULL,
    optimal_moisture_min FLOAT NOT NULL DEFAULT 30.0,
    optimal_moisture_max FLOAT NOT NULL DEFAULT 70.0,
    growth_stage VARCHAR(50) DEFAULT 'vegetative',
    water_requirement_mm INTEGER DEFAULT 500,
    season VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================================
-- 3. FIELDS TABLE
-- Stores field registration with GPS location
-- Links to farmers and crops
-- ===========================================
CREATE TABLE IF NOT EXISTS fields (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    crop_id INTEGER REFERENCES crops(id) ON DELETE SET NULL,
    field_name VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    area_hectares FLOAT NOT NULL DEFAULT 1.0,
    crop_type VARCHAR(100),
    soil_type VARCHAR(50) DEFAULT 'loamy',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'fallow')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================================
-- 4. SENSORS TABLE
-- Stores sensor registry linked to fields
-- ===========================================
CREATE TABLE IF NOT EXISTS sensors (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) UNIQUE NOT NULL,
    field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    sensor_type VARCHAR(50) DEFAULT 'soil_moisture',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance', 'error')),
    last_reading_at TIMESTAMP WITH TIME ZONE,
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================================
-- 5. SENSOR_READINGS TABLE (TimescaleDB Hypertable)
-- Time-series soil moisture data
-- ===========================================
CREATE TABLE IF NOT EXISTS sensor_readings (
    id BIGSERIAL,
    sensor_id VARCHAR(50) NOT NULL,
    field_id INTEGER NOT NULL,
    soil_moisture_percent FLOAT,
    temperature_celsius FLOAT,
    is_simulated BOOLEAN DEFAULT FALSE,
    quality_flag VARCHAR(20) DEFAULT 'VALID' CHECK (quality_flag IN ('VALID', 'SIMULATED', 'INTERPOLATED', 'STALE', 'INVALID')),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Convert sensor_readings to a TimescaleDB hypertable
-- Partitioned by timestamp with 1-day chunks
SELECT create_hypertable('sensor_readings', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- ===========================================
-- 6. WEATHER_DATA TABLE (TimescaleDB Hypertable)
-- Time-series weather data from OpenWeatherMap
-- ===========================================
CREATE TABLE IF NOT EXISTS weather_data (
    id BIGSERIAL,
    field_id INTEGER NOT NULL,
    temperature_celsius FLOAT,
    humidity_percent FLOAT,
    rainfall_mm FLOAT DEFAULT 0.0,
    wind_speed_ms FLOAT,
    weather_condition VARCHAR(50),
    description VARCHAR(200),
    data_source VARCHAR(50) DEFAULT 'openweathermap',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Convert weather_data to a TimescaleDB hypertable
SELECT create_hypertable('weather_data', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- ===========================================
-- INDEXES
-- ===========================================
CREATE INDEX IF NOT EXISTS idx_fields_farmer_id ON fields(farmer_id);
CREATE INDEX IF NOT EXISTS idx_fields_crop_id ON fields(crop_id);
CREATE INDEX IF NOT EXISTS idx_sensors_field_id ON sensors(field_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_id ON sensor_readings(sensor_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_field_id ON sensor_readings(field_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_weather_data_field_id ON weather_data(field_id, timestamp DESC);

-- ===========================================
-- SEED DATA - Sample Crops
-- ===========================================
INSERT INTO crops (crop_name, optimal_moisture_min, optimal_moisture_max, growth_stage, water_requirement_mm, season, description)
VALUES
    ('Rice', 60.0, 80.0, 'vegetative', 1200, 'Kharif', 'Paddy rice - requires high soil moisture throughout growth'),
    ('Wheat', 40.0, 60.0, 'vegetative', 450, 'Rabi', 'Winter wheat - moderate water requirement'),
    ('Cotton', 35.0, 55.0, 'vegetative', 700, 'Kharif', 'Cotton crop - sensitive to over-watering'),
    ('Sugarcane', 50.0, 70.0, 'vegetative', 1500, 'Annual', 'Sugarcane - high water demand, long growing season'),
    ('Tomato', 40.0, 65.0, 'vegetative', 600, 'Rabi', 'Tomato - needs consistent moisture for fruit development'),
    ('Maize', 45.0, 65.0, 'vegetative', 500, 'Kharif', 'Maize/Corn - moderate water needs, drought sensitive at tasseling'),
    ('Groundnut', 35.0, 55.0, 'vegetative', 500, 'Kharif', 'Groundnut/Peanut - moderate moisture, good for dryland'),
    ('Soybean', 40.0, 60.0, 'vegetative', 450, 'Kharif', 'Soybean - moderate water requirement')
ON CONFLICT (crop_name) DO NOTHING;

-- ===========================================
-- TRIGGER: Auto-update updated_at timestamps
-- ===========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_farmers_updated_at
    BEFORE UPDATE ON farmers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fields_updated_at
    BEFORE UPDATE ON fields
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===========================================
-- DONE: Database schema initialized successfully
-- ===========================================

