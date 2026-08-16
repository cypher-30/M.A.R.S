"""Inflation (CPI) connector — KNBS monthly release.

KNBS publishes a monthly CPI and inflation rate release. Emits one MacroPoint
per month with code "CPI" (year-on-year inflation, percent).
"""
from app.config import settings
from app.ingestion.base import Connector, MacroPoint


class KnbsCpiConnector(Connector):
    name = "knbs_cpi"

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or settings.knbs_cpi_url

    def fetch(self) -> list[MacroPoint]:
        raise NotImplementedError("Implement in Phase 2, step 1.")
