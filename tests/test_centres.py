def test_create_centre_admin(client, admin_headers):
    response = client.post(
        "/centres/",
        headers=admin_headers,
        json={
            "name": "Central Diagnostic Lab",
            "location": "456 Market St, City Center",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Central Diagnostic Lab"
    assert data["location"] == "456 Market St, City Center"
    assert "id" in data


def test_create_centre_normal_user_forbidden(client, user_headers):
    response = client.post(
        "/centres/",
        headers=user_headers,
        json={
            "name": "Unauthorized Centre",
            "location": "Somewhere",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required for this operation"


def test_list_centres(client, sample_centre):
    response = client.get("/centres/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == sample_centre.name


def test_get_centre_detail(client, sample_centre):
    response = client.get(f"/centres/{sample_centre.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_centre.id
    assert data["name"] == sample_centre.name
    assert "tests" in data


def test_get_nonexistent_centre(client):
    response = client.get("/centres/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Diagnostic centre not found"


def test_create_test_admin(client, admin_headers):
    response = client.post(
        "/tests/",
        headers=admin_headers,
        json={
            "name": "Blood Sugar (Fast)",
            "description": "Fasting blood glucose test",
            "price": 35.50,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Blood Sugar (Fast)"
    assert float(data["price"]) == 35.50


def test_create_test_normal_user_forbidden(client, user_headers):
    response = client.post(
        "/tests/",
        headers=user_headers,
        json={
            "name": "X-Ray Chest",
            "price": 80.00,
        },
    )
    assert response.status_code == 403


def test_assign_test_to_centre(client, admin_headers, sample_centre, sample_test):
    response = client.post(
        f"/centres/{sample_centre.id}/tests/{sample_test.id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["tests"]) == 1
    assert data["tests"][0]["id"] == sample_test.id


def test_remove_test_from_centre(client, admin_headers, centre_with_test):
    centre, test = centre_with_test
    response = client.delete(
        f"/centres/{centre.id}/tests/{test.id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["tests"]) == 0
