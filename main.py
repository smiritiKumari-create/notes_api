"""
Notes API — FastAPI + MySQL + SQLAlchemy
----------------------------------------
Run locally:
    uvicorn main:app --reload

Interactive docs:
    http://127.0.0.1:8000/docs   (Swagger UI)
    http://127.0.0.1:8000/redoc  (ReDoc)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers  import notes_router, tags_router


# ── Create all tables on startup ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Notes API",
    description=(
        "A REST API for creating, tagging, and searching Markdown notes.\n\n"
        "**Features**\n"
        "- Full Markdown support with server-side HTML rendering\n"
        "- Many-to-many Note ↔ Tag relationships\n"
        "- MySQL FULLTEXT search across title and body\n"
        "- Paginated listing with multi-tag and pinned filters\n"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS (adjust origins for production) ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # lock this down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(notes_router, prefix="/api/v1")
app.include_router(tags_router,  prefix="/api/v1")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}