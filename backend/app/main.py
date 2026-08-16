"""FastAPI entrypoint. Run with: uvicorn app.main:app --reload"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import alerts, health, indicators, scores
from app.config import settings
from app.jobs.scheduler import shutdown_scheduler, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(title="MARS API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["indicators"])
app.include_router(scores.router, prefix="/api/scores", tags=["scores"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])


@app.get("/")
def root() -> dict:
    return {"app": settings.app_name, "env": settings.environment}
