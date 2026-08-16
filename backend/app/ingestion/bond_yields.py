"""Treasury bill and bond yield connector.

Emits T91 / T364 weekly auction results and the latest long bond yield. These
are the risk-free comparison used to detect capital rotating out of equities.
"""
from app.ingestion.base import Connector, MacroPoint


class TreasuryYieldConnector(Connector):
    name = "cbk_treasury"

    def fetch(self) -> list[MacroPoint]:
        raise NotImplementedError("Implement in Phase 2, step 1.")
