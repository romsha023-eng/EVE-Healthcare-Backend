import uuid
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.booking import Booking, BookingStatus
from app.db.models.payment import Payment, PaymentStatus
from app.db.models.user import User, UserRole
from app.schemas.payment import PaymentCreate


def process_payment(
    db: Session,
    payment_in: PaymentCreate,
    current_user: User
) -> Payment:
    """Process simulated payment transactionally with state machine & permission enforcement."""
    # Fetch booking
    booking = db.query(Booking).filter(Booking.id == payment_in.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    # Authorization Check: User must own the booking or be ADMIN
    if current_user.role != UserRole.ADMIN and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to process payment for another user's booking",
        )

    # State Machine Rule: Payments can only be processed when booking is PENDING
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot process payment for a booking with status '{booking.status.value}'",
        )

    # Check for existing successful payment for this booking
    existing_success_payment = (
        db.query(Payment)
        .filter(Payment.booking_id == booking.id, Payment.status == PaymentStatus.SUCCESS)
        .first()
    )
    if existing_success_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Successful payment already processed for this booking",
        )

    # Verify payment amount matches booking amount
    if Decimal(str(payment_in.amount)) != Decimal(str(booking.amount)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount ({payment_in.amount}) does not match booking amount ({booking.amount})",
        )

    pay_status = payment_in.status or PaymentStatus.SUCCESS
    provider_txn_id = payment_in.provider_transaction_id or f"txn_sim_{uuid.uuid4().hex[:12]}"

    payment = Payment(
        booking_id=booking.id,
        amount=payment_in.amount,
        status=pay_status,
        provider_transaction_id=provider_txn_id,
    )

    # Update booking status transactionally
    if pay_status == PaymentStatus.SUCCESS:
        booking.status = BookingStatus.CONFIRMED
    else:
        booking.status = BookingStatus.FAILED

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
