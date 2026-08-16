"""All database reads and writes live here.

Two reasons this is its own layer:

  1. Jobs stay readable — they orchestrate, they don't write SQL.
  2. Every write is an *upsert*. Jobs get re-run (by you, by a retry, by a cron
     that fired twice after a restart) and a re-run must never duplicate a row
     or crash on a unique constraint.

The upserts are written with plain SELECT-then-INSERT rather than Postgres's
ON CONFLICT so the same code runs against SQLite in tests.
"""
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Alert, BankReport, MacroIndicator, PriceBar, SectorScore
from app.ingestion.base import MacroPoint, PricePoint

# --- Writes -----------------------------------------------------------------


def upsert_macro_point(session: Session, point: MacroPoint) -> MacroIndicator:
    row = session.scalars(
        select(MacroIndicator).where(
            MacroIndicator.code == point.code,
            MacroIndicator.observed_on == point.observed_on,
        )
    ).first()
    if row is None:
        row = MacroIndicator(code=point.code, observed_on=point.observed_on)
        session.add(row)
    row.value = point.value
    row.unit = point.unit
    row.source = point.source
    return row


def upsert_price_point(session: Session, point: PricePoint) -> PriceBar:
    row = session.scalars(
        select(PriceBar).where(
            PriceBar.ticker == point.ticker,
            PriceBar.traded_on == point.traded_on,
        )
    ).first()
    if row is None:
        row = PriceBar(ticker=point.ticker, traded_on=point.traded_on)
        session.add(row)
    row.close = point.close
    row.volume = point.volume
    row.source = point.source
    return row


def upsert_bank_report(
    session: Session,
    ticker: str,
    period: str,
    *,
    npl_ratio: float | None = None,
    profit_after_tax: float | None = None,
    loan_book: float | None = None,
    extraction_confidence: float | None = None,
    needs_review: bool = True,
    raw_extraction: str | None = None,
    source_url: str | None = None,
) -> BankReport:
    row = session.scalars(
        select(BankReport).where(BankReport.ticker == ticker, BankReport.period == period)
    ).first()
    if row is None:
        row = BankReport(ticker=ticker, period=period)
        session.add(row)
    row.npl_ratio = npl_ratio
    row.profit_after_tax = profit_after_tax
    row.loan_book = loan_book
    row.extraction_confidence = extraction_confidence
    row.needs_review = needs_review
    row.raw_extraction = raw_extraction
    row.source_url = source_url
    return row


def upsert_sector_score(
    session: Session, scored_on: date, score: float, signal: str, components_json: str
) -> SectorScore:
    row = session.scalars(select(SectorScore).where(SectorScore.scored_on == scored_on)).first()
    if row is None:
        row = SectorScore(scored_on=scored_on)
        session.add(row)
    row.score = score
    row.signal = signal
    row.components = components_json
    return row


def record_alert(
    session: Session,
    *,
    level: str,
    signal: str,
    headline: str,
    body: str,
    delivered: bool,
    sector_score_id: int | None = None,
) -> Alert:
    alert = Alert(
        level=level,
        signal=signal,
        headline=headline,
        body=body,
        delivered=delivered,
        sector_score_id=sector_score_id,
    )
    session.add(alert)
    return alert


# --- Reads ------------------------------------------------------------------


def latest_macro(session: Session, code: str, as_of: date) -> MacroIndicator | None:
    """Most recent reading of a series on or before as_of."""
    return session.scalars(
        select(MacroIndicator)
        .where(MacroIndicator.code == code, MacroIndicator.observed_on <= as_of)
        .order_by(MacroIndicator.observed_on.desc())
        .limit(1)
    ).first()


def price_on_or_before(session: Session, ticker: str, on: date) -> PriceBar | None:
    """The ETF doesn't trade every day — take the closest earlier close."""
    return session.scalars(
        select(PriceBar)
        .where(PriceBar.ticker == ticker, PriceBar.traded_on <= on)
        .order_by(PriceBar.traded_on.desc())
        .limit(1)
    ).first()


def confirmed_npl_ratios(session: Session, tickers: list[str], as_of: date) -> list[BankReport]:
    """Latest confirmed report per bank.

    needs_review=True rows are excluded on purpose: an unverified figure from
    the PDF parser must never reach the score.
    """
    results: list[BankReport] = []
    for ticker in tickers:
        row = session.scalars(
            select(BankReport)
            .where(
                BankReport.ticker == ticker,
                BankReport.needs_review.is_(False),
                BankReport.npl_ratio.is_not(None),
            )
            .order_by(BankReport.period.desc())
            .limit(1)
        ).first()
        if row is not None:
            results.append(row)
    return results


def previous_signal(session: Session, before: date) -> str | None:
    row = session.scalars(
        select(SectorScore)
        .where(SectorScore.scored_on < before)
        .order_by(SectorScore.scored_on.desc())
        .limit(1)
    ).first()
    return row.signal if row else None


def last_alert_date(session: Session) -> date | None:
    row = session.scalars(select(Alert).order_by(Alert.created_at.desc()).limit(1)).first()
    return row.created_at.date() if row and row.created_at else None


def is_stale(observed_on: date, as_of: date, max_days: int) -> bool:
    return observed_on < as_of - timedelta(days=max_days)
