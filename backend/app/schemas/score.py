"""Wire formats for the Sector Health Score."""
from datetime import date

from pydantic import BaseModel, ConfigDict


class ComponentScore(BaseModel):
    code: str            # CBR | CPI | YIELD | NPL | MOMENTUM
    raw_value: float | None
    sub_score: float     # 0-100, higher is healthier
    weight: float
    note: str = ""


class SectorScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scored_on: date
    score: float
    signal: str
    components: list[ComponentScore] = []
