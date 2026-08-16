"""Inflation (CPI) connector — KNBS monthly release.

KNBS's landing page (`/cpi-and-inflation-rates/`) links to a handful of recent
monthly report pages named like
`/reports/consumer-price-indices-and-inflation-rates-<month>-<year>/`. Each
report page states the headline figure in a fixed sentence:

    "Annual consumer price inflation was 6.5 per cent in July 2026, as
    measured by the Consumer Price Index (CPI)."

Strategy: fetch the landing page, find every report link, pick the newest by
(year, month), fetch that report, and regex out the sentence above. Emits one
MacroPoint per month with code "CPI".
"""
import re
from calendar import month_name
from datetime import date

import httpx

from app.config import settings
from app.ingestion.base import Connector, MacroPoint

LANDING_PATH = "/cpi-and-inflation-rates/"

_MONTHS = {m.lower(): i for i, m in enumerate(month_name) if m}

_REPORT_LINK_RE = re.compile(
    r'href="(https?://[^"]*?/reports/consumer-price-indices-and-inflation-rates-'
    r'([a-z]+)-(\d{4})/?)"',
    re.IGNORECASE,
)

_HEADLINE_RE = re.compile(
    r"[Aa]nnual\s+consumer\s+price\s+inflation\s+was\s+([\d.]+)\s+per\s*cent\s+in\s+"
    r"([A-Za-z]+)\s+(\d{4})"
)


def _latest_report_link(html: str) -> tuple[str, int, int] | None:
    """Return (url, year, month) for the most recent report linked on the landing page."""
    best: tuple[str, int, int] | None = None
    for url, month_text, year_text in _REPORT_LINK_RE.findall(html):
        month = _MONTHS.get(month_text.lower())
        if month is None:
            continue
        year = int(year_text)
        if best is None or (year, month) > (best[2], best[1]):
            best = (url, month, year)
    if best is None:
        return None
    url, month, year = best
    return url, year, month


def _parse_headline(html: str) -> tuple[float, int, int] | None:
    """Return (inflation_rate_pct, year, month) parsed from a report page."""
    match = _HEADLINE_RE.search(html)
    if not match:
        return None
    value = float(match.group(1))
    month = _MONTHS.get(match.group(2).lower())
    year = int(match.group(3))
    if month is None:
        return None
    return value, year, month


class KnbsCpiConnector(Connector):
    name = "knbs_cpi"

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or settings.knbs_cpi_url

    def fetch(self) -> list[MacroPoint]:
        # See settings.knbs_verify_tls docstring in config.py — defaults to secure.
        with httpx.Client(timeout=20, follow_redirects=True, verify=settings.knbs_verify_tls) as client:
            landing = client.get(f"{self.base_url}{LANDING_PATH}")
            landing.raise_for_status()
            link = _latest_report_link(landing.text)
            if link is None:
                raise ValueError("KNBS CPI landing page: no monthly report links found.")
            report_url, _year, _month = link

            report = client.get(report_url)
            report.raise_for_status()

        return self._parse(report.text)

    def _parse(self, report_html: str) -> list[MacroPoint]:
        parsed = _parse_headline(report_html)
        if parsed is None:
            raise ValueError("KNBS CPI report page: headline inflation sentence not found.")
        value, year, month = parsed
        return [MacroPoint(code="CPI", observed_on=date(year, month, 1), value=value, source="KNBS")]
