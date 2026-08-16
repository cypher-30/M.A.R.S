"""The upserts must be safe to run twice — jobs get re-run all the time."""
from datetime import date

from sqlalchemy import func, select

from app.db import repository as repo
from app.db.models import MacroIndicator, PriceBar
from app.ingestion.base import MacroPoint, PricePoint


def test_macro_upsert_is_idempotent(session):
    point = MacroPoint("CBR", date(2026, 6, 1), 10.5, "test")
    repo.upsert_macro_point(session, point)
    repo.upsert_macro_point(session, point)
    session.commit()
    assert session.scalar(select(func.count()).select_from(MacroIndicator)) == 1


def test_macro_upsert_updates_a_revised_figure(session):
    repo.upsert_macro_point(session, MacroPoint("CPI", date(2026, 6, 1), 6.0, "test"))
    repo.upsert_macro_point(session, MacroPoint("CPI", date(2026, 6, 1), 6.4, "test-revised"))
    session.commit()
    row = session.scalars(select(MacroIndicator)).one()
    assert row.value == 6.4
    assert row.source == "test-revised"


def test_price_upsert_is_idempotent(session):
    bar = PricePoint("WSA", date(2026, 6, 1), 101.5, 5000)
    repo.upsert_price_point(session, bar)
    repo.upsert_price_point(session, bar)
    session.commit()
    assert session.scalar(select(func.count()).select_from(PriceBar)) == 1


def test_price_on_or_before_skips_non_trading_days(session):
    repo.upsert_price_point(session, PricePoint("WSA", date(2026, 6, 5), 100.0))
    session.commit()
    # 6 and 7 June 2026 are a weekend; asking for the 7th gives Friday's close.
    bar = repo.price_on_or_before(session, "WSA", date(2026, 6, 7))
    assert bar is not None and bar.traded_on == date(2026, 6, 5)


def test_unconfirmed_reports_are_excluded(session):
    repo.upsert_bank_report(session, "KCB", "2026Q1", npl_ratio=12.0, needs_review=True)
    repo.upsert_bank_report(session, "EQTY", "2026Q1", npl_ratio=11.0, needs_review=False)
    session.commit()
    confirmed = repo.confirmed_npl_ratios(session, ["KCB", "EQTY"], date(2026, 6, 1))
    assert [r.ticker for r in confirmed] == ["EQTY"]


def test_staleness_check():
    assert repo.is_stale(date(2026, 1, 1), date(2026, 6, 1), max_days=30) is True
    assert repo.is_stale(date(2026, 5, 25), date(2026, 6, 1), max_days=30) is False
