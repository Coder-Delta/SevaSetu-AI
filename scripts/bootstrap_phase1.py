import argparse
import sys
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.relational_db.database import SessionLocal, init_db
from data.relational_db.models.scheme import Scheme
from data.vector_db.config import get_or_create_collection
from integrations.external.scheme_source import SchemeSourceCSV
from packages.shared.config import settings


def build_scheme_document(scheme: Scheme) -> str:
    return "\n".join(
        [
            f"Scheme Name: {scheme.scheme_name}",
            f"Details: {scheme.details or ''}",
            f"Benefits: {scheme.benefits or ''}",
            f"Eligibility: {scheme.eligibility or ''}",
            f"Documents Required: {scheme.documents_required or ''}",
            f"Application Process: {scheme.application_process or ''}",
            f"Level: {scheme.level or ''}",
            f"Category: {scheme.scheme_category or ''}",
            f"Tags: {scheme.tags or ''}",
        ]
    )


def upsert_schemes(limit: int | None = None) -> int:
    source = SchemeSourceCSV(settings.SCHEMES_DATASET_PATH)
    loaded_schemes = source.load_schemes()
    if limit is not None:
        loaded_schemes = loaded_schemes[:limit]

    db = SessionLocal()
    try:
        persisted: List[Scheme] = []
        for scheme_data in loaded_schemes:
            scheme = db.query(Scheme).filter(Scheme.slug == scheme_data["slug"]).first()
            if scheme is None:
                scheme = Scheme(**scheme_data)
                db.add(scheme)
            else:
                for key, value in scheme_data.items():
                    setattr(scheme, key, value)
            persisted.append(scheme)

        db.commit()

        for scheme in persisted:
            db.refresh(scheme)

        collection = get_or_create_collection()
        collection.upsert(
            ids=[str(scheme.id) for scheme in persisted],
            documents=[build_scheme_document(scheme) for scheme in persisted],
            metadatas=[
                {
                    "scheme_name": scheme.scheme_name,
                    "slug": scheme.slug,
                    "level": scheme.level or "",
                    "scheme_category": scheme.scheme_category or "",
                }
                for scheme in persisted
            ],
        )
        return len(persisted)
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap the SevaSetu AI Phase 1 relational and vector stores."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional cap for the number of schemes to ingest during development.",
    )
    args = parser.parse_args()

    init_db()
    total = upsert_schemes(limit=args.limit)
    print(
        f"Bootstrapped {total} schemes from {settings.SCHEMES_DATASET_PATH}. "
        "ASSUMPTION: dataset source still needs verification before production use."
    )


if __name__ == "__main__":
    main()
