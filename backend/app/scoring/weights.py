"""Scoring weights and the bands that turn a raw reading into a sub-score.

Everything a human should be able to argue about lives in this file. The engine
itself contains no numbers. Change these, re-run the backtest, keep a note of
why in docs/scoring-notes.md.

Weights must sum to 1.0.
"""

WEIGHTS: dict[str, float] = {
    "CBR": 0.20,        # cost of borrowing
    "CPI": 0.15,        # inflation
    "YIELD": 0.20,      # risk-free competition for capital
    "NPL": 0.30,        # actual credit distress — the heaviest input
    "MOMENTUM": 0.15,   # 30-day price trend of the ETF
}

# (upper_bound_inclusive, sub_score). Read as: "a CBR at or below 9.0 scores 90".
# The last entry is the floor for anything above the previous bound.
BANDS: dict[str, list[tuple[float, float]]] = {
    "CBR": [(9.0, 90), (11.0, 75), (13.0, 55), (15.0, 35), (float("inf"), 15)],
    "CPI": [(5.0, 90), (7.5, 70), (10.0, 45), (float("inf"), 20)],
    "YIELD": [(11.0, 85), (14.0, 65), (17.0, 40), (float("inf"), 20)],
    "NPL": [(9.0, 90), (12.0, 70), (15.0, 45), (18.0, 25), (float("inf"), 10)],
}

# 30-day ETF price change, percent.
MOMENTUM_BANDS: list[tuple[float, float]] = [
    (-10.0, 15),
    (-5.0, 35),
    (0.0, 55),
    (5.0, 75),
    (float("inf"), 90),
]

# Score thresholds that produce a signal.
SIGNAL_THRESHOLDS = {
    "SELL_BELOW": 35.0,
    "BUY_ABOVE": 70.0,
}

# A component with no fresh data scores neutral rather than dragging the total.
NEUTRAL_SUB_SCORE = 50.0

# Data older than this is treated as missing.
MAX_STALENESS_DAYS = {"CBR": 120, "CPI": 60, "YIELD": 21, "NPL": 200, "MOMENTUM": 7}
