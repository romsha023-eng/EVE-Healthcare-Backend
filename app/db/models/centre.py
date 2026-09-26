from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.database import Base

centre_tests = Table(
    "centre_tests",
    Base.metadata,
    Column("centre_id", Integer, ForeignKey("diagnostic_centres.id", ondelete="CASCADE"), primary_key=True),
    Column("test_id", Integer, ForeignKey("diagnostic_tests.id", ondelete="CASCADE"), primary_key=True),
)


class DiagnosticCentre(Base):
    __tablename__ = "diagnostic_centres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    tests = relationship(
        "DiagnosticTest",
        secondary=centre_tests,
        back_populates="centres"
    )
    bookings = relationship("Booking", back_populates="centre", cascade="all, delete-orphan")
