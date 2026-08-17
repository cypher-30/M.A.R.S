"""Daily price connector for the ETF and constituent banks via market-data API.

The provider response shape can vary by endpoint/version (flat list vs grouped
maps, `close` vs `last_price`, etc). Parsing is centralized here so the rest of
the system always receives canonical PricePoint records.
"""
from datetime import date, datetime, timezone
from json import JSONDecodeError
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings
from app.ingestion.base import Connector, PricePoint


_BATCH_ENDPOINT_CANDIDATES = [
    "/api/prices/latest",
    "/api/v1/prices/latest",
    "/prices/latest",
    "/api/quotes/latest",
    "/api/v1/quotes/latest",
]

_PER_TICKER_ENDPOINT_CANDIDATES = [
    "/stocks/{ticker}.KE/candles",
    "/stocks/{ticker}/candles",
    "/stocks/{ticker}.KE/history",
    "/stocks/{ticker}/history",
    "/api/prices/{ticker}/latest",
    "/api/v1/prices/{ticker}/latest",
    "/api/quotes/{ticker}",
    "/api/v1/quotes/{ticker}",
]


def _should_retry(exc: BaseException) -> bool:
    if isinstance(exc, (httpx.ConnectError, httpx.TimeoutException)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        return code in {408, 429} or code >= 500
    return False


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        raw = value.strip().replace(",", "")
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            return None
    return None


def _coerce_date(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc).date()
        except (OverflowError, OSError, ValueError):
            return None
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        for converter in (
            lambda s: datetime.fromisoformat(s.replace("Z", "+00:00")).date(),
            lambda s: date.fromisoformat(s),
        ):
            try:
                return converter(raw)
            except ValueError:
                continue
    return None


def _record_to_price_point(record: dict[str, Any], *, fallback_ticker: str | None = None) -> PricePoint | None:
    ticker = fallback_ticker or record.get("ticker") or record.get("symbol") or record.get("code")
    if isinstance(ticker, str):
        ticker = ticker.strip().upper()
        if "." in ticker:
            ticker = ticker.split(".", 1)[0]
    else:
        return None

    traded_on = _coerce_date(
        record.get("traded_on")
        or record.get("trading_date")
        or record.get("date")
        or record.get("as_of")
        or record.get("timestamp")
        or record.get("datetime")
    )
    if traded_on is None:
        return None

    close = _coerce_float(
        record.get("close")
        or record.get("close_price")
        or record.get("closing_price")
        or record.get("last")
        or record.get("last_price")
        or record.get("price")
    )
    if close is None:
        return None

    volume = _coerce_float(record.get("volume") or record.get("vol") or record.get("traded_volume"))
    source = record.get("source")
    source_name = str(source).strip() if source is not None else "mystocks"
    return PricePoint(
        ticker=ticker,
        traded_on=traded_on,
        close=close,
        volume=volume,
        source=source_name or "mystocks",
    )


def _as_records(payload: Any, *, fallback_ticker: str | None = None) -> list[PricePoint]:
    points: list[PricePoint] = []
    if isinstance(payload, dict):
        if "candles" in payload and isinstance(payload["candles"], list):
            symbol = payload.get("symbol") or payload.get("ticker") or payload.get("code")
            record_ticker = symbol if isinstance(symbol, str) else fallback_ticker
            return _as_records(payload["candles"], fallback_ticker=record_ticker)

        if "priceHistory" in payload and isinstance(payload["priceHistory"], list):
            symbol = payload.get("symbol") or payload.get("ticker") or payload.get("code")
            record_ticker = symbol if isinstance(symbol, str) else fallback_ticker
            return _as_records(payload["priceHistory"], fallback_ticker=record_ticker)

        for key in ("data", "results", "quotes", "prices", "items", "payload"):
            if key in payload:
                return _as_records(payload[key], fallback_ticker=fallback_ticker)

        # Some APIs return grouped records keyed by ticker:
        # {"WSA": [{...}], "KCB": [{...}]}.
        nested_points: list[PricePoint] = []
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                key_as_ticker = key.upper() if isinstance(key, str) and (key.isupper() or "." in key) else fallback_ticker
                nested_points.extend(
                    _as_records(
                        value,
                        fallback_ticker=key_as_ticker,
                    )
                )
        if nested_points:
            return nested_points

        point = _record_to_price_point(payload, fallback_ticker=fallback_ticker)
        if point:
            points.append(point)
        return points

    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                point = _record_to_price_point(item, fallback_ticker=fallback_ticker)
                if point:
                    points.append(point)
        return points

    return points


class NsePriceConnector(Connector):
    name = "mystocks"

    def __init__(self, tickers: list[str] | None = None) -> None:
        raw = tickers or [settings.active_etf_ticker(), *settings.constituents]
        self.tickers = list(dict.fromkeys(raw))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception(_should_retry),
        reraise=True,
    )
    def _get(self, path: str, params: dict | None = None) -> Any:
        headers = {"Authorization": f"Bearer {settings.mystocks_api_key}"}
        with httpx.Client(base_url=settings.mystocks_base_url, timeout=20) as client:
            response = client.get(path, params=params, headers=headers)
            response.raise_for_status()
            content_type = (response.headers.get("content-type") or "").lower()
            if "json" not in content_type:
                raise ValueError(
                    f"MyStocks endpoint returned non-JSON content-type ({content_type}) at {response.url}"
                )
            try:
                return response.json()
            except JSONDecodeError as exc:
                raise ValueError(f"MyStocks endpoint returned invalid JSON at {response.url}") from exc

    def _fetch_batch(self) -> list[PricePoint]:
        for path in _BATCH_ENDPOINT_CANDIDATES:
            try:
                payload = self._get(path, params={"tickers": ",".join(self.tickers)})
            except httpx.HTTPStatusError as error:
                if error.response.status_code == 404:
                    continue
                raise
            points = _as_records(payload)
            if points:
                return points
        return []

    def _fetch_per_ticker(self) -> list[PricePoint]:
        points: list[PricePoint] = []
        missing: list[str] = []
        for ticker in self.tickers:
            for path_template in _PER_TICKER_ENDPOINT_CANDIDATES:
                path = path_template.format(ticker=ticker)
                try:
                    payload = self._get(path)
                except httpx.HTTPStatusError as error:
                    if error.response.status_code == 404:
                        continue
                    raise
                parsed = _as_records(payload, fallback_ticker=ticker)
                if parsed:
                    points.append(max(parsed, key=lambda point: point.traded_on))
                    break
            else:
                missing.append(ticker)
        if missing:
            raise ValueError(f"Price API returned no parseable records for tickers: {', '.join(missing)}")
        return points

    def fetch(self) -> list[PricePoint]:
        points = self._fetch_batch()
        if not points:
            points = self._fetch_per_ticker()

        newest_by_ticker: dict[str, PricePoint] = {}
        for point in points:
            current = newest_by_ticker.get(point.ticker)
            if current is None or point.traded_on > current.traded_on:
                newest_by_ticker[point.ticker] = point

        missing = sorted(set(self.tickers) - set(newest_by_ticker))
        if missing:
            raise ValueError(f"Price API did not return records for tickers: {', '.join(missing)}")

        return [newest_by_ticker[ticker] for ticker in self.tickers if ticker in newest_by_ticker]
