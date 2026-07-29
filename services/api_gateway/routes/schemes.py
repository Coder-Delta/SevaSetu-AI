from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from data.relational_db.database import get_db
from data.relational_db.models.scheme import Scheme
from data.relational_db.models.user import User
from packages.shared.auth import get_current_user
from packages.shared.schemas import SchemeResponse, SchemeSearchResult
from services.api_gateway.routes.common import build_user_profile_dict
from services.orchestrator.eligibility.rule_engine import evaluate_eligibility

router = APIRouter(prefix="/schemes", tags=["schemes"])


class SchemeSearchPayload(BaseModel):
    query: str
    language: str = "en"
    top_k: int = 5
    user_profile: Optional[Dict[str, Any]] = None


def serialize_scheme_for_rules(scheme: Scheme) -> Dict[str, Any]:
    return {
        "id": str(scheme.id),
        "scheme_name": scheme.scheme_name,
        "eligibility": scheme.eligibility,
        "level": scheme.level,
        "scheme_category": scheme.scheme_category,
        "details": scheme.details,
        "benefits": scheme.benefits,
        "application_process": scheme.application_process,
        "documents_required": scheme.documents_required,
        "tags": scheme.tags,
    }


@router.get("/", response_model=List[SchemeResponse])
def list_schemes(
    q: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> List[Scheme]:
    query = db.query(Scheme).filter(Scheme.is_active.is_(True))
    if q:
        like_term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Scheme.scheme_name.ilike(like_term),
                Scheme.details.ilike(like_term),
                Scheme.tags.ilike(like_term),
            )
        )
    return query.order_by(Scheme.created_at.desc()).offset(offset).limit(limit).all()


@router.post("/search", response_model=List[SchemeSearchResult])
def search_for_schemes(
    payload: SchemeSearchPayload,
    current_user: User = Depends(get_current_user),
) -> List[SchemeSearchResult]:
    from services.orchestrator.rag.retriever import search_schemes

    results = search_schemes(payload.query, top_k=payload.top_k)
    profile = payload.user_profile or build_user_profile_dict(current_user)

    response_items: List[SchemeSearchResult] = []
    for item in results:
        scheme = item["scheme"]
        eligibility_explanation = None
        if any(value is not None for value in profile.values()):
            eligibility_result = evaluate_eligibility(profile, serialize_scheme_for_rules(scheme))
            eligibility_explanation = eligibility_result.explanation

        response_items.append(
            SchemeSearchResult(
                scheme=scheme,
                relevance_score=item["relevance_score"],
                eligibility_explanation=eligibility_explanation,
            )
        )

    return response_items
