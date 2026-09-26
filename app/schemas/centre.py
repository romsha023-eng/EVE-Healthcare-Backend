from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.test import TestResponse


class CentreCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Apollo Diagnostics - Downtown"])
    location: str = Field(..., min_length=1, max_length=255, examples=["123 Healthcare Ave, Cityville"])


class CentreUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, min_length=1, max_length=255)


class CentreResponse(BaseModel):
    id: int
    name: str
    location: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CentreDetailResponse(CentreResponse):
    tests: List[TestResponse] = []

    model_config = ConfigDict(from_attributes=True)
