"""Treasury bill and bond yield connector.

Emits T91 / T364 weekly auction results as MacroPoints by reading the newest
Treasury-bill results PDF linked from CBK's auction-results page.
"""
import io
import re
from datetime import date
from urllib.parse import urljoin

import httpx
from pypdf import PdfReader

from app.ingestion.base import Connector, MacroPoint

TREASURY_BILLS_PATH = "/bills-bonds/treasury-bills/"

# "Weighted Average Interest Rate of  accepted bids 8.8347% 8.9616% 8.9953%"
# — three tenors in a fixed order: 91-day, 182-day, 364-day.
_ACCEPTED_BIDS_RATE_RE = re.compile(
    r"Weighted Average Interest Rate of\s+accepted bids\s+"
    r"([\d.]+)%\s+([\d.]+)%\s+([\d.]+)%"
)

# "...TREASURY  BILLS ISSUES 2689/091, 2663/182 & 2618/364  DATED 06-07-2026"
_DATED_RE = re.compile(r"DATED\s+(\d{2})-(\d{2})-(\d{4})")

_RESULTS_LINK_RE = re.compile(
    r'href=["\']([^"\']*?/uploads/91_day_historical_treasury_bill_results/[^"\']*?\.pdf)["\']',
    re.IGNORECASE,
)

_DATE_IN_LINK_RE = re.compile(
    r"(?i)(?:dated|dd)\s*(\d{1,2})[.\-](\d{1,2})[.\-](\d{4})"
)


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


def _extract_results_pdf_links(html: str) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()
    for href in _RESULTS_LINK_RE.findall(html):
        if href not in seen:
            links.append(href)
            seen.add(href)
    return links


def _link_date(link: str) -> date | None:
    match = _DATE_IN_LINK_RE.search(link)
    if not match:
        return None
    day, month, year = match.groups()
    try:
        return date(int(year), int(month), int(day))
    except ValueError:
        return None


def _select_latest_results_pdf_link(links: list[str]) -> str | None:
    if not links:
        return None
    dated = [(link, _link_date(link)) for link in links]
    with_date = [(link, observed_on) for link, observed_on in dated if observed_on is not None]
    if not with_date:
        return links[0]
    return max(with_date, key=lambda entry: entry[1])[0]


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    if not text:
        raise ValueError("Treasury bill results PDF had no extractable text.")
    return text


class TreasuryYieldConnector(Connector):
    name = "cbk_treasury"

    def __init__(self, base_url: str = "https://www.centralbank.go.ke") -> None:
        self.base_url = base_url

    def fetch(self) -> list[MacroPoint]:
        listing_url = f"{self.base_url}{TREASURY_BILLS_PATH}"
        with httpx.Client(timeout=20, follow_redirects=True) as client:
            listing = client.get(listing_url)
            listing.raise_for_status()
            links = _extract_results_pdf_links(listing.text)
            pdf_link = _select_latest_results_pdf_link(links)
            if pdf_link is None:
                raise ValueError("CBK treasury-bills page: no results PDF links found.")

            pdf_url = urljoin(self.base_url, pdf_link)
            pdf_response = client.get(pdf_url)
            pdf_response.raise_for_status()

        return _parse_pdf_text(_extract_pdf_text(pdf_response.content))
