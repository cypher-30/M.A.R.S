"""Combine sub-scores into the daily Sector Health Score and a signal."""
from datetime import date

from app.schemas.indicators import IndicatorSnapshot
from app.schemas.score import ComponentScore, SectorScoreOut
from app.scoring.rules import band_score, momentum_score, pct_change
from app.scoring.weights import SIGNAL_THRESHOLDS, WEIGHTS


def score_components(snapshot: IndicatorSnapshot) -> list[ComponentScore]:
    momentum = pct_change(snapshot.etf_price, snapshot.etf_price_30d_ago)
    raw = {
        "CBR": snapshot.cbr,
        "CPI": snapshot.cpi,
        "YIELD": snapshot.t364_yield,
        "NPL": snapshot.avg_npl_ratio,
        "MOMENTUM": momentum,
    }
    components: list[ComponentScore] = []
    for code, weight in WEIGHTS.items():
        value = raw[code]
        sub = momentum_score(value) if code == "MOMENTUM" else band_score(code, value)
        components.append(
            ComponentScore(
                code=code,
                raw_value=value,
                sub_score=sub,
                weight=weight,
                note="no fresh data — scored neutral" if value is None else "",
            )
        )
    return components


def composite_score(components: list[ComponentScore]) -> float:
    total_weight = sum(c.weight for c in components) or 1.0
    return round(sum(c.sub_score * c.weight for c in components) / total_weight, 1)


def signal_for(score: float) -> str:
    if score < SIGNAL_THRESHOLDS["SELL_BELOW"]:
        return "SELL"
    if score > SIGNAL_THRESHOLDS["BUY_ABOVE"]:
        return "BUY"
    return "HOLD"


def calculate(snapshot: IndicatorSnapshot) -> SectorScoreOut:
    components = score_components(snapshot)
    score = composite_score(components)
    return SectorScoreOut(
        scored_on=snapshot.as_of or date.today(),
        score=score,
        signal=signal_for(score),
        components=components,
    )
