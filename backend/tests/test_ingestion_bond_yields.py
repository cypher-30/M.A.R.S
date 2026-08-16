"""Treasury bill results PDF parsing, tested against a saved real auction result.

fetch() itself still raises NotImplementedError — see the module docstring in
app/ingestion/bond_yields.py for why (CBK's results table loads via AJAX, so
there's no static way yet to discover the current week's PDF URL). This test
proves the parsing half, which is real and does not need the network.
"""
from datetime import date
from pathlib import Path

import pytest
from pypdf import PdfReader

from app.ingestion.bond_yields import TreasuryYieldConnector, _parse_pdf_text

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


def test_fetch_is_still_an_explicit_stub():
    with pytest.raises(NotImplementedError):
        TreasuryYieldConnector().fetch()
