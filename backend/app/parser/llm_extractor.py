"""Extract NPL ratio, PAT and loan book from report text using an LLM.

Design rules that matter more than the model choice:
  * Ask for strict JSON with a fixed schema, no prose.
  * Require the model to return the verbatim source line for each number so it
    can be checked against the document.
  * Anything that fails verification is stored with needs_review=True and is
    excluded from scoring until a human confirms it.

The provider calls below are written but UNVERIFIED against a live API — there
was no network access when they were written. Expect to adjust the response
parsing on first run; the shape of the prompt and the verification logic is the
part that matters and that part is tested offline.
"""
import json
import re
from dataclasses import dataclass, field

from app.config import settings

EXTRACTION_SCHEMA = {
    "npl_ratio": "gross non-performing loans as a percentage of gross loans",
    "profit_after_tax": "profit after tax for the period, in KES",
    "loan_book": "gross loans and advances to customers, in KES",
}

SYSTEM_PROMPT = (
    "You extract figures from Kenyan bank financial statements. "
    "Return JSON only, no commentary and no markdown fences. "
    "The JSON must have one key per requested field, each mapping to an object "
    'with "value" (a number, or null if the figure is not present) and '
    '"evidence" (the exact line of text from the document the number was read '
    "from, copied character for character). "
    "Never estimate, convert, or infer a value that is not printed in the text. "
    "If a figure is absent, return null rather than a guess."
)


@dataclass
class ExtractionResult:
    values: dict[str, float | None]
    evidence: dict[str, str]
    confidence: float = 0.0
    verified: bool = False
    failures: list[str] = field(default_factory=list)


def build_prompt(document_text: str, ticker: str, period: str) -> str:
    fields = "\n".join(f"- {k}: {v}" for k, v in EXTRACTION_SCHEMA.items())
    return (
        f"Bank: {ticker}\nPeriod: {period}\n\nExtract these fields:\n{fields}\n\n"
        f"---- DOCUMENT ----\n{document_text}"
    )


# --- Response handling (pure, testable offline) -----------------------------


def strip_fences(text: str) -> str:
    """Models add ```json fences even when told not to."""
    return re.sub(r"^\s*```(?:json)?|```\s*$", "", text.strip()).strip()


def parse_response(text: str) -> ExtractionResult:
    """Turn the model's JSON into an ExtractionResult. Tolerant of missing keys."""
    data = json.loads(strip_fences(text))
    values: dict[str, float | None] = {}
    evidence: dict[str, str] = {}
    for field_name in EXTRACTION_SCHEMA:
        entry = data.get(field_name) or {}
        raw = entry.get("value")
        values[field_name] = float(raw) if isinstance(raw, (int, float)) else None
        evidence[field_name] = str(entry.get("evidence") or "")
    return ExtractionResult(values=values, evidence=evidence)


NUMBER_PATTERN = re.compile(r"\d[\d,]*(?:\.\d+)?")


def numbers_in(text: str) -> list[float]:
    """Every number in a line, with thousands separators removed."""
    found: list[float] = []
    for token in NUMBER_PATTERN.findall(text):
        try:
            found.append(float(token.replace(",", "")))
        except ValueError:
            continue
    return found


def value_appears_in(value: float, line: str) -> bool:
    """True when the line actually contains this number.

    Compares parsed numbers rather than digit strings. An earlier version
    matched digits as substrings, which broke on 12450000000.0 vs
    "KES 12,450,000,000" (the trailing .0 added a digit) and would also have
    accepted 13 as a match for 13.4. Parse both sides and compare.
    """
    return any(abs(value - candidate) <= 0.005 for candidate in numbers_in(line))


def verify_against_source(result: ExtractionResult, document_text: str) -> ExtractionResult:
    """Two checks, both required:
      1. the evidence line the model quoted really appears in the document, and
      2. the number it reported really appears in that line.

    Check 2 is the point of the whole design: without it a model can quote a
    real sentence and attach an invented figure to it. Fields that fail are set
    to None and named in result.failures.
    """
    failures: list[str] = []
    for field_name, value in list(result.values.items()):
        if value is None:
            continue
        line = result.evidence.get(field_name, "")
        if not line or line not in document_text:
            failures.append(f"{field_name}: quoted line not found in document")
            result.values[field_name] = None
        elif not value_appears_in(value, line):
            failures.append(f"{field_name}: value {value} not present in its own quoted line")
            result.values[field_name] = None

    checked = [f for f in EXTRACTION_SCHEMA if result.values.get(f) is not None]
    result.failures = failures
    result.confidence = round(len(checked) / len(EXTRACTION_SCHEMA), 2)
    result.verified = not failures and bool(checked)
    return result


# --- Provider calls ---------------------------------------------------------


def _call_openai(prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.llm_model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


def _call_gemini(prompt: str) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.llm_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0,
            response_mime_type="application/json",
        ),
    )
    return response.text or ""


def extract(document_text: str, ticker: str, period: str) -> ExtractionResult:
    """Full round trip: prompt, call, parse, verify."""
    prompt = build_prompt(document_text, ticker, period)
    raw = _call_openai(prompt) if settings.llm_provider == "openai" else _call_gemini(prompt)
    return verify_against_source(parse_response(raw), document_text)
