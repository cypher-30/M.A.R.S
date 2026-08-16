"""Shared contract for every data source.

Each connector returns plain dataclass records. Persistence is handled by the
caller (app/jobs/scheduler.py) so connectors stay easy to test offline.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MacroPoint:
    code: str          # CBR | CPI | T91 | T364 | BOND_10Y
    observed_on: date
    value: float
    source: str
    unit: str = "percent"


@dataclass(frozen=True)
class PricePoint:
    ticker: str
    traded_on: date
    close: float
    volume: float | None = None
    source: str = "mystocks"


class Connector(ABC):
    """A single upstream data source."""

    name: str = "connector"

    @abstractmethod
    def fetch(self) -> list:
        """Return the newest available records. Must not raise on empty results."""
        raise NotImplementedError
