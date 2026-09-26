from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.booking import BookingCreate, BookingDetailResponse, BookingResponse
from app.services.booking_service import (
    cancel_booking,
    create_booking,
    get_booking_by_id,
    list_bookings,
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Diagnostic Test Booking",
    description="Book a diagnostic test at a specific centre for a given appointment datetime. Must be authenticated.",
)
def create_new_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_booking(db, current_user, booking_in)


@router.get(
    "/",
    response_model=List[BookingResponse],
    status_code=status.HTTP_200_OK,
    summary="List Bookings",
    description="Retrieve bookings. Normal users receive their own bookings; ADMIN users receive all bookings.",
)
def get_all_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_bookings(db, current_user)


@router.get(
    "/{booking_id}",
    response_model=BookingDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Booking Details",
    description="Retrieve details for a specific booking. Users may only access their own bookings unless ADMIN.",
)
def get_single_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_booking_by_id(db, booking_id, current_user)


@router.patch(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel Booking",
    description="Cancel a PENDING booking. Confirmed or already cancelled bookings cannot be cancelled.",
)
def cancel_existing_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cancel_booking(db, booking_id, current_user)
