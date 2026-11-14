# 🏛️ System Architecture — Milestone 1

## AI-Powered Smart Irrigation System for Predictive Water Management and Crop Optimization
**Milestone 1: Sensor Data Ingestion & Weather API Integration (Weeks 1–2)**

---

## 1. High-Level System Architecture Diagram

```mermaid
flowchart TD
    subgraph IoT_Layer["📡 IoT Telemetry & Simulation Layer"]
        HardwareSensors["Physical Soil Moisture Sensors\n(Capacitive / TDR)"]
        Simulator["IoT Telemetry Simulator\n(Random-Walk + Diurnal Cycle)\n(app/services/simulator.py)"]
    end

    subgraph External_APIs["🌐 External Weather Services"]
        OWM["OpenWeatherMap API\n(Current Weather Endpoint)\n(api.openweathermap.org)"]
    end

    subgraph Backend_App["⚙️ Backend Service (FastAPI / Python 3.12)"]
        subgraph Routers["API Routers (/api/v1/*)"]
            RF["Farmers Router\n(/farmers)"]
            RFLD["Fields Router\n(/fields)"]
            RC["Crops Router\n(/crops)"]
            RS["Sensors Router\n(/sensors)"]
            RSD["Sensor Data Router\n(/sensor-data)"]
            RW["Weather Router\n(/weather)"]
        end

        subgraph Core_Services["Business Logic & Pipeline Services"]
            DC["Data Cleaning & Normalization Engine\n(Pandas / Clamping / Gap Detection)"]
            SI["Sensor Ingestion Pipeline\n(Single + Batch + Duplication Filter)"]
            WS["Weather Integration Service\n(HTTPX Async + Tenacity Retries + Cache Fallback)"]
        end

        subgraph ORM_Layer["SQLAlchemy 2.0 ORM"]
            ORM_Models["Farmer, Field, Crop, Sensor,\nSensorReading, WeatherData"]
        end
    end

    subgraph DB_Layer["🗄️ Relational & Time-Series Database"]
        PG["PostgreSQL 15+\n(Relational Profiles: Farmers, Fields, Crops, Sensors)"]
        TS["TimescaleDB Extension\n(Hypertables: sensor_readings, weather_data)"]
    end

    subgraph Frontend_App["🖥️ Farmer & Operator Dashboard (Next.js 14 + Tailwind)"]
        D_Dash["Dashboard Overview\n(Moisture Trends & Live Telemetry)"]
        D_Farmers["Farmer Management\n(Registration & Directory)"]
        D_Fields["Field Management\n(GPS Mapping & Soil Setup)"]
        D_Crops["Crop Configurations\n(Optimal Thresholds & Growth Stages)"]
        D_Sensors["Sensor Monitoring\n(Live Status, Charts & 7-Day Sim)"]
        D_Weather["Weather Telemetry\n(Live OWM & Historical Graphs)"]
    end

    %% Data flow links
    HardwareSensors -->|HTTP REST POST /api/v1/sensor-data| RSD
    Simulator -->|Automated Batch Ingestion| RSD
    OWM <-->|Async GET /weather + 3x Exponential Retries| WS

    RSD --> SI
    SI --> DC
    DC --> ORM_Layer
    WS --> ORM_Layer
    RF & RFLD & RC & RS --> ORM_Layer

    ORM_Layer -->|Relational Queries| PG
    ORM_Layer -->|Time-Series Hypertable Partitioning| TS

    Frontend_App <-->|REST API JSON| Routers
```

---

## 2. Architectural Design Decisions

### 2.1 Backend: FastAPI + Pydantic + SQLAlchemy
- **FastAPI**: Selected for native asynchronous execution, automatic interactive OpenAPI/Swagger generation (`/docs`), and native type checking.
- **Pydantic v2**: Enforces strict payload validation at the gateway level. Sensor values outside physiological or physical possibilities (e.g. soil moisture < 0% or > 100%) are rejected or flagged before hitting database storage.
- **SQLAlchemy 2.0**: Type-safe Object Relational Mapping (ORM) allowing seamless transition between PostgreSQL with TimescaleDB in production and SQLite in isolated automated test environments.

### 2.2 Time-Series Engine: TimescaleDB Hypertables
- Regular relational databases degrade exponentially when millions of time-indexed sensor readings are accumulated.
- **TimescaleDB** partitions data by time intervals (e.g., 1-day chunks) under the hood while maintaining standard SQL table semantics.
- Querying the last 24 hours of soil moisture across 500 fields runs orders of magnitude faster without manual table partitioning.

### 2.3 Sensor Telemetry Simulation Engine
- Physical IoT hardware is frequently unavailable during early development phases.
- The simulator (`app/services/simulator.py`) generates realistic diurnal cycles:
  - Soil moisture decreases slowly during daylight hours due to evapotranspiration and stabilizes at night.
  - Temperature peaks in the early afternoon (14:00) and bottoms out before dawn (05:00).
  - Explicit provenance tracking: every simulated record carries `is_simulated = True` and `quality_flag = 'SIMULATED'`.

### 2.4 External Weather Resilience: Exponential Backoff & Cached Fallback
- Third-party weather APIs (OpenWeatherMap) can experience transient outages, rate limiting, or network timeouts.
- Using `tenacity`, the weather client retries failed attempts up to 3 times with exponential backoff (1s, 2s, 4s).
- If all attempts fail, the service returns the most recent cached observation for the field with an explicit `is_stale = True` metadata flag, preventing system crashes.

