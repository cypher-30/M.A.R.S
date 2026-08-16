"""Wire formats for alerts."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    level: str
    signal: str
    headline: str
    body: str
    delivered: bool
    created_at: datetime
