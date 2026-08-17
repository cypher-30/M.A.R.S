"""NSE price connector parsing and endpoint fallback behavior."""
import pytest
from httpx import HTTPStatusError, Request, Response

from app.ingestion.nse_prices import NsePriceConnector, _as_records


def test_parses_flat_data_payload():
    payload = {
        "data": [
            {"ticker": "wsa", "date": "2026-08-16", "close": "12.34", "volume": "1,234"},
            {"ticker": "KCB", "date": "2026-08-16", "last_price": 45.5},
        ]
    }
    points = _as_records(payload)
    assert len(points) == 2
    by_ticker = {point.ticker: point for point in points}
    assert by_ticker["WSA"].close == 12.34
    assert by_ticker["WSA"].volume == 1234.0
    assert by_ticker["KCB"].close == 45.5


def test_parses_grouped_payload_keyed_by_ticker():
    payload = {
        "prices": {
            "WSA": [{"date": "2026-08-16", "close": "12.34"}],
            "KCB": {"date": "2026-08-16", "last_price": 45.5},
        }
    }
    points = _as_records(payload)
    assert {point.ticker for point in points} == {"WSA", "KCB"}


def test_parses_candles_payload_and_normalizes_symbol_suffix():
    payload = {
        "symbol": "KCB.KE",
        "candles": [
            {"timestamp": "2026-08-16T00:00:00.000Z", "close": 82.5, "volume": 1000},
        ],
    }
    points = _as_records(payload)
    assert len(points) == 1
    assert points[0].ticker == "KCB"
    assert points[0].close == 82.5


def test_fetch_uses_batch_endpoint_when_available(monkeypatch):
    connector = NsePriceConnector(tickers=["WSA", "KCB"])

    def fake_get(path: str, params=None):
        assert path == "/api/prices/latest"
        assert params == {"tickers": "WSA,KCB"}
        return {
            "data": [
                {"ticker": "WSA", "date": "2026-08-16", "close": 12.0},
                {"ticker": "KCB", "date": "2026-08-16", "close": 40.5},
            ]
        }

    monkeypatch.setattr(connector, "_get", fake_get)
    points = connector.fetch()
    assert [point.ticker for point in points] == ["WSA", "KCB"]


def test_fetch_falls_back_to_per_ticker_endpoints(monkeypatch):
    connector = NsePriceConnector(tickers=["WSA"])

    def fake_get(path: str, params=None):
        request = Request("GET", f"https://example.com{path}")
        if path == "/api/prices/latest":
            response = Response(404, request=request)
            raise HTTPStatusError("not found", request=request, response=response)
        if path == "/api/v1/prices/latest":
            response = Response(404, request=request)
            raise HTTPStatusError("not found", request=request, response=response)
        if path == "/prices/latest":
            response = Response(404, request=request)
            raise HTTPStatusError("not found", request=request, response=response)
        if path == "/api/quotes/latest":
            response = Response(404, request=request)
            raise HTTPStatusError("not found", request=request, response=response)
        if path == "/api/v1/quotes/latest":
            response = Response(404, request=request)
            raise HTTPStatusError("not found", request=request, response=response)
        if path == "/api/prices/WSA/latest":
            return {"ticker": "WSA", "traded_on": "2026-08-16", "price": 14.2}
        response = Response(404, request=request)
        raise HTTPStatusError("not found", request=request, response=response)

    monkeypatch.setattr(connector, "_get", fake_get)
    points = connector.fetch()
    assert len(points) == 1
    assert points[0].ticker == "WSA"
    assert points[0].close == 14.2


def test_fetch_errors_when_any_ticker_is_missing(monkeypatch):
    connector = NsePriceConnector(tickers=["WSA", "KCB"])

    def fake_get(path: str, params=None):
        return {"data": [{"ticker": "WSA", "date": "2026-08-16", "close": 12.0}]}

    monkeypatch.setattr(connector, "_get", fake_get)
    with pytest.raises(ValueError, match="KCB"):
        connector.fetch()


def test_deduplicates_repeated_tickers_from_configuration(monkeypatch):
    connector = NsePriceConnector(tickers=["KCB", "KCB", "EQTY"])

    def fake_get(path: str, params=None):
        assert params == {"tickers": "KCB,EQTY"}
        return {
            "data": [
                {"ticker": "KCB", "date": "2026-08-16", "close": 90.0},
                {"ticker": "EQTY", "date": "2026-08-16", "close": 91.75},
            ]
        }

    monkeypatch.setattr(connector, "_get", fake_get)
    points = connector.fetch()
    assert [point.ticker for point in points] == ["KCB", "EQTY"]
