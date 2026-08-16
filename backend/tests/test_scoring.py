"""The scoring rules are the heart of the system, so they get real tests."""
from app.schemas.indicators import IndicatorSnapshot
from app.scoring.engine import calculate, composite_score, score_components, signal_for
from app.scoring.rules import band_score, momentum_score, pct_change
from app.scoring.weights import NEUTRAL_SUB_SCORE, WEIGHTS


def test_weights_sum_to_one():
    assert round(sum(WEIGHTS.values()), 6) == 1.0


def test_lower_cbr_scores_higher():
    assert band_score("CBR", 8.0) > band_score("CBR", 14.0)


def test_missing_reading_is_neutral():
    assert band_score("NPL", None) == NEUTRAL_SUB_SCORE
    assert momentum_score(None) == NEUTRAL_SUB_SCORE


def test_pct_change():
    assert pct_change(110, 100) == 10.0
    assert pct_change(None, 100) is None
    assert pct_change(110, 0) is None


def test_healthy_snapshot_reads_buy():
    snapshot = IndicatorSnapshot(
        cbr=8.5, cpi=4.2, t364_yield=10.0, avg_npl_ratio=8.0,
        etf_price=110, etf_price_30d_ago=100,
    )
    result = calculate(snapshot)
    assert result.score > 70
    assert result.signal == "BUY"


def test_distressed_snapshot_reads_sell():
    snapshot = IndicatorSnapshot(
        cbr=16.0, cpi=11.0, t364_yield=18.0, avg_npl_ratio=19.0,
        etf_price=85, etf_price_30d_ago=100,
    )
    result = calculate(snapshot)
    assert result.score < 35
    assert result.signal == "SELL"


def test_components_cover_every_weighted_input():
    components = score_components(IndicatorSnapshot())
    assert {c.code for c in components} == set(WEIGHTS)
    assert composite_score(components) == NEUTRAL_SUB_SCORE
    assert signal_for(NEUTRAL_SUB_SCORE) == "HOLD"
