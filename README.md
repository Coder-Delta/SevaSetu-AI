# SevaSetu AI

A civic welfare discovery and guidance platform that helps citizens find, understand, and apply for government schemes using AI-powered assistance.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                │
│                    apps/web/                              │
└──────────────────────────┬───────────────────────────────┘
                           │ HTTP / REST API
┌──────────────────────────▼───────────────────────────────┐
│                 API Gateway (FastAPI)                     │
│                 services/api_gateway/                     │
│  ┌────────┬────────┬────────┬────────┬────────┬────────┐ │
│  │  Auth  │Profile │Schemes │  Chat  │  Apps  │ Admin  │ │
│  │ routes │ routes │ routes │ routes │ routes │ routes │ │
│  └────────┴────────┴────────┴────────┴────────┴────────┘ │
└──────────────────────────┬───────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐ ┌──────────────┐ ┌──────────────────┐
│ PostgreSQL /  │ │   ChromaDB   │ │  MinIO (Object   │
│   SQLite      │ │  (Vector DB) │ │    Storage)      │
└───────────────┘ └──────────────┘ └──────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│               Orchestrator Service                        │
│               services/orchestrator/                      │
│  ┌──────────────────────┐  ┌───────────────────────────┐ │
│  │   Rule Engine        │  │  RAG Pipeline             │ │
│  │   (Eligibility)      │  │  (Scheme Retrieval + LLM) │ │
│  └──────────────────────┘  └───────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

## Features

- **User Authentication** — Register and login with JWT-based auth
- **Profile Management** — Capture citizen demographics (age, income, category, location, etc.)
- **Scheme Discovery** — Semantic search over government schemes using vector embeddings
- **Eligibility Checking** — Rule-based eligibility evaluation against citizen profiles
- **AI Chat Assistant** — RAG-powered conversational guidance using Groq LLM
- **Application Tracking** — Draft and track scheme applications
- **Multi-language Support** — English, Hindi, and Bengali

## Tech Stack

| Component     | Technology                          |
|---------------|-------------------------------------|
| Frontend      | React, TypeScript, Vite             |
| API Gateway   | FastAPI, Python                     |
| Database      | SQLite (dev) / PostgreSQL (prod)    |
| Vector DB     | ChromaDB + sentence-transformers    |
| LLM           | Groq (llama-3.3-70b-specdec)        |
| Object Store  | MinIO                               |
| Auth          | JWT (python-jose) + bcrypt          |
| Embeddings    | all-MiniLM-L6-v2 (HuggingFace)      |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional, for PostgreSQL + MinIO)

### Backend Setup

```bash
# Clone the repository
git clone <repo-url>
cd IBM-Project

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (Groq API key, etc.)

# Run the API server
uvicorn services.api_gateway.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup

```bash
cd apps/web
npm install
npm run dev
```

The frontend will be available at `http://127.0.0.1:5173`.

### Database & Infrastructure (Optional)

```bash
docker compose up -d
```

This starts PostgreSQL and MinIO containers. The app uses SQLite by default for local development.

## API Endpoints

### Authentication

| Method | Endpoint                | Description       |
|--------|-------------------------|-------------------|
| POST   | `/api/v1/auth/register` | Create an account |
| POST   | `/api/v1/auth/login`    | Sign in           |

### Profile

| Method | Endpoint               | Description        |
|--------|------------------------|--------------------|
| GET    | `/api/v1/profile/me`   | Get user profile   |
| PATCH  | `/api/v1/profile/me`   | Update profile     |

### Schemes

| Method | Endpoint                  | Description         |
|--------|---------------------------|---------------------|
| POST   | `/api/v1/schemes/search`  | Semantic search     |

### Chat

| Method | Endpoint           | Description           |
|--------|--------------------|-----------------------|
| POST   | `/api/v1/chat/`    | AI assistant message  |

### Applications

| Method | Endpoint                    | Description               |
|--------|-----------------------------|---------------------------|
| POST   | `/api/v1/applications/`     | Create application draft  |
| GET    | `/api/v1/applications/me`   | List user's applications  |

## Environment Variables

Key configuration in `.env`:

| Variable                          | Default            | Description                  |
|-----------------------------------|--------------------|------------------------------|
| `APP_NAME`                        | SevaSetu AI        | Application name             |
| `JWT_SECRET_KEY`                  | (change me)        | JWT signing secret           |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 30                 | Token expiry                 |
| `DATABASE_URL`                    | SQLite path        | Database connection string   |
| `GROQ_API_KEY`                    | (set yours)        | Groq LLM API key             |
| `CORS_ORIGINS`                    | JSON array of URLs | Allowed CORS origins         |

## Project Structure

```
IBM-Project/
├── apps/web/                 # React frontend
├── data/
│   ├── fixtures/             # Dataset CSV files
│   ├── relational_db/        # SQLAlchemy models + DB
│   ├── vector_db/            # ChromaDB config
│   └── object_storage/       # MinIO config
├── integrations/external/    # External service integrations
├── packages/shared/          # Shared code (auth, config, schemas)
├── scripts/                  # Bootstrap and utility scripts
├── services/
│   ├── api_gateway/          # FastAPI routes
│   └── orchestrator/         # Rule engine + RAG pipeline
└── tests/                    # Test suite
```

## License

Proprietary — Internal project