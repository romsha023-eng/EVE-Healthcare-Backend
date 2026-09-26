from datetime import timedelta
from app.core.security import create_access_token


def test_signup_success(client):
    response = client.post(
        "/auth/signup",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "password": "securepassword123",
            "role": "USER",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["name"] == "Alice Smith"
    assert data["role"] == "USER"
    assert "password_hash" not in data
    assert "id" in data


def test_signup_duplicate_email(client):
    payload = {
        "name": "Bob Jones",
        "email": "bob@example.com",
        "password": "password123",
    }
    res1 = client.post("/auth/signup", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/auth/signup", json=payload)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Email is already registered"


def test_login_success(client, normal_user):
    response = client.post(
        "/auth/login",
        json={
            "email": "john@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "john@example.com"


def test_login_invalid_password(client, normal_user):
    response = client.post(
        "/auth/login",
        json={
            "email": "john@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "nobody@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_missing_token_access(client):
    response = client.get("/bookings/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authentication token"


def test_invalid_token_access(client):
    response = client.get(
        "/bookings/",
        headers={"Authorization": "Bearer invalid_token_string"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_expired_token_access(client):
    expired_token = create_access_token(
        data={"sub": "1", "email": "test@example.com"},
        expires_delta=timedelta(seconds=-10)
    )
    response = client.get(
        "/bookings/",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"
