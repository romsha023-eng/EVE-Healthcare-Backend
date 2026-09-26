from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TestCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Complete Blood Count (CBC)"])
    description: Optional[str] = Field(None, examples=["Evaluates overall health and detects a wide range of disorders."])
    price: Decimal = Field(..., gt=0, decimal_places=2, examples=[50.00])


class TestUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)


class TestResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
