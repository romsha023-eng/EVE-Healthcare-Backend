from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import require_admin
from app.db.database import get_db
from app.db.models.test import DiagnosticTest
from app.db.models.user import User
from app.schemas.test import TestCreate, TestResponse

router = APIRouter(prefix="/tests", tags=["Diagnostic Tests"])


@router.post(
    "/",
    response_model=TestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Diagnostic Test",
    description="Create a new diagnostic test. ADMIN privileges required.",
)
def create_test(
    test_in: TestCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    test = DiagnosticTest(
        name=test_in.name,
        description=test_in.description,
        price=test_in.price,
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


@router.get(
    "/",
    response_model=List[TestResponse],
    status_code=status.HTTP_200_OK,
    summary="List Diagnostic Tests",
    description="Retrieve all available diagnostic tests.",
)
def list_tests(db: Session = Depends(get_db)):
    return db.query(DiagnosticTest).order_by(DiagnosticTest.name).all()


@router.get(
    "/{test_id}",
    response_model=TestResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Diagnostic Test Details",
    description="Retrieve details for a specific diagnostic test.",
)
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(DiagnosticTest).filter(DiagnosticTest.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test not found",
        )
    return test
