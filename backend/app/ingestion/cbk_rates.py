"""Central Bank Rate connector.

The CBK publishes the CBR after each Monetary Policy Committee meeting.
Strategy: fetch the published rates page, locate the most recent effective
date and rate, and emit a single MacroPoint.

TODO(build): confirm the exact page and table markup before writing the parser,
then keep a saved copy of one page under tests/fixtures/ so this can be tested
without network access.
"""
from app.config import settings
from app.ingestion.base import Connector, MacroPoint


class CbkRateConnector(Connector):
    name = "cbk_cbr"

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or settings.cbk_rates_url

    def fetch(self) -> list[MacroPoint]:
        raise NotImplementedError("Implement in Phase 2, step 1.")
