from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.db.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    booking_id: int = Field(..., gt=0, examples=[1])
    amount: Decimal = Field(..., gt=0, decimal_places=2, examples=[50.00])
    status: Optional[PaymentStatus] = Field(default=PaymentStatus.SUCCESS, examples=[PaymentStatus.SUCCESS])
    provider_transaction_id: Optional[str] = Field(None, examples=["txn_sim_12345"])


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    status: PaymentStatus
    provider_transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
