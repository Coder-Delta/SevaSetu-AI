import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data.relational_db.database import init_db
from packages.shared.config import settings
from services.api_gateway.routes import admin, applications, auth, chat, profile, schemes

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description=(
        "Phase 1 backend scaffold for SevaSetu AI. "
        "ASSUMPTION: the local CSV dataset is a working development source pending verification."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(schemes.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def read_root() -> dict[str, object]:
    return {
        "name": settings.APP_NAME,
        "phase": "Phase 1 scaffolded, pending verified scheme source",
        "languages": ["en", "hi", "bn"],
        "mock_data_mode": settings.MOCK_DATA_MODE,
    }


@app.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
