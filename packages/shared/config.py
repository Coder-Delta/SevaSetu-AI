from json import JSONDecodeError, loads
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    APP_NAME: str = "SevaSetu AI"
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-before-production"
    JWT_SECRET_KEY: str = "change-me-before-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database  
    DATABASE_URL: str = "sqlite:///./data/relational_db/sevasetu.db"
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./data/vector_db/chroma_store"
    CHROMA_COLLECTION_NAME: str = "scheme_embeddings"

    # Groq
    GROQ_API_KEY: str = ""
    GROQ_MODEL_NAME: str = "openai/gpt-oss-120b"

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Data bootstrap
    SCHEMES_DATASET_PATH: str = "./data/fixtures/schemes_dataset.csv"
    MOCK_DATA_MODE: bool = True

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "citizen-documents"
    MINIO_SECURE: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, list):
            return value
        if not value:
            return []
        try:
            parsed = loads(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except JSONDecodeError:
            pass
        return [item.strip() for item in value.split(",") if item.strip()]

settings = Settings()
