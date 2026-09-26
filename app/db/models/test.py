from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.models.centre import centre_tests


class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    centres = relationship(
        "DiagnosticCentre",
        secondary=centre_tests,
        back_populates="tests"
    )
    bookings = relationship("Booking", back_populates="test", cascade="all, delete-orphan")
