from datetime import datetime, timedelta, timezone


def test_create_booking_success(client, user_headers, centre_with_test):
    centre, test = centre_with_test
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    response = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["centre_id"] == centre.id
    assert data["test_id"] == test.id
    assert float(data["amount"]) == float(test.price)
    assert data["status"] == "PENDING"
    assert "id" in data


def test_create_booking_invalid_centre(client, user_headers, sample_test):
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": 99999,
            "test_id": sample_test.id,
            "appointment_datetime": future_time,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Diagnostic centre not found"


def test_create_booking_invalid_test(client, user_headers, sample_centre):
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": sample_centre.id,
            "test_id": 99999,
            "appointment_datetime": future_time,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Diagnostic test not found"


def test_create_booking_unassigned_test_at_centre(client, user_headers, sample_centre, sample_test):
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": sample_centre.id,
            "test_id": sample_test.id,
            "appointment_datetime": future_time,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Selected diagnostic test is not available at this diagnostic centre"


def test_create_booking_past_datetime(client, user_headers, centre_with_test):
    centre, test = centre_with_test
    past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    response = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": past_time,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Appointment datetime must be in the future"


def test_unauthorized_user_access_booking(client, user_headers, other_user_headers, centre_with_test):
    centre, test = centre_with_test
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    # User 1 creates booking
    res = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    booking_id = res.json()["id"]

    # User 2 attempts to get User 1's booking
    res_other = client.get(f"/bookings/{booking_id}", headers=other_user_headers)
    assert res_other.status_code == 403
    assert res_other.json()["detail"] == "Not authorized to access another user's booking"


def test_admin_access_any_booking(client, user_headers, admin_headers, centre_with_test):
    centre, test = centre_with_test
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    # User creates booking
    res = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    booking_id = res.json()["id"]

    # Admin accesses booking
    res_admin = client.get(f"/bookings/{booking_id}", headers=admin_headers)
    assert res_admin.status_code == 200
    assert res_admin.json()["id"] == booking_id


def test_cancel_booking(client, user_headers, centre_with_test):
    centre, test = centre_with_test
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    res = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    booking_id = res.json()["id"]

    # Cancel booking
    cancel_res = client.patch(f"/bookings/{booking_id}/cancel", headers=user_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    # Attempt to cancel again
    cancel_again = client.patch(f"/bookings/{booking_id}/cancel", headers=user_headers)
    assert cancel_again.status_code == 400
    assert cancel_again.json()["detail"] == "Booking is already cancelled"
