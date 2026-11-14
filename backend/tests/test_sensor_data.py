"""
Unit tests for Sensor Data Ingestion, Cleaning & Normalization, and Simulation.
"""

from datetime import datetime, timezone


def test_sensor_data_ingestion_and_simulation(client):
    # Setup farmer, field, sensor
    f_res = client.post("/api/v1/farmers/", json={"name": "Pooja Sharma", "email": "pooja@agri.in"})
    farmer_id = f_res.json()["id"]

    field_res = client.post(
        "/api/v1/fields/",
        json={
            "farmer_id": farmer_id,
            "field_name": "Test Field 1",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "area_hectares": 3.0,
        },
    )
    field_id = field_res.json()["id"]

    s_res = client.post(
        "/api/v1/sensors/",
        json={"sensor_id": "SN-TEST-001", "field_id": field_id},
    )
    sensor_id = s_res.json()["sensor_id"]

    # 1. Ingest single reading
    reading_payload = {
        "sensor_id": sensor_id,
        "field_id": field_id,
        "soil_moisture_percent": 45.5,
        "temperature_celsius": 24.2,
        "is_simulated": False,
        "quality_flag": "VALID",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    r_res = client.post("/api/v1/sensor-data/", json=reading_payload)
    assert r_res.status_code == 201
    assert r_res.json()["soil_moisture_percent"] == 45.5
    assert r_res.json()["quality_flag"] == "VALID"

    # 2. Ingest batch
    batch_payload = {
        "readings": [
            {
                "sensor_id": sensor_id,
                "field_id": field_id,
                "soil_moisture_percent": 46.0,
                "temperature_celsius": 24.0,
                "is_simulated": False,
                "quality_flag": "VALID",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ]
    }
    b_res = client.post("/api/v1/sensor-data/batch", json=batch_payload)
    assert b_res.status_code == 201
    assert len(b_res.json()) >= 1

    # 3. Trigger simulation for 1 day
    sim_res = client.post(f"/api/v1/sensor-data/simulate/{sensor_id}?days=1&interval_minutes=60")
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert len(sim_data) > 0
    assert sim_data[0]["is_simulated"] is True
    assert sim_data[0]["quality_flag"] == "SIMULATED"

    # 4. Query sensor readings
    history_res = client.get(f"/api/v1/sensor-data/{sensor_id}?limit=50")
    assert history_res.status_code == 200
    assert len(history_res.json()) > 0

