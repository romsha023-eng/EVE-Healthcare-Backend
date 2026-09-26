from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import require_admin
from app.db.database import get_db
from app.db.models.centre import DiagnosticCentre
from app.db.models.test import DiagnosticTest
from app.db.models.user import User
from app.schemas.centre import CentreCreate, CentreDetailResponse, CentreResponse

router = APIRouter(prefix="/centres", tags=["Diagnostic Centres"])


@router.post(
    "/",
    response_model=CentreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Diagnostic Centre",
    description="Create a new diagnostic centre. ADMIN privileges required.",
)
def create_centre(
    centre_in: CentreCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    centre = DiagnosticCentre(
        name=centre_in.name,
        location=centre_in.location,
    )
    db.add(centre)
    db.commit()
    db.refresh(centre)
    return centre


@router.get(
    "/",
    response_model=List[CentreResponse],
    status_code=status.HTTP_200_OK,
    summary="List Diagnostic Centres",
    description="Retrieve all diagnostic centres.",
)
def list_centres(db: Session = Depends(get_db)):
    return db.query(DiagnosticCentre).order_by(DiagnosticCentre.name).all()


@router.get(
    "/{centre_id}",
    response_model=CentreDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Diagnostic Centre Details",
    description="Retrieve diagnostic centre details including its available tests.",
)
def get_centre(centre_id: int, db: Session = Depends(get_db)):
    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == centre_id).first()
    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )
    return centre


@router.post(
    "/{centre_id}/tests/{test_id}",
    response_model=CentreDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign Test to Diagnostic Centre",
    description="Associate a diagnostic test with a diagnostic centre. ADMIN privileges required.",
)
def assign_test_to_centre(
    centre_id: int,
    test_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == centre_id).first()
    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )

    test = db.query(DiagnosticTest).filter(DiagnosticTest.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test not found",
        )

    if test not in centre.tests:
        centre.tests.append(test)
        db.commit()
        db.refresh(centre)

    return centre


@router.delete(
    "/{centre_id}/tests/{test_id}",
    response_model=CentreDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove Test from Diagnostic Centre",
    description="Remove association between a diagnostic test and centre. ADMIN privileges required.",
)
def remove_test_from_centre(
    centre_id: int,
    test_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == centre_id).first()
    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )

    test = db.query(DiagnosticTest).filter(DiagnosticTest.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test not found",
        )

    if test in centre.tests:
        centre.tests.remove(test)
        db.commit()
        db.refresh(centre)

    return centre
