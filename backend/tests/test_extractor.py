"""The verification step is the whole safety story for the PDF parser.

A model that quotes a real sentence and attaches an invented number to it is
the failure mode that would quietly corrupt the score. These tests exist so
that failure can't come back.
"""
from app.parser.llm_extractor import (
    ExtractionResult,
    numbers_in,
    value_appears_in,
    build_prompt,
    parse_response,
    strip_fences,
    verify_against_source,
)

DOCUMENT = """
CONDENSED FINANCIAL STATEMENTS
Gross non-performing loans and advances stood at 13.4 percent of gross loans.
Profit after tax for the period was KES 12,450,000,000.
Gross loans and advances to customers were KES 512,300,000,000.
"""


def _result(values, evidence):
    return ExtractionResult(values=values, evidence=evidence)


def test_strip_fences_handles_a_fenced_response():
    assert strip_fences('```json\n{"a": 1}\n```') == '{"a": 1}'


def test_parse_response_reads_values_and_evidence():
    raw = """
    {"npl_ratio": {"value": 13.4, "evidence": "line one"},
     "profit_after_tax": {"value": null, "evidence": ""},
     "loan_book": {"value": 512300000000, "evidence": "line three"}}
    """
    result = parse_response(raw)
    assert result.values["npl_ratio"] == 13.4
    assert result.values["profit_after_tax"] is None
    assert result.evidence["npl_ratio"] == "line one"


def test_parse_response_tolerates_a_missing_field():
    result = parse_response('{"npl_ratio": {"value": 9.1, "evidence": "x"}}')
    assert result.values["loan_book"] is None


def test_a_correct_extraction_verifies():
    result = _result(
        {"npl_ratio": 13.4, "profit_after_tax": None, "loan_book": None},
        {"npl_ratio": "Gross non-performing loans and advances stood at 13.4 percent of gross loans."},
    )
    verified = verify_against_source(result, DOCUMENT)
    assert verified.values["npl_ratio"] == 13.4
    assert verified.failures == []
    assert verified.verified is True


def test_an_invented_quote_is_rejected():
    result = _result(
        {"npl_ratio": 13.4, "profit_after_tax": None, "loan_book": None},
        {"npl_ratio": "Non-performing loans were 13.4 percent."},   # not in the document
    )
    verified = verify_against_source(result, DOCUMENT)
    assert verified.values["npl_ratio"] is None
    assert verified.verified is False


def test_a_real_quote_with_a_wrong_number_is_rejected():
    """The one that matters: the sentence is genuine, the figure is not."""
    result = _result(
        {"npl_ratio": 4.2, "profit_after_tax": None, "loan_book": None},
        {"npl_ratio": "Gross non-performing loans and advances stood at 13.4 percent of gross loans."},
    )
    verified = verify_against_source(result, DOCUMENT)
    assert verified.values["npl_ratio"] is None
    assert "not present in its own quoted line" in verified.failures[0]


def test_thousands_separators_do_not_break_matching():
    result = _result(
        {"npl_ratio": None, "profit_after_tax": 12450000000.0, "loan_book": None},
        {"profit_after_tax": "Profit after tax for the period was KES 12,450,000,000."},
    )
    verified = verify_against_source(result, DOCUMENT)
    assert verified.values["profit_after_tax"] == 12450000000.0
    assert verified.failures == []


def test_a_near_miss_number_is_rejected():
    """13 is not 13.4. Substring matching used to let this through."""
    result = _result(
        {"npl_ratio": 13.0, "profit_after_tax": None, "loan_book": None},
        {"npl_ratio": "Gross non-performing loans and advances stood at 13.4 percent of gross loans."},
    )
    assert verify_against_source(result, DOCUMENT).values["npl_ratio"] is None


def test_number_parsing_handles_separators_and_decimals():
    assert numbers_in("KES 12,450,000,000 and 13.4 percent") == [12450000000.0, 13.4]
    assert value_appears_in(12450000000.0, "was KES 12,450,000,000.") is True
    assert value_appears_in(12450000000.0, "was KES 12,450,000,001.") is False


def test_prompt_names_every_field():
    prompt = build_prompt("text", "KCB", "2026Q1")
    for field_name in ("npl_ratio", "profit_after_tax", "loan_book"):
        assert field_name in prompt
    assert "KCB" in prompt and "2026Q1" in prompt
