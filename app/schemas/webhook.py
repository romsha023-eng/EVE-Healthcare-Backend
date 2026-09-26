from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

from app.db.models.payment import PaymentStatus


class WebhookPayload(BaseModel):
    event_id: str = Field(..., min_length=1, max_length=255, examples=["evt_123"])
    payment_id: Optional[str] = Field(None, examples=["pay_123"])
    booking_id: int = Field(..., gt=0, examples=[1])
    status: PaymentStatus = Field(..., examples=[PaymentStatus.SUCCESS])
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2, examples=[50.00])


class WebhookResponse(BaseModel):
    message: str = Field(..., examples=["Webhook event processed successfully"])
    event_id: str = Field(..., examples=["evt_123"])
    processed: bool = Field(..., examples=[True])
