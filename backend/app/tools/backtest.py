"""Replay history through the current scoring weights.

This is the tool that tells you whether your weights are any good. It answers
three questions:

  * How often would the signal have flipped? More than a handful of times a
    year and you'd be paying fees to chase noise.
  * How long did it sit in each state?
  * Which component was doing the deciding?

`replay` is pure — hand it a list of snapshots and it works with no database,
which is how it gets tested.
"""
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta

from app.schemas.indicators import IndicatorSnapshot
from app.scoring.engine import calculate


@dataclass
class Flip:
    on: date
    from_signal: str
    to_signal: str
    score: float


@dataclass
class BacktestReport:
    days: int = 0
    flips: list[Flip] = field(default_factory=list)
    days_in_signal: Counter = field(default_factory=Counter)
    mean_score: float = 0.0
    min_score: float = 0.0
    max_score: float = 0.0

    @property
    def flips_per_year(self) -> float:
        return round(len(self.flips) / max(self.days, 1) * 365, 1)

    def summary(self) -> str:
        lines = [
            f"Days replayed:      {self.days}",
            f"Score range:        {self.min_score:.0f} – {self.max_score:.0f} "
            f"(mean {self.mean_score:.1f})",
            f"Signal changes:     {len(self.flips)}  (~{self.flips_per_year}/year)",
            "",
            "Time in each signal:",
        ]
        for signal, count in self.days_in_signal.most_common():
            share = count / max(self.days, 1) * 100
            lines.append(f"  {signal:<5} {count:>5} days  ({share:.0f}%)")
        if self.flips:
            lines += ["", "Changes:"]
            for flip in self.flips:
                lines.append(f"  {flip.on}  {flip.from_signal} -> {flip.to_signal}  ({flip.score:.0f})")
        lines += [
            "",
            "Read this before trusting a signal: if the flip count is high, the bands in",
            "scoring/weights.py are too narrow for how noisy the inputs are. Widen them,",
            "re-run, and write down what you changed in docs/scoring-notes.md.",
        ]
        return "\n".join(lines)


def replay(snapshots: list[IndicatorSnapshot]) -> BacktestReport:
    report = BacktestReport()
    scores: list[float] = []
    previous: str | None = None

    for snapshot in snapshots:
        result = calculate(snapshot)
        scores.append(result.score)
        report.days_in_signal[result.signal] += 1
        if previous is not None and result.signal != previous:
            report.flips.append(
                Flip(
                    on=result.scored_on,
                    from_signal=previous,
                    to_signal=result.signal,
                    score=result.score,
                )
            )
        previous = result.signal

    report.days = len(snapshots)
    if scores:
        report.mean_score = round(sum(scores) / len(scores), 1)
        report.min_score = min(scores)
        report.max_score = max(scores)
    return report


def main(days: int = 365) -> int:
    """Build one snapshot per day from the database and replay them."""
    from app.db.session import SessionLocal
    from app.services.snapshot import build_snapshot

    end = date.today()
    start = end - timedelta(days=days)
    snapshots: list[IndicatorSnapshot] = []

    with SessionLocal() as session:
        for offset in range((end - start).days + 1):
            build = build_snapshot(session, as_of=start + timedelta(days=offset))
            snapshots.append(build.snapshot)

    if not snapshots:
        print("No data to replay. Run: python -m app.cli seed")
        return 1

    print(replay(snapshots).summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
