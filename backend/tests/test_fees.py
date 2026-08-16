"""Exit-cost maths: a sell must clear the round trip before it is worth doing."""
from app.alerting.fees import exit_is_justified, net_proceeds, round_trip_cost_pct
from app.alerting.thresholds import decide
from datetime import date


def test_round_trip_doubles_a_single_fee_by_default():
    assert round_trip_cost_pct(2.0) == 4.0


def test_small_dip_does_not_justify_exit():
    assert exit_is_justified(3.0, exit_fee_pct=2.0, buffer_pct=0.5) is False


def test_large_dip_justifies_exit():
    assert exit_is_justified(9.0, exit_fee_pct=2.0, buffer_pct=0.5) is True


def test_net_proceeds_applies_the_fee():
    assert net_proceeds(100_000, exit_fee_pct=2.0) == 98_000.00


def test_unchanged_signal_is_not_alerted():
    assert decide("HOLD", "HOLD", None, today=date(2026, 9, 1)).should_send is False


def test_new_sell_signal_is_critical():
    decision = decide("SELL", "HOLD", None, today=date(2026, 9, 1))
    assert decision.should_send is True
    assert decision.level == "CRITICAL"


def test_cooldown_suppresses_rapid_flipping():
    decision = decide("BUY", "SELL", date(2026, 8, 31), today=date(2026, 9, 1))
    assert decision.should_send is False
