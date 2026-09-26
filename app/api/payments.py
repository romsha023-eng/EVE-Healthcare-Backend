from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.schemas.webhook import WebhookPayload, WebhookResponse
from app.services.payment_service import process_payment
from app.services.webhook_service import process_webhook

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Simulate Payment",
    description="Process a simulated payment for a booking. Validates booking ID, amount match, and state transitions.",
)
def create_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return process_payment(db, payment_in, current_user)


@router.post(
    "/webhook/",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Payment Provider Webhook",
    description="Idempotent webhook endpoint to receive simulated payment gateway events.",
)
def payment_webhook(
    payload: WebhookPayload,
    db: Session = Depends(get_db),
):
    return process_webhook(db, payload)
