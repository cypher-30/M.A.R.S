"""Stale data must not masquerade as current data."""
from datetime import date

from app.config import settings
from app.db import repository as repo
from app.ingestion.base import MacroPoint, PricePoint
from app.services.snapshot import build_snapshot


def test_fresh_readings_are_used(session):
    repo.upsert_macro_point(session, MacroPoint("CBR", date(2026, 5, 20), 10.0, "test"))
    repo.upsert_macro_point(session, MacroPoint("T364", date(2026, 5, 30), 13.0, "test"))
    session.commit()
    build = build_snapshot(session, as_of=date(2026, 6, 1))
    assert build.snapshot.cbr == 10.0
    assert build.snapshot.t364_yield == 13.0


def test_a_reading_past_its_staleness_limit_is_dropped(session):
    # T364 tolerates 21 days; this one is over four months old.
    repo.upsert_macro_point(session, MacroPoint("T364", date(2026, 1, 5), 13.0, "test"))
    session.commit()
    build = build_snapshot(session, as_of=date(2026, 6, 1))
    assert build.snapshot.t364_yield is None
    assert any("T364" in note for note in build.dropped_as_stale)


def test_one_bank_is_not_a_sector(session):
    repo.upsert_bank_report(session, "KCB", "2026Q1", npl_ratio=12.0, needs_review=False)
    session.commit()
    build = build_snapshot(session, as_of=date(2026, 6, 1))
    assert build.snapshot.avg_npl_ratio is None


def test_two_confirmed_banks_are_averaged(session):
    repo.upsert_bank_report(session, "KCB", "2026Q1", npl_ratio=12.0, needs_review=False)
    repo.upsert_bank_report(session, "EQTY", "2026Q1", npl_ratio=10.0, needs_review=False)
    session.commit()
    build = build_snapshot(session, as_of=date(2026, 6, 1))
    assert build.snapshot.avg_npl_ratio == 11.0


def test_momentum_uses_the_closest_earlier_close(session):
    etf_ticker = settings.active_etf_ticker(date(2026, 6, 1))
    repo.upsert_price_point(session, PricePoint(etf_ticker, date(2026, 4, 30), 100.0))
    repo.upsert_price_point(session, PricePoint(etf_ticker, date(2026, 6, 1), 110.0))
    session.commit()
    build = build_snapshot(session, as_of=date(2026, 6, 1))
    assert build.snapshot.etf_price == 110.0
    assert build.snapshot.etf_price_30d_ago == 100.0


def test_an_empty_database_produces_a_neutral_snapshot(session):
    build = build_snapshot(session, as_of=date(2026, 6, 1))
    snapshot = build.snapshot
    assert (snapshot.cbr, snapshot.cpi, snapshot.avg_npl_ratio, snapshot.etf_price) == (
        None, None, None, None,
    )
    assert build.missing
