import enum
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class PaymentStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, index=True)
    provider_transaction_id = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    booking = relationship("Booking", back_populates="payments")

    __table_args__ = (
        Index(
            "uq_payment_booking_success",
            "booking_id",
            unique=True,
            postgresql_where=(status == PaymentStatus.SUCCESS),
            sqlite_where=(status == PaymentStatus.SUCCESS),
        ),
    )
