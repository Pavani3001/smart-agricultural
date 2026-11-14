"""
Unit tests for Sensor registration and management.
"""

def test_sensor_registration_and_query(client):
    # Setup farmer and field
    f_res = client.post("/api/v1/farmers/", json={"name": "Vikram Singh", "email": "vikram@agri.in"})
    farmer_id = f_res.json()["id"]

    field_res = client.post(
        "/api/v1/fields/",
        json={
            "farmer_id": farmer_id,
            "field_name": "Plot A",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "area_hectares": 1.2,
        },
    )
    field_id = field_res.json()["id"]

    # Register sensor
    sensor_payload = {
        "sensor_id": "SN-MOIST-101",
        "field_id": field_id,
        "sensor_type": "capacitive_soil_moisture",
        "status": "active",
    }
    s_res = client.post("/api/v1/sensors/", json=sensor_payload)
    assert s_res.status_code == 201
    assert s_res.json()["sensor_id"] == "SN-MOIST-101"

    # List sensors
    list_res = client.get(f"/api/v1/sensors/?field_id={field_id}")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # Get by sensor_id
    get_res = client.get("/api/v1/sensors/SN-MOIST-101")
    assert get_res.status_code == 200
    assert get_res.json()["field_id"] == field_id

