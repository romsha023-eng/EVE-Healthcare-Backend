from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.booking import Booking, BookingStatus
from app.db.models.payment import Payment, PaymentStatus
from app.db.models.webhook import WebhookEvent
from app.schemas.webhook import WebhookPayload, WebhookResponse


def process_webhook(db: Session, payload: WebhookPayload) -> WebhookResponse:
    """Process incoming payment webhook with strict idempotency, resource consistency, and amount validation guarantees."""
    # Fast path check for duplicate event_id
    existing_event = db.query(WebhookEvent).filter(WebhookEvent.event_id == payload.event_id).first()
    if existing_event:
        return WebhookResponse(
            message="Event already processed",
            event_id=payload.event_id,
            processed=False,
        )

    # Validate associated booking exists
    booking = db.query(Booking).filter(Booking.id == payload.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found for webhook event",
        )

    # Webhook Payment Amount Validation
    if payload.amount is not None and Decimal(str(payload.amount)) != Decimal(str(booking.amount)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount in webhook does not match booking amount",
        )

    # Validate payment_id / booking_id resource consistency
    if payload.payment_id:
        existing_txn = (
            db.query(Payment)
            .filter(Payment.provider_transaction_id == payload.payment_id)
            .first()
        )
        if existing_txn and existing_txn.booking_id != booking.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment ID is associated with a different booking",
            )

    event_type = f"payment.{payload.status.value.lower()}"
    webhook_event = WebhookEvent(
        event_id=payload.event_id,
        event_type=event_type,
        payload=payload.model_dump_json(),
    )

    try:
        db.add(webhook_event)

        # Check if a successful payment already exists for this booking
        existing_success_payment = (
            db.query(Payment)
            .filter(Payment.booking_id == booking.id, Payment.status == PaymentStatus.SUCCESS)
            .first()
        )

        # Non-PENDING or already paid bookings: record event idempotently without creating duplicate payment or changing state
        if booking.status == BookingStatus.CONFIRMED or existing_success_payment:
            db.commit()
            return WebhookResponse(
                message="Booking is already confirmed/paid",
                event_id=payload.event_id,
                processed=False,
            )

        if booking.status == BookingStatus.CANCELLED:
            db.commit()
            return WebhookResponse(
                message="Booking is cancelled. Webhook logged without state modification.",
                event_id=payload.event_id,
                processed=False,
            )

        if booking.status == BookingStatus.FAILED:
            db.commit()
            return WebhookResponse(
                message="Booking is in FAILED state. Webhook logged without state modification.",
                event_id=payload.event_id,
                processed=False,
            )

        # Apply state changes ONLY for PENDING booking
        provider_txn = payload.payment_id or f"wh_{payload.event_id}"
        payment = Payment(
            booking_id=booking.id,
            amount=payload.amount if payload.amount is not None else booking.amount,
            status=payload.status,
            provider_transaction_id=provider_txn,
        )
        db.add(payment)

        # Update booking status
        if payload.status == PaymentStatus.SUCCESS:
            booking.status = BookingStatus.CONFIRMED
        elif payload.status == PaymentStatus.FAILED:
            booking.status = BookingStatus.FAILED

        db.commit()
        return WebhookResponse(
            message="Webhook event processed successfully",
            event_id=payload.event_id,
            processed=True,
        )
    except IntegrityError:
        db.rollback()
        return WebhookResponse(
            message="Event already processed",
            event_id=payload.event_id,
            processed=False,
        )
