"""Wire formats for macro indicators and prices."""
from datetime import date

from pydantic import BaseModel, ConfigDict


class MacroIndicatorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    observed_on: date
    value: float
    unit: str
    source: str


class PriceBarOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    traded_on: date
    close: float
    volume: float | None = None


class IndicatorSnapshot(BaseModel):
    """The latest reading of every input the score depends on."""

    cbr: float | None = None
    cpi: float | None = None
    t364_yield: float | None = None
    avg_npl_ratio: float | None = None
    etf_price: float | None = None
    etf_price_30d_ago: float | None = None
    as_of: date | None = None
