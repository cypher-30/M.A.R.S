"""Daily price connector for the ETF and its constituent banks.

Uses the MyStocks REST API when a key is configured. Keep the response shape
mapping in one place so swapping providers later touches only this file.
"""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.ingestion.base import Connector, PricePoint


class NsePriceConnector(Connector):
    name = "mystocks"

    def __init__(self, tickers: list[str] | None = None) -> None:
        self.tickers = tickers or [settings.etf_ticker, *settings.constituents]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _get(self, path: str, params: dict | None = None) -> dict:
        headers = {"Authorization": f"Bearer {settings.mystocks_api_key}"}
        with httpx.Client(base_url=settings.mystocks_base_url, timeout=20) as client:
            response = client.get(path, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

    def fetch(self) -> list[PricePoint]:
        raise NotImplementedError(
            "Implement in Phase 2, step 1 — map the provider payload to PricePoint."
        )
