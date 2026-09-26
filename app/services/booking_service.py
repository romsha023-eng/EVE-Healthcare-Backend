from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.booking import Booking, BookingStatus
from app.db.models.centre import DiagnosticCentre
from app.db.models.test import DiagnosticTest
from app.db.models.user import User, UserRole
from app.schemas.booking import BookingCreate


def create_booking(db: Session, current_user: User, booking_in: BookingCreate) -> Booking:
    """Create a new diagnostic test booking."""
    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == booking_in.centre_id).first()
    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )

    test = db.query(DiagnosticTest).filter(DiagnosticTest.id == booking_in.test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test not found",
        )

    # Check if test is offered at the centre
    if test not in centre.tests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected diagnostic test is not available at this diagnostic centre",
        )

    # Validate appointment datetime (must be in future)
    appt_dt = booking_in.appointment_datetime
    if appt_dt.tzinfo is None:
        appt_dt = appt_dt.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    if appt_dt <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment datetime must be in the future",
        )

    booking = Booking(
        user_id=current_user.id,
        test_id=test.id,
        centre_id=centre.id,
        appointment_datetime=appt_dt,
        amount=test.price,
        status=BookingStatus.PENDING,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def get_booking_by_id(db: Session, booking_id: int, current_user: User) -> Booking:
    """Get booking by ID with ownership/permission checks."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if current_user.role != UserRole.ADMIN and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access another user's booking",
        )

    return booking


def list_bookings(db: Session, current_user: User) -> List[Booking]:
    """List bookings based on user permissions (admin views all, normal user views own)."""
    if current_user.role == UserRole.ADMIN:
        return db.query(Booking).order_by(Booking.created_at.desc()).all()
    return (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )


def cancel_booking(db: Session, booking_id: int, current_user: User) -> Booking:
    """Cancel a booking if permitted and in a valid state."""
    booking = get_booking_by_id(db, booking_id, current_user)

    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled",
        )

    if booking.status in (BookingStatus.CONFIRMED, BookingStatus.FAILED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a booking with status '{booking.status.value}'",
        )

    booking.status = BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    return booking
