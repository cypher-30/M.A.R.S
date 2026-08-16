"""KNBS CPI connector, tested against saved real pages — no network required."""
from datetime import date
from pathlib import Path

from app.ingestion.knbs_cpi import KnbsCpiConnector, _latest_report_link, _parse_headline

LANDING = Path(__file__).parent / "fixtures" / "knbs_cpi_landing.html"
REPORT = Path(__file__).parent / "fixtures" / "knbs_cpi_report.html"


def test_finds_the_newest_report_link_on_the_landing_page():
    """Note: verified 2026-08-16, the dedicated /cpi-and-inflation-rates/ landing
    page lagged the KNBS homepage by one release (linked June 2026 as newest,
    while the homepage already listed July 2026). The connector reads the
    landing page since it's a stable, on-topic target; this may run a few
    weeks behind the absolute latest release rather than same-day.
    """
    link = _latest_report_link(LANDING.read_text(encoding="utf-8"))
    assert link is not None
    url, year, month = link
    assert "consumer-price-indices-and-inflation-rates" in url
    assert (year, month) == (2026, 6)  # June 2026 is the newest report linked in the fixture


def test_parses_the_headline_inflation_sentence():
    parsed = _parse_headline(REPORT.read_text(encoding="utf-8"))
    assert parsed is not None
    value, year, month = parsed
    assert value == 6.5
    assert (year, month) == (2026, 7)


def test_connector_parse_returns_one_macro_point():
    connector = KnbsCpiConnector()
    points = connector._parse(REPORT.read_text(encoding="utf-8"))
    assert len(points) == 1
    point = points[0]
    assert point.code == "CPI"
    assert point.source == "KNBS"
    assert point.value == 6.5
    assert point.observed_on == date(2026, 7, 1)
