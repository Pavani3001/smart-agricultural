"""
Unit tests for Farmer CRUD API endpoints.
"""

def test_create_and_get_farmer(client):
    # Create farmer
    payload = {
        "name": "Ramesh Kumar",
        "email": "ramesh.kumar@agri.in",
        "phone": "+91-9876543210",
        "address": "Village Kothur, Telangana",
    }
    response = client.post("/api/v1/farmers/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    farmer_id = data["id"]

    # Get farmer by ID
    get_res = client.get(f"/api/v1/farmers/{farmer_id}")
    assert get_res.status_code == 200
    assert get_res.json()["email"] == payload["email"]

    # List farmers
    list_res = client.get("/api/v1/farmers/")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_duplicate_farmer_email(client):
    payload = {
        "name": "Suresh Patel",
        "email": "suresh.patel@agri.in",
        "phone": "+91-9123456780",
    }
    res1 = client.post("/api/v1/farmers/", json=payload)
    assert res1.status_code == 201

    # Attempt duplicate
    res2 = client.post("/api/v1/farmers/", json=payload)
    assert res2.status_code == 409


def test_farmer_not_found(client):
    res = client.get("/api/v1/farmers/9999")
    assert res.status_code == 404

