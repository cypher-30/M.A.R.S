"""Fill the database with plausible demo data so you can see the whole system
work before a single API key exists.

The numbers are synthetic and deterministic (fixed seed) — they are shaped like
Kenyan macro data, but they are not Kenyan macro data. Never leave seeded rows
in a database you're making decisions from:

    python -m app.tools.seed_demo --clear

Everything it writes goes through the same upsert path the real jobs use, so
this doubles as a test of the persistence layer.
"""
import argparse
import json
import math
import random
from datetime import date, timedelta

from sqlalchemy import delete

from app.config import settings
from app.db import repository as repo
from app.db.models import Alert, BankReport, MacroIndicator, PriceBar, SectorScore
from app.db.session import SessionLocal
from app.ingestion.base import MacroPoint, PricePoint
from app.scoring.engine import calculate
from app.services.snapshot import build_snapshot

DAYS = 180
SEED = 20260816


def _macro_series(start: date, days: int) -> list[MacroPoint]:
    """A slow tightening cycle that eases at the end — enough movement to make
    the score cross both thresholds at least once."""
    points: list[MacroPoint] = []
    for offset in range(0, days, 30):                      # CBR moves monthly at most
        day = start + timedelta(days=offset)
        phase = offset / days
        cbr = 9.0 + 6.0 * math.sin(phase * math.pi)
        points.append(MacroPoint("CBR", day, round(cbr, 2), "demo-seed"))
    for offset in range(0, days, 30):                      # CPI monthly
        day = start + timedelta(days=offset)
        phase = offset / days
        cpi = 4.5 + 5.5 * math.sin(phase * math.pi)
        points.append(MacroPoint("CPI", day, round(cpi, 2), "demo-seed"))
    for offset in range(0, days, 7):                       # T-bill auctions weekly
        day = start + timedelta(days=offset)
        phase = offset / days
        yield_364 = 10.5 + 7.0 * math.sin(phase * math.pi)
        points.append(MacroPoint("T364", day, round(yield_364, 2), "demo-seed"))
    return points


def _price_series(start: date, days: int) -> list[PricePoint]:
    rng = random.Random(SEED)
    price = 100.0
    points: list[PricePoint] = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        if day.weekday() >= 5:                             # NSE is closed at weekends
            continue
        drift = -0.18 if 0.25 < offset / days < 0.7 else 0.14
        price = max(40.0, price * (1 + (drift + rng.uniform(-0.9, 0.9)) / 100))
        points.append(
            PricePoint(settings.etf_ticker, day, round(price, 2), rng.randint(1000, 90000), "demo-seed")
        )
    return points


def clear() -> None:
    with SessionLocal() as session:
        for model in (Alert, SectorScore, BankReport, PriceBar, MacroIndicator):
            session.execute(delete(model))
        session.commit()
    print("Cleared all rows.")


def seed(days: int = DAYS) -> None:
    today = date.today()
    start = today - timedelta(days=days)
    rng = random.Random(SEED)

    with SessionLocal() as session:
        for point in _macro_series(start, days):
            repo.upsert_macro_point(session, point)
        for point in _price_series(start, days):
            repo.upsert_price_point(session, point)

        # Two quarters of confirmed bank results, so the NPL input has the
        # minimum two banks it requires.
        for quarter_offset, period in ((150, "2025Q4"), (60, "2026Q1")):
            for ticker in settings.constituents[:4]:
                repo.upsert_bank_report(
                    session,
                    ticker=ticker,
                    period=period,
                    npl_ratio=round(rng.uniform(9.0, 17.0), 2),
                    profit_after_tax=rng.randint(2_000_000_000, 18_000_000_000),
                    loan_book=rng.randint(200_000_000_000, 900_000_000_000),
                    extraction_confidence=1.0,
                    needs_review=False,          # demo rows are pre-confirmed
                    raw_extraction="demo-seed",
                )
        session.commit()

        # Score every day so the dashboard's 90-day trend has something to draw.
        scored = 0
        for offset in range(days):
            day = start + timedelta(days=offset)
            build = build_snapshot(session, as_of=day)
            result = calculate(build.snapshot)
            repo.upsert_sector_score(
                session,
                scored_on=result.scored_on,
                score=result.score,
                signal=result.signal,
                components_json=json.dumps([c.model_dump() for c in result.components]),
            )
            scored += 1
        session.commit()

    print(f"Seeded {days} days of demo data ({scored} scores).")
    print("Start the API and dashboard to see it. Run with --clear to remove.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed or clear demo data.")
    parser.add_argument("--clear", action="store_true", help="delete all rows instead of seeding")
    parser.add_argument("--days", type=int, default=DAYS)
    args = parser.parse_args()
    if args.clear:
        clear()
    else:
        seed(args.days)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
