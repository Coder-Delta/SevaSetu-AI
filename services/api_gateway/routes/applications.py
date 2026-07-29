from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from data.relational_db.database import get_db
from data.relational_db.models.application import Application
from data.relational_db.models.scheme import Scheme
from data.relational_db.models.user import User
from packages.shared.auth import get_current_user
from packages.shared.schemas import ApplicationCreate, ApplicationResponse
from services.api_gateway.routes.common import build_user_profile_dict
from services.api_gateway.routes.schemes import serialize_scheme_for_rules
from services.orchestrator.eligibility.rule_engine import evaluate_eligibility

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Application:
    scheme = db.query(Scheme).filter(Scheme.id == payload.scheme_id).first()
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheme not found.",
        )

    eligibility = evaluate_eligibility(
        build_user_profile_dict(current_user),
        serialize_scheme_for_rules(scheme),
    )
    application = Application(
        user_id=current_user.id,
        scheme_id=scheme.id,
        status="draft",
        eligibility_score=eligibility.match_score,
        notes=eligibility.explanation,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/me", response_model=List[ApplicationResponse])
def list_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Application]:
    return (
        db.query(Application)
        .options(joinedload(Application.scheme))
        .filter(Application.user_id == current_user.id)
        .order_by(Application.created_at.desc())
        .all()
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Application:
    application = (
        db.query(Application)
        .options(joinedload(Application.scheme))
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
        .first()
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )
    return application
