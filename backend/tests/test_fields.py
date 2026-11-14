"""
Unit tests for Field and Crop CRUD API endpoints.
"""

def test_crop_and_field_lifecycle(client):
    # 1. Create a crop
    crop_payload = {
        "crop_name": "Test Rice",
        "optimal_moisture_min": 60.0,
        "optimal_moisture_max": 80.0,
        "growth_stage": "vegetative",
        "water_requirement_mm": 1100,
        "season": "Kharif",
    }
    crop_res = client.post("/api/v1/crops/", json=crop_payload)
    assert crop_res.status_code == 201
    crop_id = crop_res.json()["id"]

    # 2. Create farmer
    farmer_res = client.post(
        "/api/v1/farmers/",
        json={"name": "Anita Devi", "email": "anita.devi@agri.in"},
    )
    assert farmer_res.status_code == 201
    farmer_id = farmer_res.json()["id"]

    # 3. Create field
    field_payload = {
        "farmer_id": farmer_id,
        "crop_id": crop_id,
        "field_name": "North Field - Sector 4",
        "latitude": 17.385044,
        "longitude": 78.486671,
        "area_hectares": 2.5,
        "crop_type": "Test Rice",
        "soil_type": "alluvial",
        "status": "active",
    }
    field_res = client.post("/api/v1/fields/", json=field_payload)
    assert field_res.status_code == 201
    field_data = field_res.json()
    assert field_data["field_name"] == field_payload["field_name"]
    assert field_data["latitude"] == field_payload["latitude"]
    field_id = field_data["id"]

    # 4. Filter fields by farmer
    list_res = client.get(f"/api/v1/fields/?farmer_id={farmer_id}")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
    assert list_res.json()[0]["id"] == field_id

