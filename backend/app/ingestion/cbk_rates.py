"""Central Bank Rate connector.

The CBK publishes every CBR set by the Monetary Policy Committee since 2008 as
one long history table (a wpDataTable) on a single page — there is no separate
"latest" endpoint. Strategy: fetch the page, read every (date, rate) row out of
the table, and emit the row with the most recent effective date.

Row order in the source table is NOT reliably chronological (verified against a
live fetch on 2026-08-16 — the last three rows were 10/02/2026, 09/06/2026,
08/04/2026, out of date order), so the "latest" row must be found by comparing
parsed dates, never by taking the last row.
"""
from datetime import date, datetime

import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.ingestion.base import Connector, MacroPoint

RATES_PATH = "/rates/central-bank-rate/"


def _parse_rows(html: str) -> list[tuple[date, float]]:
    """Pull every (effective_date, rate) pair out of the CBR history table.

    Finds the table by its header cells ("Date", "Rate") rather than by id or
    class, since wpDataTable ids are auto-generated and not guaranteed stable.
    """
    soup = BeautifulSoup(html, "lxml")
    rows: list[tuple[date, float]] = []

    for table in soup.find_all("table"):
        header_cells = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if "date" not in header_cells or "rate" not in header_cells:
            continue
        for tr in table.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) != 2:
                continue
            date_text = cells[0].get_text(strip=True)
            rate_text = cells[1].get_text(strip=True)
            try:
                observed_on = datetime.strptime(date_text, "%d/%m/%Y").date()
                value = float(rate_text)
            except ValueError:
                continue
            rows.append((observed_on, value))
        if rows:
            break  # first matching table is the one we want

    return rows


class CbkRateConnector(Connector):
    name = "cbk_cbr"

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or settings.cbk_rates_url

    def fetch(self) -> list[MacroPoint]:
        with httpx.Client(timeout=20, follow_redirects=True) as client:
            response = client.get(f"{self.base_url}{RATES_PATH}")
            response.raise_for_status()
        return self._parse(response.text)

    def _parse(self, html: str) -> list[MacroPoint]:
        rows = _parse_rows(html)
        if not rows:
            raise ValueError("CBK rates page: no (date, rate) rows found — page layout may have changed.")
        observed_on, value = max(rows, key=lambda r: r[0])
        return [MacroPoint(code="CBR", observed_on=observed_on, value=value, source="CBK")]
