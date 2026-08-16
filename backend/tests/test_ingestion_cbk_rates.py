"""CBK CBR connector, tested against a saved real page — no network required."""
from datetime import date
from pathlib import Path

from app.ingestion.cbk_rates import CbkRateConnector, _parse_rows

FIXTURE = Path(__file__).parent / "fixtures" / "cbk_rates_page.html"


def _html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def test_parses_rows_from_the_real_page():
    rows = _parse_rows(_html())
    assert len(rows) > 50  # the page has the full 2008-present history
    for observed_on, value in rows:
        assert isinstance(observed_on, date)
        assert 0 < value < 30  # sane CBR bound, percent


def test_picks_the_most_recent_row_by_date_not_by_position():
    """Regression guard: this page's table is not reliably in date order.

    A saved snapshot (2026-08-16) ends with rows dated 10/02/2026, 09/06/2026,
    08/04/2026 — out of order. Taking "the last row" would silently return a
    stale rate; the connector must compare parsed dates instead.
    """
    connector = CbkRateConnector()
    points = connector._parse(_html())
    assert len(points) == 1
    point = points[0]
    assert point.code == "CBR"
    assert point.source == "CBK"
    rows = _parse_rows(_html())
    assert point.observed_on == max(r[0] for r in rows)
    assert point.value == dict(rows)[point.observed_on]
