# 🌾 AI-Powered Smart Irrigation System

> **A Full-Stack Predictive Water Management and Crop Optimization Platform**  
> **Milestone 1 Deliverable: Sensor Data Ingestion & Weather API Integration (Weeks 1–2)**

---

## 📌 Project Overview

Agricultural smallholder farmers frequently experience crop loss and water wastage due to the absence of real-time, data-driven irrigation guidance. This project develops an end-to-end smart irrigation platform that ingests real-time soil moisture telemetry, integrates live meteorological forecasts, and maintains location-specific field and crop configurations.

**Milestone 1** implements the full data foundation and telemetry ingestion pipeline, including:
1. **IoT Sensor Data Ingestion Pipeline**: Ingest single and batch sensor readings via REST APIs with data cleaning, duplicate detection, and time-series normalization.
2. **Sensor Simulation Engine**: Generates realistic diurnal soil moisture and temperature telemetry for testing when physical sensors are offline, with explicit provenance tagging (`SIMULATED`).
3. **OpenWeatherMap Integration**: Fetches real-time temperature, humidity, rainfall, and wind speed based on field GPS coordinates, backed by exponential retry logic and cached fallback.
4. **Farmer & Field Management**: Multi-field registration with GPS geo-tagging, soil classifications, and crop associations.
5. **Crop Configuration Module**: Configurable soil moisture thresholds, growth stages, seasonal cycles, and water requirements (mm).
6. **Relational & Time-Series Storage**: PostgreSQL relational schema combined with TimescaleDB hypertables for partition-accelerated time-series queries.
7. **Farmer Web Dashboard**: Modern, responsive Next.js 14 frontend styled with Tailwind CSS, featuring interactive Recharts visualizations for soil moisture trends, telemetry feeds, and weather monitoring.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph IoT["📡 Telemetry Layer"]
        HW["Physical Soil Sensors"]
        SIM["Telemetry Simulator (Random-Walk)"]
    end

    subgraph Backend["⚙️ Backend (FastAPI + Python 3.12)"]
        API["REST API Layer (/api/v1/*)"]
        DC["Pandas Data Cleaning & Validation"]
        WS["OpenWeatherMap Service (HTTPX + Tenacity)"]
        ORM["SQLAlchemy 2.0 ORM"]
    end

    subgraph Database["🗄️ Database"]
        PG["PostgreSQL (Relational Profiles)"]
        TS["TimescaleDB Hypertables (Readings & Weather)"]
    end

    subgraph Frontend["🖥️ Dashboard (Next.js 14 + Tailwind + Recharts)"]
        D1["Dashboard Overview"]
        D2["Farmer Management"]
        D3["Field Mapping"]
        D4["Crop Configuration"]
        D5["Sensor Monitoring & Simulation"]
        D6["Weather Telemetry"]
    end

    HW -->|POST /api/v1/sensor-data| API
    SIM -->|Simulated Telemetry Feed| API
    WS <-->|Async Weather Fetch| API
    API --> DC --> ORM
    WS --> ORM
    ORM --> PG & TS
    Frontend <-->|REST API JSON| API
```

---

## 📂 Project Structure

```
Agricultural/
├── backend/
│   ├── app/
│   │   ├── models/                # SQLAlchemy ORM models (Farmer, Field, Crop, Sensor, Hypertables)
│   │   ├── schemas/               # Pydantic v2 validation schemas
│   │   ├── routers/               # FastAPI modular endpoints (/farmers, /fields, /crops, /sensors, /sensor-data, /weather)
│   │   ├── services/              # Business logic (data cleaning, simulator, weather client)
│   │   ├── utils/                 # Exception handlers & uniform error responses
│   │   ├── config.py              # Pydantic Settings & environment variables
│   │   ├── database.py            # Database engine, sessions & auto-table init
│   │   └── main.py                # FastAPI application entry point
│   ├── migrations/
│   │   └── init_db.sql            # Full PostgreSQL + TimescaleDB initialization script
│   ├── tests/                     # Pytest automated test suite (7/7 passed)
│   │   ├── test_farmers.py
│   │   ├── test_fields.py
│   │   ├── test_sensors.py
│   │   ├── test_sensor_data.py
│   │   └── test_weather.py
│   ├── requirements.txt           # Python backend dependencies
│   └── .env.example               # Backend environment template
│
├── frontend/
│   ├── src/
│   │   ├── app/                   # Next.js 14 App Router pages
│   │   │   ├── layout.js          # Main layout with responsive sidebar & header
│   │   │   ├── page.js            # Dashboard home overview
│   │   │   ├── farmers/page.js    # Farmer registration & profiles
│   │   │   ├── fields/page.js     # Field location & soil configuration
│   │   │   ├── crops/page.js      # Crop thresholds & water demand
│   │   │   ├── sensors/page.js    # Sensor telemetry, simulation & charts
│   │   │   └── weather/page.js    # Live OpenWeatherMap data & trends
│   │   ├── components/            # Modular React components
│   │   │   ├── dashboard/         # StatsCard, MoistureChart, WeatherCard, SensorStatus
│   │   │   ├── forms/             # Controlled forms with validation
│   │   │   ├── layout/            # Sidebar, Header
│   │   │   └── ui/                # Button, Input, Modal, Toast, Card, Select
│   │   └── lib/
│   │       ├── api.js             # Unified REST API client with error handling
│   │       └── constants.js       # App constants, status badges, emojis
│   ├── package.json               # Frontend dependencies & scripts
│   ├── jsconfig.json              # Path aliases (@/*)
│   ├── tailwind.config.js         # Agricultural theme colors
│   └── .env.example               # Frontend environment template
│
├── docs/
│   ├── architecture-diagram.md    # Detailed architecture documentation
│   ├── er-diagram.md              # Database schema & entity relationships
│   ├── api-documentation.md       # Complete REST API reference
│   └── testing-report.md          # Automated test execution report
│
├── .gitignore
├── .env.example                   # Root environment template
└── README.md                      # Master documentation
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python 3.10+** (Tested on Python 3.12)
- **Node.js 18+** (Tested on Node.js v20)
- **PostgreSQL 14+ with TimescaleDB** (or SQLite for local testing)

---

### 1. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create and activate a Python virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env
# Edit .env and enter your PostgreSQL credentials and OpenWeatherMap API key:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/smart_irrigation
# OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here

# Initialize Database Schema (if using PostgreSQL)
psql -U postgres -d smart_irrigation -f migrations/init_db.sql

# Start the FastAPI Backend Server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Backend API**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

---

### 2. Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Next.js development server
npm run dev
```

- **Dashboard UI**: `http://localhost:3000`

---

### 3. Running Automated Tests

```bash
# From the project root or backend directory:
python -m pytest backend/tests -v
```

**Results**: 7/7 test suites pass in ~4.5 seconds with 100% coverage across core endpoints.

---

## 📡 REST API Summary

| Group | Method | Endpoint | Description |
|---|---|---|---|
| **System** | `GET` | `/api/v1/health` | Service health status |
| **System** | `GET` | `/api/v1/stats/dashboard` | Aggregated dashboard telemetry stats |
| **Farmers** | `POST` | `/api/v1/farmers/` | Register new farmer |
| **Farmers** | `GET` | `/api/v1/farmers/` | List farmers |
| **Fields** | `POST` | `/api/v1/fields/` | Register field with GPS coordinates |
| **Fields** | `GET` | `/api/v1/fields/` | List fields (filter: `?farmer_id=X`) |
| **Crops** | `POST` | `/api/v1/crops/` | Configure crop moisture thresholds |
| **Crops** | `GET` | `/api/v1/crops/` | List all crop configurations |
| **Sensors** | `POST` | `/api/v1/sensors/` | Register hardware/virtual sensor node |
| **Sensors** | `GET` | `/api/v1/sensors/` | List registered sensors |
| **Telemetry** | `POST` | `/api/v1/sensor-data/` | Ingest single sensor reading |
| **Telemetry** | `POST` | `/api/v1/sensor-data/batch` | Batch ingest readings with Pandas cleaning |
| **Telemetry** | `GET` | `/api/v1/sensor-data/{sensor_id}` | Query historical readings |
| **Simulator** | `POST` | `/api/v1/sensor-data/simulate/{sensor_id}` | Generate 7-day realistic sensor data |
| **Weather** | `POST` | `/api/v1/weather/fetch/{field_id}` | Fetch live weather from OpenWeatherMap |
| **Weather** | `GET` | `/api/v1/weather/{field_id}` | Query weather history for field |

---

## 🔒 Security & Data Provenance

1. **Zero Secret Leakage**: API keys and database credentials are kept exclusively in `.env` files and ignored in `.gitignore`. Templates are provided in `.env.example`.
2. **Explicit Simulated Telemetry**: All simulator records carry `is_simulated = True` and `quality_flag = 'SIMULATED'`.
3. **Resilient Weather Calls**: 3-tier exponential backoff via `tenacity` with cached fallback and `is_stale = True` indicator on API downtime.

---

## 🎯 Milestone 1 Deliverables Checklist

- [x] Complete working Python FastAPI backend with modular routers and models
- [x] PostgreSQL + TimescaleDB schema with hypertable definitions (`migrations/init_db.sql`)
- [x] Real OpenWeatherMap API integration with retries and fallback
- [x] Sensor data ingestion pipeline (single & batch) with Pandas cleaning and normalization
- [x] Sensor simulation engine generating 7-day realistic diurnal data
- [x] Responsive Next.js 14 frontend dashboard with Tailwind CSS and Recharts
- [x] 100% passing automated test suite (`pytest`)
- [x] Full documentation: Architecture Diagram, ER Diagram, API Reference, Testing Report

