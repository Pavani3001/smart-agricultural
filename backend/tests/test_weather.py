"""
Unit tests for Weather endpoints (including fallback when API key is unconfigured).
"""

def test_weather_endpoints(client):
    # Setup farmer and field
    f_res = client.post("/api/v1/farmers/", json={"name": "Rajesh Varma", "email": "rajesh@agri.in"})
    farmer_id = f_res.json()["id"]

    field_res = client.post(
        "/api/v1/fields/",
        json={
            "farmer_id": farmer_id,
            "field_name": "Weather Test Plot",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "area_hectares": 1.5,
        },
    )
    field_id = field_res.json()["id"]

    # 1. Weather fetch endpoint (without real key will trigger safe fallback)
    fetch_res = client.post(f"/api/v1/weather/fetch/{field_id}")
    assert fetch_res.status_code == 200
    res_json = fetch_res.json()
    assert "success" in res_json

    # 2. History endpoint
    hist_res = client.get(f"/api/v1/weather/{field_id}")
    assert hist_res.status_code == 200
    assert isinstance(hist_res.json(), list)

    # 3. Current weather endpoint
    cur_res = client.get(f"/api/v1/weather/current/{field_id}")
    assert cur_res.status_code == 200

