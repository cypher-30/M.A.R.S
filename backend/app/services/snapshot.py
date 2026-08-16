"""Build the day's IndicatorSnapshot from what's in the database.

This is where MAX_STALENESS_DAYS finally does something. An old reading is
worse than no reading, because it looks current on a dashboard. Anything past
its limit is dropped to None, the scoring engine marks that component neutral,
and the dashboard says "no fresh data" instead of quietly showing a number from
four months ago.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.db import repository as repo
from app.schemas.indicators import IndicatorSnapshot
from app.scoring.weights import MAX_STALENESS_DAYS

MOMENTUM_WINDOW_DAYS = 30


@dataclass
class SnapshotBuild:
    snapshot: IndicatorSnapshot
    dropped_as_stale: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)


def _macro_value(session: Session, code: str, as_of: date, build: SnapshotBuild) -> float | None:
    row = repo.latest_macro(session, code, as_of)
    if row is None:
        build.missing.append(code)
        return None
    limit = MAX_STALENESS_DAYS.get(code, 90)
    if repo.is_stale(row.observed_on, as_of, limit):
        build.dropped_as_stale.append(f"{code} (last seen {row.observed_on})")
        return None
    return row.value


def build_snapshot(session: Session, as_of: date | None = None) -> SnapshotBuild:
    as_of = as_of or date.today()
    build = SnapshotBuild(snapshot=IndicatorSnapshot(as_of=as_of))

    cbr = _macro_value(session, "CBR", as_of, build)
    cpi = _macro_value(session, "CPI", as_of, build)
    yield_364 = _macro_value(session, "T364", as_of, build)

    # Bad loans: average the latest confirmed figure across the constituents we
    # actually have. One bank's number is not the sector; require at least two.
    reports = repo.confirmed_npl_ratios(session, settings.constituents, as_of)
    ratios = [r.npl_ratio for r in reports if r.npl_ratio is not None]
    if len(ratios) < 2:
        avg_npl = None
        build.missing.append("NPL (fewer than two confirmed bank reports)")
    else:
        avg_npl = round(sum(ratios) / len(ratios), 2)

    latest_price = repo.price_on_or_before(session, settings.etf_ticker, as_of)
    if latest_price is None:
        build.missing.append("ETF price")
        price_now = price_then = None
    else:
        price_limit = MAX_STALENESS_DAYS.get("MOMENTUM", 7)
        if repo.is_stale(latest_price.traded_on, as_of, price_limit):
            build.dropped_as_stale.append(f"ETF price (last traded {latest_price.traded_on})")
            price_now = price_then = None
        else:
            price_now = latest_price.close
            earlier = repo.price_on_or_before(
                session, settings.etf_ticker, as_of - timedelta(days=MOMENTUM_WINDOW_DAYS)
            )
            price_then = earlier.close if earlier else None
            if earlier is None:
                build.missing.append("ETF price 30 days ago")

    build.snapshot = IndicatorSnapshot(
        cbr=cbr,
        cpi=cpi,
        t364_yield=yield_364,
        avg_npl_ratio=avg_npl,
        etf_price=price_now,
        etf_price_30d_ago=price_then,
        as_of=as_of,
    )
    return build
