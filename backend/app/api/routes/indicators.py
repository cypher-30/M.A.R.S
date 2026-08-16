"""Read endpoints for the indicators feeding the score."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.db.models import MacroIndicator, PriceBar
from app.schemas.indicators import MacroIndicatorOut, PriceBarOut

router = APIRouter()


@router.get("/macro", response_model=list[MacroIndicatorOut])
def list_macro(
    code: str | None = Query(default=None, description="CBR, CPI, T364, BOND_10Y"),
    limit: int = Query(default=90, le=500),
    session: Session = Depends(get_session),
):
    stmt = select(MacroIndicator).order_by(MacroIndicator.observed_on.desc()).limit(limit)
    if code:
        stmt = stmt.where(MacroIndicator.code == code.upper())
    return session.scalars(stmt).all()


@router.get("/prices/{ticker}", response_model=list[PriceBarOut])
def list_prices(
    ticker: str,
    limit: int = Query(default=90, le=500),
    session: Session = Depends(get_session),
):
    stmt = (
        select(PriceBar)
        .where(PriceBar.ticker == ticker.upper())
        .order_by(PriceBar.traded_on.desc())
        .limit(limit)
    )
    return session.scalars(stmt).all()
