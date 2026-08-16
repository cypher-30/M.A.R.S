"""Scheduled work.

  06:30  refresh macro indicators (CBR, CPI, treasury yields)
  17:30  pull the day's NSE closes, recalculate the score, alert if needed
  Mon 07:00  poll for newly published quarterly reports

Every job is safely re-runnable: all writes are upserts, and a connector that
isn't finished yet is skipped with a log line rather than taking the job down.
"""
import json
import logging
from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.alerting import composer
from app.alerting.notifier import send_email
from app.alerting.thresholds import decide
from app.config import settings
from app.db import repository as repo
from app.db.session import SessionLocal
from app.ingestion.base import Connector
from app.ingestion.bond_yields import TreasuryYieldConnector
from app.ingestion.cbk_rates import CbkRateConnector
from app.ingestion.knbs_cpi import KnbsCpiConnector
from app.ingestion.nse_prices import NsePriceConnector
from app.scoring.engine import calculate
from app.services.snapshot import build_snapshot

logger = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None

TIMEZONE = "Africa/Nairobi"

MACRO_CONNECTORS: list[Connector] = [
    CbkRateConnector(),
    KnbsCpiConnector(),
    TreasuryYieldConnector(),
]


def _safe_fetch(connector: Connector) -> list:
    """One broken source must not stop the other three.

    NotImplementedError is treated as 'not built yet' and logged quietly;
    anything else is a real failure and logged loudly, but neither aborts
    the job.
    """
    try:
        return connector.fetch()
    except NotImplementedError:
        logger.info("Connector %s is not implemented yet — skipping.", connector.name)
    except Exception:
        logger.exception("Connector %s failed.", connector.name)
    return []


def refresh_macro_indicators() -> None:
    """Pull every macro source and upsert the results."""
    written = 0
    with SessionLocal() as session:
        for connector in MACRO_CONNECTORS:
            for point in _safe_fetch(connector):
                repo.upsert_macro_point(session, point)
                written += 1
        session.commit()
    logger.info("Macro refresh complete: %s readings written.", written)


def refresh_prices_and_score(as_of: date | None = None) -> None:
    """Pull closes, rebuild the snapshot, score it, and alert on a signal change."""
    as_of = as_of or date.today()

    with SessionLocal() as session:
        for point in _safe_fetch(NsePriceConnector()):
            repo.upsert_price_point(session, point)
        session.commit()

        build = build_snapshot(session, as_of=as_of)
        if build.dropped_as_stale:
            logger.warning("Stale inputs scored neutral: %s", ", ".join(build.dropped_as_stale))
        if build.missing:
            logger.warning("Missing inputs scored neutral: %s", ", ".join(build.missing))

        result = calculate(build.snapshot)
        previous = repo.previous_signal(session, before=as_of)

        row = repo.upsert_sector_score(
            session,
            scored_on=result.scored_on,
            score=result.score,
            signal=result.signal,
            components_json=json.dumps([c.model_dump() for c in result.components]),
        )
        session.flush()

        decision = decide(
            current_signal=result.signal,
            previous_signal=previous,
            last_alert_on=repo.last_alert_date(session),
            today=as_of,
        )
        if decision.should_send:
            head = composer.headline(result, previous)
            text = composer.body(result, previous)
            delivered = send_email(head, text)
            repo.record_alert(
                session,
                level=decision.level,
                signal=result.signal,
                headline=head,
                body=text,
                delivered=delivered,
                sector_score_id=row.id,
            )
            logger.info("Alert raised (%s), delivered=%s", decision.level, delivered)
        else:
            logger.info("No alert: %s", decision.reason)

        session.commit()

    logger.info("Score for %s: %s (%s)", as_of, result.score, result.signal)


def poll_quarterly_reports() -> None:
    """Find newly published bank filings, parse them, store for review.

    Deliberately not automatic end-to-end: parsed figures land with
    needs_review=True and stay out of the score until confirmed.
    """
    logger.info(
        "Report polling needs the publication-source connector (build-order step 6). "
        "Until then, parse a downloaded PDF with: python -m app.cli parse <path> <TICKER> <PERIOD>"
    )


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = BackgroundScheduler(timezone=TIMEZONE)
    _scheduler.add_job(refresh_macro_indicators, CronTrigger(hour=6, minute=30), id="macro")
    _scheduler.add_job(refresh_prices_and_score, CronTrigger(hour=17, minute=30), id="score")
    _scheduler.add_job(poll_quarterly_reports, CronTrigger(day_of_week="mon", hour=7), id="reports")
    # start(paused=True) is required: calling .pause() on a stopped scheduler
    # raises SchedulerNotRunningError and would crash app startup.
    paused = settings.scheduler_paused
    _scheduler.start(paused=paused)
    logger.info("Scheduler started (paused=%s).", paused)


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
