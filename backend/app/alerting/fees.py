"""Exit-cost arithmetic.

An exit only makes sense when the loss you expect to avoid is larger than what
it costs to get out and back in. These are pure functions so they can be tested
and reasoned about without touching the database.
"""
from app.config import settings


def round_trip_cost_pct(
    exit_fee_pct: float | None = None,
    reentry_fee_pct: float | None = None,
) -> float:
    """Total drag, in percent, of selling now and buying back later."""
    exit_fee = settings.brokerage_exit_fee_pct if exit_fee_pct is None else exit_fee_pct
    reentry_fee = exit_fee if reentry_fee_pct is None else reentry_fee_pct
    return exit_fee + reentry_fee


def exit_is_justified(
    predicted_loss_pct: float,
    exit_fee_pct: float | None = None,
    buffer_pct: float | None = None,
) -> bool:
    """True when the expected loss clears the round-trip cost plus a safety buffer."""
    buffer = settings.exit_fee_safety_buffer_pct if buffer_pct is None else buffer_pct
    return predicted_loss_pct > round_trip_cost_pct(exit_fee_pct) + buffer


def net_proceeds(position_value: float, exit_fee_pct: float | None = None) -> float:
    """What actually lands in the money market fund after fees."""
    fee = settings.brokerage_exit_fee_pct if exit_fee_pct is None else exit_fee_pct
    return round(position_value * (1 - fee / 100.0), 2)
