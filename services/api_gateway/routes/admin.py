from collections import Counter
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from data.relational_db.database import get_db
from data.relational_db.models.application import Application
from data.relational_db.models.scheme import Scheme
from data.relational_db.models.user import User
from packages.shared.auth import require_admin
from packages.shared.schemas import ApplicationResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/applications", response_model=List[ApplicationResponse])
def list_applications_for_admin(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> List[Application]:
    query = db.query(Application).options(joinedload(Application.scheme))
    if status:
        query = query.filter(Application.status == status)
    return query.order_by(Application.created_at.desc()).all()


@router.get("/summary", response_model=Dict[str, object])
def get_admin_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Dict[str, object]:
    applications = db.query(Application).all()
    status_counts = Counter(application.status for application in applications)

    return {
        "total_users": db.query(User).count(),
        "total_schemes": db.query(Scheme).count(),
        "total_applications": len(applications),
        "application_status_counts": dict(status_counts),
    }
