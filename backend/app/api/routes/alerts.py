"""Read and acknowledge endpoints for alerts."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.db.models import Alert
from app.schemas.alert import AlertOut

router = APIRouter()


@router.get("", response_model=list[AlertOut])
def list_alerts(limit: int = Query(default=50, le=200), session: Session = Depends(get_session)):
    stmt = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
    return session.scalars(stmt).all()
