from typing import Any, Dict

from data.relational_db.models.user import User


def build_user_profile_dict(user: User) -> Dict[str, Any]:
    return {
        "age": user.age,
        "income_bracket": user.income_bracket,
        "category": user.category,
        "occupation": user.occupation,
        "location_state": user.location_state,
        "location_district": user.location_district,
        "education_level": user.education_level,
    }
