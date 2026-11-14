# 📖 Milestone 1 REST API Documentation

## AI-Powered Smart Irrigation System
**Base URL**: `http://localhost:8000/api/v1`  
**Swagger UI**: `http://localhost:8000/docs`  
**ReDoc**: `http://localhost:8000/redoc`

---

## 1. System & Dashboard Endpoints

### 1.1 Health Check
- **Endpoint**: `GET /health`
- **Description**: Verifies API operational status and service environment.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "environment": "development",
  "database_connected": true
}
```

### 1.2 Dashboard Summary Statistics
- **Endpoint**: `GET /stats/dashboard`
- **Description**: Returns live aggregated counts across all entities.
- **Response `200 OK`**:
```json
{
  "total_farmers": 12,
  "total_fields": 28,
  "active_fields": 25,
  "total_sensors": 45,
  "active_sensors": 42,
  "total_sensor_readings": 2840,
  "simulated_sensor_readings": 2840,
  "total_weather_records": 196
}
```

---

## 2. Farmers API (`/farmers`)

| Method | Route | Description | Status Code |
|---|---|---|---|
| `POST` | `/farmers/` | Register a new farmer | `201 Created` |
| `GET` | `/farmers/` | List all farmers (supports `skip`, `limit`) | `200 OK` |
| `GET` | `/farmers/{farmer_id}` | Retrieve specific farmer details | `200 OK` |
| `PUT` | `/farmers/{farmer_id}` | Update profile information | `200 OK` |
| `DELETE`| `/farmers/{farmer_id}` | Delete farmer (cascades to fields/sensors) | `204 No Content` |

#### Sample Request (`POST /farmers/`):
```json
{
  "name": "Ramesh Patel",
  "email": "ramesh.patel@agri.in",
  "phone": "+91-9876543210",
  "address": "Village Kothur, Ranga Reddy District, Telangana"
}
```

---

## 3. Fields API (`/fields`)

| Method | Route | Description | Status Code |
|---|---|---|---|
| `POST` | `/fields/` | Register an agricultural plot with GPS | `201 Created` |
| `GET` | `/fields/` | List fields (filter: `?farmer_id=1`) | `200 OK` |
| `GET` | `/fields/{field_id}` | Retrieve field with attached sensor nodes | `200 OK` |
| `PUT` | `/fields/{field_id}` | Update field location, soil type, or status | `200 OK` |
| `DELETE`| `/fields/{field_id}` | Delete field and unregister sensors | `204 No Content` |

#### Sample Request (`POST /fields/`):
```json
{
  "farmer_id": 1,
  "crop_id": 2,
  "field_name": "Sector 3 - North Paddy",
  "latitude": 17.385044,
  "longitude": 78.486671,
  "area_hectares": 2.5,
  "crop_type": "Rice",
  "soil_type": "alluvial",
  "status": "active"
}
```

---

## 4. Crops API (`/crops`)

| Method | Route | Description | Status Code |
|---|---|---|---|
| `POST` | `/crops/` | Add crop threshold configuration | `201 Created` |
| `GET` | `/crops/` | List all crop configurations | `200 OK` |
| `GET` | `/crops/{crop_id}` | Retrieve crop profile and thresholds | `200 OK` |
| `PUT` | `/crops/{crop_id}` | Update optimal moisture bounds | `200 OK` |

#### Sample Request (`POST /crops/`):
```json
{
  "crop_name": "Paddy Rice (IR64)",
  "optimal_moisture_min": 60.0,
  "optimal_moisture_max": 80.0,
  "growth_stage": "vegetative",
  "water_requirement_mm": 1200,
  "season": "Kharif",
  "description": "High water demand cereal crop requiring submerged or saturated soil conditions"
}
```

---

## 5. Sensors API (`/sensors`)

| Method | Route | Description | Status Code |
|---|---|---|---|
| `POST` | `/sensors/` | Register hardware/virtual sensor node | `201 Created` |
| `GET` | `/sensors/` | List sensors (filter: `?field_id=1`) | `200 OK` |
| `GET` | `/sensors/{sensor_id}` | Retrieve sensor status and telemetry meta | `200 OK` |
| `PUT` | `/sensors/{sensor_id}` | Update sensor status or assigned field | `200 OK` |
| `DELETE`| `/sensors/{sensor_id}` | Remove sensor from registry | `204 No Content` |

---

## 6. Sensor Ingestion & Simulation API (`/sensor-data`)

### 6.1 Ingest Single Reading
- **Endpoint**: `POST /sensor-data/`
- **Request Body**:
```json
{
  "sensor_id": "SN-MOIST-101",
  "field_id": 1,
  "soil_moisture_percent": 48.2,
  "temperature_celsius": 26.5,
  "is_simulated": false,
  "quality_flag": "VALID",
  "timestamp": "2026-11-13T09:30:00Z"
}
```

### 6.2 Batch Telemetry Ingestion
- **Endpoint**: `POST /sensor-data/batch`
- **Request Body**: Array of readings under `{ "readings": [...] }`. Cleans and normalizes in batch via Pandas.

### 6.3 Query Telemetry History
- **Endpoint**: `GET /sensor-data/{sensor_id}?limit=100&start_time=...&end_time=...`
- **Returns**: Historical time-series sorted by timestamp descending.

### 6.4 Trigger 7-Day IoT Simulation
- **Endpoint**: `POST /sensor-data/simulate/{sensor_id}?days=7&interval_minutes=15`
- **Description**: Synthesizes 672 readings using random-walk and diurnal temperature cycles.
- **Labels**: Every record is tagged with `is_simulated = true` and `quality_flag = 'SIMULATED'`.

---

## 7. Weather API (`/weather`)

### 7.1 Fetch Live Weather for Field
- **Endpoint**: `POST /weather/fetch/{field_id}`
- **Description**: Calls OpenWeatherMap API using field GPS coordinates. Retries 3x on network failure and falls back to last known cached reading if API is down.
- **Response `200 OK`**:
```json
{
  "success": true,
  "message": "Weather fetched successfully",
  "data": {
    "id": 14,
    "field_id": 1,
    "temperature_celsius": 29.4,
    "humidity_percent": 68.0,
    "rainfall_mm": 0.0,
    "wind_speed_ms": 3.6,
    "weather_condition": "Clouds",
    "description": "scattered clouds",
    "data_source": "openweathermap",
    "timestamp": "2026-11-13T10:00:00Z",
    "fetched_at": "2026-11-13T10:00:01Z"
  },
  "is_stale": false
}
```

### 7.2 Query Historical Weather
- **Endpoint**: `GET /weather/{field_id}?limit=50`
- **Description**: Returns chronological weather records for analytics and trend visualization.

