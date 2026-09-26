from datetime import datetime, timedelta, timezone


def test_successful_payment_by_booking_owner(client, user_headers, centre_with_test):
    """Case A & H: Successful payment by booking owner with correct amount."""
    centre, test = centre_with_test
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    # Create booking
    b_res = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    booking = b_res.json()

    # Process payment by owner
    pay_res = client.post(
        "/payments/",
        headers=user_headers,
        json={
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "SUCCESS",
            "provider_transaction_id": "txn_owner_101",
        },
    )
    assert pay_res.status_code == 201
    pay_data = pay_res.json()
    assert pay_data["status"] == "SUCCESS"
    assert pay_data["booking_id"] == booking["id"]

    # Verify booking status updated to CONFIRMED
    get_b = client.get(f"/bookings/{booking['id']}", headers=user_headers)
    assert get_b.json()["status"] == "CONFIRMED"


def test_admin_payment_for_another_user_booking(client, user_headers, admin_headers, centre_with_test):
    """Case B: Admin payment for another user's booking."""
    centre, test = centre_with_test
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    # User creates booking
    b_res = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    booking = b_res.json()

    # Admin processes payment for user's booking
    pay_res = client.post(
        "/payments/",
        headers=admin_headers,
        json={
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "SUCCESS",
        },
    )
    assert pay_res.status_code == 201
    assert pay_res.json()["status"] == "SUCCESS"


def test_non_owner_attempt_payment_forbidden(client, user_headers, other_user_headers, centre_with_test):
    """Case C: Non-owner user attempting payment on another user's booking -> 403."""
    centre, test = centre_with_test
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    # User 1 creates booking
    b_res = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    booking = b_res.json()

    # User 2 attempts payment on User 1's booking
    pay_res = client.post(
        "/payments/",
        headers=other_user_headers,
        json={
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "SUCCESS",
        },
    )
    assert pay_res.status_code == 403
    assert pay_res.json()["detail"] == "Not authorized to process payment for another user's booking"


def test_payment_on_failed_booking_rejected(client, user_headers, centre_with_test):
    """Case D: Payment on FAILED booking -> 400."""
    centre, test = centre_with_test
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    # Create booking
    b_res = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    booking = b_res.json()

    # Fail payment first
    fail_res = client.post(
        "/payments/",
        headers=user_headers,
        json={
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "FAILED",
        },
    )
    assert fail_res.status_code == 201

    # Attempt second payment on now-FAILED booking
    retry_res = client.post(
        "/payments/",
        headers=user_headers,
        json={
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "SUCCESS",
        },
    )
    assert retry_res.status_code == 400
    assert "Cannot process payment for a booking with status 'FAILED'" in retry_res.json()["detail"]


def test_payment_on_cancelled_booking_rejected(client, user_headers, centre_with_test):
    """Case E: Payment on CANCELLED booking -> 400."""
    centre, test = centre_with_test
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    b_res = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    booking = b_res.json()

    # Cancel booking
    client.patch(f"/bookings/{booking['id']}/cancel", headers=user_headers)

    # Attempt payment
    pay_res = client.post(
        "/payments/",
        headers=user_headers,
        json={
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "SUCCESS",
        },
    )
    assert pay_res.status_code == 400
    assert "Cannot process payment for a booking with status 'CANCELLED'" in pay_res.json()["detail"]


def test_payment_on_confirmed_booking_rejected(client, user_headers, centre_with_test):
    """Case F & L: Payment on CONFIRMED booking / duplicate successful payment -> 400."""
    centre, test = centre_with_test
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    b_res = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    booking = b_res.json()

    # First successful payment
    pay1 = client.post(
        "/payments/",
        headers=user_headers,
        json={
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "SUCCESS",
        },
    )
    assert pay1.status_code == 201

    # Duplicate payment attempt
    pay2 = client.post(
        "/payments/",
        headers=user_headers,
        json={
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "SUCCESS",
        },
    )
    assert pay2.status_code == 400
    assert "Cannot process payment for a booking with status 'CONFIRMED'" in pay2.json()["detail"]


def test_incorrect_payment_amount_rejected(client, user_headers, centre_with_test):
    """Case G: Incorrect payment amount -> 400."""
    centre, test = centre_with_test
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    b_res = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    booking = b_res.json()

    pay_res = client.post(
        "/payments/",
        headers=user_headers,
        json={
            "booking_id": booking["id"],
            "amount": 9.99,  # Incorrect amount
            "status": "SUCCESS",
        },
    )
    assert pay_res.status_code == 400
    assert "does not match booking amount" in pay_res.json()["detail"]
