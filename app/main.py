from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.lessons import router as lessons_router
from app.routers.matches import router as matches_router
from app.routers.challenges import router as challenges_router
from app.routers.leaderboard import leaderboard_router, reviews_router

# ─── Create tables on startup (use Alembic in production) ───────────────────
# Import models so Base knows about them
import app.models.user  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Edutrack API",
    description="Backend for Edutrack — skill exchange platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(lessons_router)
app.include_router(matches_router)
app.include_router(challenges_router)
app.include_router(leaderboard_router)
app.include_router(reviews_router)


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok", "service": "edutrack-api"}


STATIC_DIR = Path(__file__).parent.parent / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend(full_path: str = ""):
        if full_path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404)
        index = STATIC_DIR / "index.html"
        return FileResponse(index)
