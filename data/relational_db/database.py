from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from packages.shared.config import settings
from .models.base import Base

engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import all models to ensure they are registered on Base
    from .models import user, scheme, application, conversation
    Base.metadata.create_all(bind=engine)
