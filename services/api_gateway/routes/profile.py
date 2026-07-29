from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from data.relational_db.database import get_db
from data.relational_db.models.user import User
from packages.shared.auth import get_current_user
from packages.shared.schemas import UserProfile, UserProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=UserProfile)
def get_my_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserProfile)
def update_my_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field_name, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
