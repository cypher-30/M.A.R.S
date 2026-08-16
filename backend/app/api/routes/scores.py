"""Read endpoints for the Sector Health Score."""
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.db.models import SectorScore
from app.schemas.score import SectorScoreOut

router = APIRouter()


def _to_out(row: SectorScore) -> SectorScoreOut:
    return SectorScoreOut(
        scored_on=row.scored_on,
        score=row.score,
        signal=row.signal,
        components=json.loads(row.components or "[]"),
    )


@router.get("/latest", response_model=SectorScoreOut)
def latest(session: Session = Depends(get_session)):
    row = session.scalars(
        select(SectorScore).order_by(SectorScore.scored_on.desc()).limit(1)
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail="No score has been calculated yet.")
    return _to_out(row)


@router.get("/history", response_model=list[SectorScoreOut])
def history(limit: int = Query(default=90, le=365), session: Session = Depends(get_session)):
    rows = session.scalars(
        select(SectorScore).order_by(SectorScore.scored_on.desc()).limit(limit)
    ).all()
    return [_to_out(r) for r in rows]
