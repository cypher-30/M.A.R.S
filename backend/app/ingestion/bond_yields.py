"""Treasury bill and bond yield connector.

Emits T91 / T364 weekly auction results and the latest long bond yield. These
are the risk-free comparison used to detect capital rotating out of equities.

Investigated 2026-08-16: CBK's auction-results table on
https://www.centralbank.go.ke/bills-bonds/treasury-bills/ is loaded client-side
(it's a wpDataTable rendered via an AJAX call after page load), so a plain HTTP
fetch of that page never contains the PDF links — confirmed by fetching the
static HTML and finding no results/PDF hrefs, only the wpDataTable container
markup. The individual weekly results ARE public, unauthenticated PDFs (e.g.
https://www.centralbank.go.ke/uploads/91_day_historical_treasury_bill_results/
...RESULTS 2689-091 2663-182 2618-364 DATED 06-07-2026.pdf, found via search),
and their layout is a clean, fixed-format text extraction — proven below
against a saved real sample. What's still missing is a way to discover *this
week's* URL without either rendering the page's JS (e.g. a headless browser)
or a manual weekly download. Whoever unblocks this should first try finding
the AJAX endpoint the wpDataTable calls (open the page in a real browser,
check the Network tab for a request to admin-ajax.php or similar, and see if
it can be called directly with plain HTTP).

`_parse_pdf_text` is real and tested against
tests/fixtures/cbk_treasury_bill_results_sample.pdf — once a URL-discovery
method exists, `fetch()` only needs to download the PDF and call it.
"""
import re
from datetime import date

from app.ingestion.base import Connector, MacroPoint

# "Weighted Average Interest Rate of  accepted bids 8.8347% 8.9616% 8.9953%"
# — three tenors in a fixed order: 91-day, 182-day, 364-day.
_ACCEPTED_BIDS_RATE_RE = re.compile(
    r"Weighted Average Interest Rate of\s+accepted bids\s+"
    r"([\d.]+)%\s+([\d.]+)%\s+([\d.]+)%"
)

# "...TREASURY  BILLS ISSUES 2689/091, 2663/182 & 2618/364  DATED 06-07-2026"
_DATED_RE = re.compile(r"DATED\s+(\d{2})-(\d{2})-(\d{4})")


def _parse_pdf_text(text: str) -> list[MacroPoint]:
    """Parse one weekly auction-results PDF's extracted text (pypdf) into
    T91 and T364 MacroPoints. Deliberately skips the 182-day tenor — it has no
    code in app/ingestion/base.py's documented set (CBR|CPI|T91|T364|BOND_10Y)
    and nothing in scoring/ consumes it.
    """
    dated = _DATED_RE.search(text)
    if not dated:
        raise ValueError("Treasury bill results PDF: no 'DATED dd-mm-yyyy' issue date found.")
    day, month, year = dated.groups()
    observed_on = date(int(year), int(month), int(day))

    rates = _ACCEPTED_BIDS_RATE_RE.search(text)
    if not rates:
        raise ValueError(
            "Treasury bill results PDF: 'Weighted Average Interest Rate of accepted "
            "bids' line not found — layout may have changed."
        )
    t91, _t182, t364 = (float(g) for g in rates.groups())

    return [
        MacroPoint(code="T91", observed_on=observed_on, value=t91, source="CBK"),
        MacroPoint(code="T364", observed_on=observed_on, value=t364, source="CBK"),
    ]


class TreasuryYieldConnector(Connector):
    name = "cbk_treasury"

    def fetch(self) -> list[MacroPoint]:
        raise NotImplementedError(
            "Parsing is implemented and tested (_parse_pdf_text). What's missing is "
            "discovering this week's results PDF URL — see module docstring."
        )
