"""Pure functions turning one raw reading into a 0-100 sub-score."""
from app.scoring.weights import BANDS, MOMENTUM_BANDS, NEUTRAL_SUB_SCORE


def band_score(code: str, value: float | None) -> float:
    """Lower reading is healthier for CBR, CPI, YIELD and NPL."""
    if value is None:
        return NEUTRAL_SUB_SCORE
    for upper, score in BANDS[code]:
        if value <= upper:
            return float(score)
    return NEUTRAL_SUB_SCORE


def momentum_score(pct_change_30d: float | None) -> float:
    """Higher price change is healthier."""
    if pct_change_30d is None:
        return NEUTRAL_SUB_SCORE
    for upper, score in MOMENTUM_BANDS:
        if pct_change_30d <= upper:
            return float(score)
    return NEUTRAL_SUB_SCORE


def pct_change(current: float | None, previous: float | None) -> float | None:
    if current is None or previous in (None, 0):
        return None
    return (current - previous) / previous * 100.0
