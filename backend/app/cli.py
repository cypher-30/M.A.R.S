"""Manual triggers for everything the scheduler would otherwise run.

    python -m app.cli macro                       refresh CBR, CPI, treasury yields
    python -m app.cli score                       recalculate today's score, alert if needed
    python -m app.cli reports                     look for new quarterly filings
    python -m app.cli parse <pdf> <TICKER> <PERIOD>   parse one downloaded report
    python -m app.cli seed                        fill the database with demo data
    python -m app.cli backtest                    replay stored history through the scorer

Useful during the build: run a job on demand instead of waiting for its cron.
"""
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")


def _macro() -> int:
    from app.jobs.scheduler import refresh_macro_indicators

    refresh_macro_indicators()
    return 0


def _score() -> int:
    from app.jobs.scheduler import refresh_prices_and_score

    refresh_prices_and_score()
    return 0


def _reports() -> int:
    from app.jobs.scheduler import poll_quarterly_reports

    poll_quarterly_reports()
    return 0


def _parse(args: list[str]) -> int:
    if len(args) != 3:
        print("Usage: python -m app.cli parse <pdf-path> <TICKER> <PERIOD>")
        return 2
    path, ticker, period = args

    from app.db.session import SessionLocal
    from app.db import repository as repo
    from app.parser.llm_extractor import extract
    from app.parser.pdf_loader import load_pdf, select_relevant_pages

    doc = load_pdf(path)
    if not doc.has_text_layer:
        print("This PDF has no text layer (it's a scan). Enter the figures by hand.")
        return 1

    pages = select_relevant_pages(doc, ["non-performing", "profit after tax", "loans and advances"])
    text = "\n\n".join(pages) if pages else doc.text
    result = extract(text, ticker, period)

    print(f"Confidence {result.confidence:.0%} · verified={result.verified}")
    for name, value in result.values.items():
        print(f"  {name}: {value}")
    for failure in result.failures:
        print(f"  REJECTED — {failure}")

    with SessionLocal() as session:
        repo.upsert_bank_report(
            session,
            ticker=ticker.upper(),
            period=period.upper(),
            npl_ratio=result.values.get("npl_ratio"),
            profit_after_tax=result.values.get("profit_after_tax"),
            loan_book=result.values.get("loan_book"),
            extraction_confidence=result.confidence,
            needs_review=True,
            raw_extraction=str(result.evidence),
            source_url=path,
        )
        session.commit()

    print("\nStored with needs_review=True. It will not affect the score until you")
    print("confirm the figures and set needs_review=false.")
    return 0


def _seed() -> int:
    from app.tools.seed_demo import seed

    seed()
    return 0


def _backtest() -> int:
    from app.tools.backtest import main as run_backtest

    return run_backtest()


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    command, rest = args[0], args[1:]
    simple = {"macro": _macro, "score": _score, "reports": _reports, "seed": _seed,
              "backtest": _backtest}
    if command in simple:
        return simple[command]()
    if command == "parse":
        return _parse(rest)
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
