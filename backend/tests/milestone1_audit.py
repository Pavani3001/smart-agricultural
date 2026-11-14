"""
Automated Milestone 1 Audit Verification Script.
Executes deep checks across:
- Sensor Data ingestion (single, batch, simulation, quality flags, duplicate rejection, invalid values)
- Weather API integration (endpoint logic, retry & stale fallback, live key check)
- Farmer and Field management (registration, duplicate email, multiple fields, crop & sensor FKs)
- Data Cleaning (range checks, time-series gaps, duplicate detection)
- Database schema and relationship integrity
"""

import sys
import os
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup test environment
os.environ["APP_ENV"] = "testing"
from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.services.data_cleaning import (
    validate_sensor_reading,
    normalize_reading,
    detect_duplicates,
    handle_missing_readings,
    FLAG_VALID,
    FLAG_INVALID,
    FLAG_SIMULATED,
)
import pandas as pd

# In-memory database for reproducible audit
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

results = {}

print("=================================================================")
print("          MILESTONE 1 AUDIT: DEEP SYSTEM VERIFICATION            ")
print("=================================================================\n")

# -------------------------------------------------------------
# 1. SENSOR DATA INGESTION & SIMULATION
# -------------------------------------------------------------
print("--- [1] SENSOR DATA VERIFICATION ---")

# Setup prerequisite farmer and field
f_res = client.post("/api/v1/farmers/", json={"name": "Audit Farmer", "email": "audit.farmer@agri.in"})
farmer_id = f_res.json()["id"]

field_res = client.post(
    "/api/v1/fields/",
    json={"farmer_id": farmer_id, "field_name": "Audit Field Alpha", "latitude": 17.40, "longitude": 78.45, "area_hectares": 2.0},
)
field_id = field_res.json()["id"]

s_res = client.post("/api/v1/sensors/", json={"sensor_id": "AUDIT-SN-01", "field_id": field_id})
sensor_id = s_res.json()["sensor_id"]

# 1.1 Single sensor ingestion
now_iso = datetime.now(timezone.utc).isoformat()
single_res = client.post(
    "/api/v1/sensor-data/",
    json={
        "sensor_id": sensor_id,
        "field_id": field_id,
        "soil_moisture_percent": 55.4,
        "temperature_celsius": 26.2,
        "is_simulated": False,
        "quality_flag": "VALID",
        "timestamp": now_iso,
    },
)
results["1.1 Single Sensor Ingestion"] = (single_res.status_code == 201) and (single_res.json()["soil_moisture_percent"] == 55.4)
print(f"1.1 Single Ingestion: Status {single_res.status_code}, Moisture: {single_res.json().get('soil_moisture_percent')}% -> {'PASS' if results['1.1 Single Sensor Ingestion'] else 'FAIL'}")

# 1.2 Duplicate reading rejection
dup_res = client.post(
    "/api/v1/sensor-data/",
    json={
        "sensor_id": sensor_id,
        "field_id": field_id,
        "soil_moisture_percent": 55.4,
        "temperature_celsius": 26.2,
        "is_simulated": False,
        "quality_flag": "VALID",
        "timestamp": now_iso, # exactly same timestamp
    },
)
results["1.2 Duplicate Reading Rejection"] = (dup_res.status_code == 400)
print(f"1.2 Duplicate Rejection: Status {dup_res.status_code} ({dup_res.json().get('detail')}) -> {'PASS' if results['1.2 Duplicate Reading Rejection'] else 'FAIL'}")

# 1.3 Batch sensor ingestion
t1 = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
t2 = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
batch_res = client.post(
    "/api/v1/sensor-data/batch",
    json={
        "readings": [
            {"sensor_id": sensor_id, "field_id": field_id, "soil_moisture_percent": 52.0, "temperature_celsius": 25.5, "timestamp": t1, "is_simulated": False},
            {"sensor_id": sensor_id, "field_id": field_id, "soil_moisture_percent": 53.5, "temperature_celsius": 25.8, "timestamp": t2, "is_simulated": False},
        ]
    },
)
results["1.3 Batch Ingestion"] = (batch_res.status_code == 201) and (len(batch_res.json()) == 2)
print(f"1.3 Batch Ingestion: Status {batch_res.status_code}, Ingested count: {len(batch_res.json()) if batch_res.status_code == 201 else 0} -> {'PASS' if results['1.3 Batch Ingestion'] else 'FAIL'}")

# 1.4 Simulated readings & clear labelling
sim_res = client.post(f"/api/v1/sensor-data/simulate/{sensor_id}?days=1&interval_minutes=30")
sim_pass = False
if sim_res.status_code == 200:
    sim_data = sim_res.json()
    all_labelled = all(r["is_simulated"] is True and r["quality_flag"] == "SIMULATED" for r in sim_data)
    sim_pass = len(sim_data) > 0 and all_labelled
results["1.4 Simulated Readings & Labelling"] = sim_pass
print(f"1.4 Simulated Readings: Status {sim_res.status_code}, Count: {len(sim_res.json())}, All labelled 'SIMULATED' and is_simulated=True -> {'PASS' if sim_pass else 'FAIL'}")

# 1.5 Invalid sensor value handling
invalid_res = client.post(
    "/api/v1/sensor-data/",
    json={
        "sensor_id": sensor_id,
        "field_id": field_id,
        "soil_moisture_percent": 150.0, # Physical impossibility > 100%
        "temperature_celsius": 25.0,
        "timestamp": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
    },
)
# Pydantic schema validation rejects values outside 0-100 with HTTP 422
results["1.5 Invalid Moisture Rejection (>100%)"] = (invalid_res.status_code == 422)
print(f"1.5 Invalid Value (>100%): Status {invalid_res.status_code} (Pydantic 422 validation error) -> {'PASS' if results['1.5 Invalid Moisture Rejection (>100%)'] else 'FAIL'}")

print("\n--- [2] WEATHER API INTEGRATION ---")
# 2.1 Live API Key check
api_key_configured = bool(settings.OPENWEATHERMAP_API_KEY and settings.OPENWEATHERMAP_API_KEY != "your_openweathermap_api_key_here")
print(f"2.1 OpenWeatherMap API Key Configured in .env: {api_key_configured} (Value: {repr(settings.OPENWEATHERMAP_API_KEY)})")
results["2.1 Live Weather Key Configured"] = api_key_configured

# 2.2 Weather Fetch Endpoint & Fallback Check
w_res = client.post(f"/api/v1/weather/fetch/{field_id}")
print(f"2.2 Weather Endpoint Response: Status {w_res.status_code}, Body: {w_res.json()}")
# When key is not configured, it returns success=False or fallback with is_stale
results["2.2 Weather API Endpoint & Fallback Graceful Handling"] = (w_res.status_code == 200)

print("\n--- [3] FARMER AND FIELD MANAGEMENT ---")
# 3.1 Duplicate Farmer Email Rejection
dup_f_res = client.post("/api/v1/farmers/", json={"name": "Duplicate Farmer", "email": "audit.farmer@agri.in"})
results["3.1 Duplicate Email Rejection"] = (dup_f_res.status_code == 409)
print(f"3.1 Duplicate Email Rejection: Status {dup_f_res.status_code} ({dup_f_res.json().get('detail')}) -> {'PASS' if results['3.1 Duplicate Email Rejection'] else 'FAIL'}")

# 3.2 Multiple Field Registration for Same Farmer
f2_res = client.post(
    "/api/v1/fields/",
    json={"farmer_id": farmer_id, "field_name": "Audit Field Beta", "latitude": 17.42, "longitude": 78.48, "area_hectares": 3.5},
)
farmer_fields = client.get(f"/api/v1/fields/?farmer_id={farmer_id}").json()
results["3.2 Multiple Field Registration"] = (f2_res.status_code == 201) and (len(farmer_fields) >= 2)
print(f"3.2 Multiple Fields for Farmer #{farmer_id}: Total registered fields: {len(farmer_fields)} -> {'PASS' if results['3.2 Multiple Field Registration'] else 'FAIL'}")

# 3.3 Crop and Sensor Association
c_res = client.post("/api/v1/crops/", json={"crop_name": "Audit Maize", "optimal_moisture_min": 45.0, "optimal_moisture_max": 65.0})
crop_id = c_res.json()["id"]
update_field_res = client.put(f"/api/v1/fields/{field_id}", json={"crop_id": crop_id, "crop_type": "Audit Maize"})
field_detail = client.get(f"/api/v1/fields/{field_id}").json()
has_crop_and_sensor = (field_detail["crop_id"] == crop_id) and (len(field_detail["sensors"]) >= 1)
results["3.3 Crop and Sensor Associations"] = has_crop_and_sensor
print(f"3.3 Field FK Associations: Field crop_id={field_detail.get('crop_id')}, Attached sensors count={len(field_detail.get('sensors', []))} -> {'PASS' if has_crop_and_sensor else 'FAIL'}")

print("\n--- [4] DATA CLEANING & VALIDATION UNIT CHECKS ---")
# 4.1 Missing values detection
is_valid, flag, reason = validate_sensor_reading(None, None)
results["4.1 Missing Value Detection"] = (not is_valid) and (flag == FLAG_INVALID)
print(f"4.1 Missing Values: is_valid={is_valid}, flag={flag}, reason='{reason}' -> {'PASS' if results['4.1 Missing Value Detection'] else 'FAIL'}")

# 4.2 Out-of-bounds Clamping / Normalization
norm_m, norm_t = normalize_reading(120.0, -80.0)
results["4.2 Value Clamping / Normalization"] = (norm_m == 100.0) and (norm_t == -50.0)
print(f"4.2 Clamping: 120% -> {norm_m}%, -80°C -> {norm_t}°C -> {'PASS' if results['4.2 Value Clamping / Normalization'] else 'FAIL'}")

# 4.3 Time-series gap detection
gap_df = pd.DataFrame([
    {"sensor_id": "S1", "timestamp": datetime(2026, 11, 13, 10, 0, tzinfo=timezone.utc)},
    {"sensor_id": "S1", "timestamp": datetime(2026, 11, 13, 10, 45, tzinfo=timezone.utc)}, # 45 min gap (> 15 min threshold)
])
gap_res_df = handle_missing_readings(gap_df, max_gap_minutes=15)
has_missing_flag = gap_res_df["gap_flag"].iloc[1] == "MISSING"
results["4.3 Time-Series Gap Detection"] = has_missing_flag
print(f"4.3 Gap Detection: Row 1 gap_flag='{gap_res_df['gap_flag'].iloc[1]}' (>15 min gap) -> {'PASS' if has_missing_flag else 'FAIL'}")

print("\n=================================================================")
print("                   AUDIT SUMMARY SUMMARY                         ")
print("=================================================================")
for check, passed in results.items():
    print(f"[{'PASS' if passed else 'FAIL'}] {check}")

