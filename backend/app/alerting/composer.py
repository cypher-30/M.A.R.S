"""Turn a score into words a person can act on.

Rules taken from how alerts actually get read:
  * The headline says what changed and what the number is. Nothing else.
  * The body leads with the single biggest reason, not a list of five.
  * A SELL always states the exit-cost maths, because that is the part a
    panicking reader most needs to see.
  * No apologies, no hedging language, no exclamation marks.
"""
from app.alerting.fees import round_trip_cost_pct
from app.schemas.score import SectorScoreOut

LABELS = {
    "CBR": "the Central Bank Rate",
    "CPI": "inflation",
    "YIELD": "364-day treasury yields",
    "NPL": "bad loans at the constituent banks",
    "MOMENTUM": "the ETF's 30-day price trend",
}

SIGNAL_SENTENCE = {
    "SELL": "Conditions have deteriorated past the level you set for moving to the money market fund.",
    "BUY": "Conditions have improved past the level you set for adding to the position.",
    "HOLD": "Conditions are back inside the range where the plan is to sit still.",
}


def biggest_drag(result: SectorScoreOut) -> str:
    """The component costing the most weighted points versus a neutral 50."""
    scored = [c for c in result.components if not c.note]
    if not scored:
        return "no component has fresh data"
    worst = min(scored, key=lambda c: (c.sub_score - 50) * c.weight)
    direction = "weighing on" if worst.sub_score < 50 else "supporting"
    reading = "no reading" if worst.raw_value is None else f"{worst.raw_value:.1f}%"
    return f"{LABELS[worst.code]} at {reading} is {direction} the score most"


def headline(result: SectorScoreOut, previous_signal: str | None) -> str:
    moved = f"{previous_signal} to {result.signal}" if previous_signal else result.signal
    return f"Sector health {result.score:.0f}/100 — signal moved {moved}"


def body(result: SectorScoreOut, previous_signal: str | None) -> str:
    lines = [
        f"Reading for {result.scored_on}: {result.score:.0f} out of 100.",
        "",
        SIGNAL_SENTENCE.get(result.signal, ""),
        "",
        f"Main driver: {biggest_drag(result)}.",
        "",
        "All inputs:",
    ]
    for component in result.components:
        reading = "no fresh data" if component.raw_value is None else f"{component.raw_value:.1f}%"
        lines.append(
            f"  {LABELS[component.code]}: {reading} "
            f"— scores {component.sub_score:.0f}/100, counts for {component.weight * 100:.0f}%"
        )

    if result.signal == "SELL":
        cost = round_trip_cost_pct()
        lines += [
            "",
            f"Before acting: selling and buying back costs about {cost:.1f}% in fees. "
            "This alert fired on conditions, not on a price forecast. Check the "
            "actual expected loss against that cost before moving anything.",
        ]

    stale = [c.code for c in result.components if c.note]
    if stale:
        lines += ["", f"Scored neutral for lack of fresh data: {', '.join(stale)}."]

    lines += ["", "This is a monitoring signal, not investment advice."]
    return "\n".join(lines)
