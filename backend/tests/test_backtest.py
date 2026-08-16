"""The backtest is how you find out the weights are wrong before money does."""
from datetime import date, timedelta

from app.schemas.indicators import IndicatorSnapshot
from app.tools.backtest import replay

HEALTHY = dict(cbr=8.5, cpi=4.2, t364_yield=10.0, avg_npl_ratio=8.0,
               etf_price=110, etf_price_30d_ago=100)
DISTRESSED = dict(cbr=16.0, cpi=11.0, t364_yield=18.0, avg_npl_ratio=19.0,
                  etf_price=85, etf_price_30d_ago=100)


def _series(specs: list[dict]) -> list[IndicatorSnapshot]:
    start = date(2026, 1, 1)
    return [IndicatorSnapshot(as_of=start + timedelta(days=i), **spec)
            for i, spec in enumerate(specs)]


def test_a_steady_market_produces_no_flips():
    report = replay(_series([HEALTHY] * 30))
    assert report.flips == []
    assert report.days_in_signal["BUY"] == 30


def test_a_regime_change_is_caught_once():
    report = replay(_series([HEALTHY] * 20 + [DISTRESSED] * 20))
    assert len(report.flips) == 1
    assert report.flips[0].from_signal == "BUY"
    assert report.flips[0].to_signal == "SELL"
    assert report.flips[0].on == date(2026, 1, 21)


def test_alternating_inputs_expose_a_noisy_ruleset():
    report = replay(_series([HEALTHY, DISTRESSED] * 15))
    assert len(report.flips) == 29
    assert report.flips_per_year > 300      # the number that tells you to widen the bands


def test_empty_input_is_handled():
    report = replay([])
    assert report.days == 0 and report.flips_per_year == 0.0


def test_summary_mentions_the_flip_count():
    report = replay(_series([HEALTHY] * 10 + [DISTRESSED] * 10))
    assert "Signal changes:     1" in report.summary()
