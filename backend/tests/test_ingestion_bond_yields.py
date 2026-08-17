"""Treasury bill connector and parser tests against offline fixtures."""
from datetime import date
from pathlib import Path

import pytest
from httpx import Request, Response
from pypdf import PdfReader

from app.ingestion.bond_yields import (
    TreasuryYieldConnector,
    _extract_results_pdf_links,
    _parse_pdf_text,
    _select_latest_results_pdf_link,
)

FIXTURE = Path(__file__).parent / "fixtures" / "cbk_treasury_bill_results_sample.pdf"


def _extracted_text() -> str:
    return PdfReader(str(FIXTURE)).pages[0].extract_text()


def test_parses_t91_and_t364_from_a_real_auction_result():
    points = _parse_pdf_text(_extracted_text())
    by_code = {p.code: p for p in points}
    assert set(by_code) == {"T91", "T364"}
    assert by_code["T91"].value == pytest.approx(8.8347)
    assert by_code["T364"].value == pytest.approx(8.9953)
    assert by_code["T91"].observed_on == date(2026, 7, 6)
    assert by_code["T364"].source == "CBK"


def test_picks_newest_results_pdf_link_by_date_not_position():
    links = [
        "/uploads/91_day_historical_treasury_bill_results/old-results Dated 06-07-2026.pdf",
        "/uploads/91_day_historical_treasury_bill_results/new-results Dated 13-07-2026.pdf",
    ]
    assert _select_latest_results_pdf_link(links) == links[1]


def test_extracts_results_pdf_links_from_html():
    html = """
    <a href="/uploads/91_day_historical_treasury_bill_results/a Dated 06-07-2026.pdf">a</a>
    <a href="/uploads/91_day_historical_treasury_bill_results/b Dated 13-07-2026.pdf">b</a>
    """
    assert len(_extract_results_pdf_links(html)) == 2


def test_fetch_downloads_newest_pdf_and_parses_points(monkeypatch):
    fixture_bytes = FIXTURE.read_bytes()
    listing_html = """
    <a href="/uploads/91_day_historical_treasury_bill_results/older Dated 06-07-2026.pdf">older</a>
    <a href="/uploads/91_day_historical_treasury_bill_results/newer Dated 13-07-2026.pdf">newer</a>
    """

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, url: str):
            request = Request("GET", url)
            if url.endswith("/bills-bonds/treasury-bills/"):
                return Response(200, request=request, text=listing_html)
            if "newer" in url:
                return Response(200, request=request, content=fixture_bytes)
            return Response(404, request=request, text="not found")

    monkeypatch.setattr("app.ingestion.bond_yields.httpx.Client", FakeClient)
    points = TreasuryYieldConnector().fetch()
    by_code = {p.code: p for p in points}
    assert set(by_code) == {"T91", "T364"}
    assert by_code["T91"].value == pytest.approx(8.8347)
