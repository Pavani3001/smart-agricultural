# 🗄️ Database Entity-Relationship (ER) Diagram

## AI-Powered Smart Irrigation System
**Database Stack**: PostgreSQL 15+ with TimescaleDB Hypertable Extensions

---

## 1. Mermaid Entity-Relationship Diagram

```mermaid
erDiagram
    FARMERS ||--o{ FIELDS : "registers and owns"
    CROPS ||--o{ FIELDS : "planted on"
    FIELDS ||--o{ SENSORS : "equipped with"
    FIELDS ||--o{ WEATHER_DATA : "geo-located weather history"
    SENSORS ||--o{ SENSOR_READINGS : "transmits telemetry"

    FARMERS {
        SERIAL id PK
        VARCHAR(100) name "Full name of farmer"
        VARCHAR(150) email UK "Unique contact email"
        VARCHAR(20) phone "Contact phone number"
        TEXT address "Mailing address / village"
        TIMESTAMPTZ created_at "Registration timestamp"
        TIMESTAMPTZ updated_at "Profile modification timestamp"
    }

    CROPS {
        SERIAL id PK
        VARCHAR(100) crop_name UK "e.g., Rice, Wheat, Cotton"
        FLOAT optimal_moisture_min "Lower moisture boundary (%)"
        FLOAT optimal_moisture_max "Upper moisture boundary (%)"
        VARCHAR(50) growth_stage "e.g., vegetative, flowering"
        INTEGER water_requirement_mm "Total seasonal water demand"
        VARCHAR(50) season "e.g., Kharif, Rabi, Zaid"
        TEXT description "Agronomic notes"
        TIMESTAMPTZ created_at
    }

    FIELDS {
        SERIAL id PK
        INTEGER farmer_id FK "References farmers(id) ON DELETE CASCADE"
        INTEGER crop_id FK "References crops(id) ON DELETE SET NULL"
        VARCHAR(100) field_name "Descriptive name of field/plot"
        DOUBLE_PRECISION latitude "GPS Latitude (-90 to +90)"
        DOUBLE_PRECISION longitude "GPS Longitude (-180 to +180)"
        FLOAT area_hectares "Cultivated area in hectares"
        VARCHAR(100) crop_type "Free-text/legacy crop label"
        VARCHAR(50) soil_type "e.g., loamy, clay, sandy"
        VARCHAR(20) status "active | inactive | fallow"
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    SENSORS {
        SERIAL id PK
        VARCHAR(50) sensor_id UK "Unique hardware/node identifier"
        INTEGER field_id FK "References fields(id) ON DELETE CASCADE"
        VARCHAR(50) sensor_type "e.g., soil_moisture, temperature"
        VARCHAR(20) status "active | inactive | maintenance | error"
        TIMESTAMPTZ last_reading_at "Timestamp of most recent packet"
        TIMESTAMPTZ installed_at "Installation date"
        TIMESTAMPTZ created_at
    }

    SENSOR_READINGS {
        BIGSERIAL id PK "Hypertable chunk auto-increment"
        VARCHAR(50) sensor_id "Matches sensors.sensor_id"
        INTEGER field_id "Associated field identifier"
        FLOAT soil_moisture_percent "Measured volumetric moisture (0-100%)"
        FLOAT temperature_celsius "Ambient/probe temperature (-50 to +60 C)"
        BOOLEAN is_simulated "True if synthetic telemetry"
        VARCHAR(20) quality_flag "VALID | SIMULATED | INTERPOLATED | STALE | INVALID"
        TIMESTAMPTZ timestamp "Measurement timestamp (partition key)"
        TIMESTAMPTZ ingested_at "Database arrival timestamp"
    }

    WEATHER_DATA {
        BIGSERIAL id PK "Hypertable chunk auto-increment"
        INTEGER field_id "Associated field identifier"
        FLOAT temperature_celsius "Ambient temperature from OpenWeatherMap"
        FLOAT humidity_percent "Relative atmospheric humidity (%)"
        FLOAT rainfall_mm "Precipitation volume (mm)"
        FLOAT wind_speed_ms "Wind speed (meters per second)"
        VARCHAR(50) weather_condition "Condition classification (e.g. Rain, Clear)"
        VARCHAR(200) description "Detailed observation text"
        VARCHAR(50) data_source "Default: openweathermap"
        TIMESTAMPTZ timestamp "Observation time (partition key)"
        TIMESTAMPTZ fetched_at "API fetch timestamp"
    }
```

---

## 2. Table Specifications & Indexes

| Table | Storage Engine | Partition Interval | Foreign Keys | Key Indexes |
|---|---|---|---|---|
| `farmers` | PostgreSQL Relational | N/A | None | `email` (UNIQUE) |
| `crops` | PostgreSQL Relational | N/A | None | `crop_name` (UNIQUE) |
| `fields` | PostgreSQL Relational | N/A | `farmer_id`, `crop_id` | `farmer_id`, `crop_id` |
| `sensors` | PostgreSQL Relational | N/A | `field_id` | `sensor_id` (UNIQUE), `field_id` |
| `sensor_readings` | **TimescaleDB Hypertable** | **1 day** | Denormalized for partition performance | `(sensor_id, timestamp DESC)`, `(field_id, timestamp DESC)` |
| `weather_data` | **TimescaleDB Hypertable** | **1 day** | Denormalized for partition performance | `(field_id, timestamp DESC)` |

---

## 3. Data Integrity & Validation Rules

1. **Cascade Semantics**:
   - Deleting a `farmer` cascades to all owned `fields` and attached `sensors`.
   - Deleting a `crop` sets `fields.crop_id` to `NULL`, preserving the field configuration.
2. **Quality Provenance**:
   - `quality_flag` enforces explicit classification:
     - `VALID`: Physical reading within physical bounds.
     - `SIMULATED`: Generated by the sensor telemetry simulation service.
     - `INTERPOLATED`: Cleaned or filled by pandas batch routines.
     - `STALE`: Cached weather observation returned after API downtime.
     - `INVALID`: Rejected sensor value (e.g. moisture > 100% or sensor failure).

