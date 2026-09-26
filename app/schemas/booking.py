from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.db.models.booking import BookingStatus
from app.schemas.auth import UserResponse
from app.schemas.centre import CentreResponse
from app.schemas.test import TestResponse


class BookingCreate(BaseModel):
    test_id: int = Field(..., gt=0, examples=[1])
    centre_id: int = Field(..., gt=0, examples=[1])
    appointment_datetime: datetime = Field(..., examples=["2026-10-15T10:00:00Z"])


class BookingResponse(BaseModel):
    id: int
    user_id: int
    test_id: int
    centre_id: int
    appointment_datetime: datetime
    amount: Decimal
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookingDetailResponse(BookingResponse):
    user: Optional[UserResponse] = None
    test: Optional[TestResponse] = None
    centre: Optional[CentreResponse] = None

    model_config = ConfigDict(from_attributes=True)
