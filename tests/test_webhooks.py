from datetime import datetime, timedelta, timezone


def test_successful_webhook(client, user_headers, centre_with_test):
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

    webhook_res = client.post(
        "/payments/webhook/",
        json={
            "event_id": "evt_wh_100",
            "payment_id": "pay_wh_100",
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "SUCCESS",
        },
    )
    assert webhook_res.status_code == 200
    assert webhook_res.json()["processed"] is True

    get_b = client.get(f"/bookings/{booking['id']}", headers=user_headers)
    assert get_b.json()["status"] == "CONFIRMED"


def test_webhook_mismatched_amount_rejected(client, user_headers, centre_with_test):
    """Case 9: Webhook with mismatched amount -> 400."""
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

    webhook_res = client.post(
        "/payments/webhook/",
        json={
            "event_id": "evt_bad_amt",
            "payment_id": "pay_bad_amt",
            "booking_id": booking["id"],
            "amount": 1.00,  # Mismatched amount
            "status": "SUCCESS",
        },
    )
    assert webhook_res.status_code == 400
    assert webhook_res.json()["detail"] == "Payment amount in webhook does not match booking amount"

    # Verify booking status remains PENDING
    get_b = client.get(f"/bookings/{booking['id']}", headers=user_headers)
    assert get_b.json()["status"] == "PENDING"


def test_webhook_already_confirmed_booking_no_duplicate_payment(client, user_headers, centre_with_test):
    """Case 10 & 11: Webhook for already CONFIRMED booking does not create duplicate payment."""
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

    # Confirm booking via /payments/
    client.post(
        "/payments/",
        headers=user_headers,
        json={
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "SUCCESS",
        },
    )

    # Webhook arrives for already confirmed booking
    wh_res = client.post(
        "/payments/webhook/",
        json={
            "event_id": "evt_after_confirm",
            "payment_id": "pay_after_confirm",
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "SUCCESS",
        },
    )
    assert wh_res.status_code == 200
    assert wh_res.json()["processed"] is False
    assert wh_res.json()["message"] == "Booking is already confirmed/paid"


def test_duplicate_webhook_event_idempotency(client, user_headers, centre_with_test):
    """Case 12: Duplicate webhook event remains idempotent."""
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

    payload = {
        "event_id": "evt_repeat_999",
        "payment_id": "pay_repeat_999",
        "booking_id": booking["id"],
        "amount": booking["amount"],
        "status": "SUCCESS",
    }

    res1 = client.post("/payments/webhook/", json=payload)
    assert res1.status_code == 200
    assert res1.json()["processed"] is True

    # Duplicate call with exact same event_id
    res2 = client.post("/payments/webhook/", json=payload)
    assert res2.status_code == 200
    assert res2.json()["processed"] is False
    assert res2.json()["message"] == "Event already processed"


def test_webhook_cannot_change_failed_to_confirmed(client, user_headers, centre_with_test):
    """Case 13: SUCCESS webhook cannot change FAILED -> CONFIRMED."""
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

    # Fail payment first via /payments/
    client.post(
        "/payments/",
        headers=user_headers,
        json={
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "FAILED",
        },
    )

    # Webhook with SUCCESS arrives for FAILED booking
    wh_res = client.post(
        "/payments/webhook/",
        json={
            "event_id": "evt_override_failed",
            "payment_id": "pay_override_failed",
            "booking_id": booking["id"],
            "amount": booking["amount"],
            "status": "SUCCESS",
        },
    )
    assert wh_res.status_code == 200
    assert wh_res.json()["processed"] is False
    assert "Booking is in FAILED state" in wh_res.json()["message"]

    # Booking status must remain FAILED
    get_b = client.get(f"/bookings/{booking['id']}", headers=user_headers)
    assert get_b.json()["status"] == "FAILED"


def test_webhook_invalid_booking_id(client):
    """Case 14: Webhook with invalid booking ID is rejected -> 404."""
    webhook_res = client.post(
        "/payments/webhook/",
        json={
            "event_id": "evt_nonexistent_booking",
            "payment_id": "pay_inv",
            "booking_id": 99999,
            "status": "SUCCESS",
        },
    )
    assert webhook_res.status_code == 404
    assert "Booking not found" in webhook_res.json()["detail"]


def test_webhook_inconsistent_payment_id_rejected(client, user_headers, centre_with_test):
    """Case 15: Webhook with payment_id assigned to a different booking is rejected -> 400."""
    centre, test = centre_with_test
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    # Create Booking 1 & pay for it with payment_id="pay_shared_001"
    b1_res = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    booking1 = b1_res.json()
    client.post(
        "/payments/",
        headers=user_headers,
        json={
            "booking_id": booking1["id"],
            "amount": booking1["amount"],
            "status": "SUCCESS",
            "provider_transaction_id": "pay_shared_001",
        },
    )

    # Create Booking 2
    b2_res = client.post(
        "/bookings/",
        headers=user_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_datetime": future_time,
        },
    )
    booking2 = b2_res.json()

    # Webhook for Booking 2 attempts to use payment_id "pay_shared_001" (which belongs to Booking 1)
    wh_res = client.post(
        "/payments/webhook/",
        json={
            "event_id": "evt_inconsistent_txn",
            "payment_id": "pay_shared_001",
            "booking_id": booking2["id"],
            "amount": booking2["amount"],
            "status": "SUCCESS",
        },
    )
    assert wh_res.status_code == 400
    assert wh_res.json()["detail"] == "Payment ID is associated with a different booking"
