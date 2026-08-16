"""Alert wording. A person reads these while worried; they have to be clear."""
from datetime import date

from app.alerting.composer import biggest_drag, body, headline
from app.schemas.indicators import IndicatorSnapshot
from app.scoring.engine import calculate

DISTRESSED = IndicatorSnapshot(
    cbr=16.0, cpi=11.0, t364_yield=18.0, avg_npl_ratio=19.0,
    etf_price=85, etf_price_30d_ago=100, as_of=date(2026, 6, 1),
)


def test_headline_states_the_score_and_the_change():
    result = calculate(DISTRESSED)
    text = headline(result, "HOLD")
    assert "SELL" in text and "HOLD" in text and "/100" in text


def test_a_sell_body_always_shows_the_exit_cost():
    text = body(calculate(DISTRESSED), "HOLD")
    assert "fees" in text
    assert "not investment advice" in text


def test_the_body_names_the_biggest_driver():
    result = calculate(DISTRESSED)
    assert biggest_drag(result) in body(result, "HOLD")


def test_missing_inputs_are_disclosed_not_hidden():
    partial = IndicatorSnapshot(cbr=16.0, as_of=date(2026, 6, 1))
    text = body(calculate(partial), "HOLD")
    assert "Scored neutral for lack of fresh data" in text
    assert "no fresh data" in text


def test_biggest_drag_handles_a_completely_empty_snapshot():
    result = calculate(IndicatorSnapshot(as_of=date(2026, 6, 1)))
    assert biggest_drag(result) == "no component has fresh data"
