"""Decide whether a score change deserves to interrupt someone.

Two rules keep the channel worth reading:
  1. Only alert on a signal *change*, not on every day the signal holds.
  2. Suppress repeat alerts inside a cooldown window.
"""
from dataclasses import dataclass
from datetime import date, timedelta

COOLDOWN_DAYS = 3


@dataclass
class AlertDecision:
    should_send: bool
    level: str = "INFO"      # INFO | WARNING | CRITICAL
    reason: str = ""


def decide(
    current_signal: str,
    previous_signal: str | None,
    last_alert_on: date | None,
    today: date | None = None,
) -> AlertDecision:
    today = today or date.today()

    if previous_signal == current_signal:
        return AlertDecision(False, reason="Signal unchanged.")

    if last_alert_on and today - last_alert_on < timedelta(days=COOLDOWN_DAYS):
        return AlertDecision(False, reason="Inside cooldown window.")

    level = {"SELL": "CRITICAL", "BUY": "WARNING"}.get(current_signal, "INFO")
    return AlertDecision(True, level=level, reason=f"Signal moved to {current_signal}.")
