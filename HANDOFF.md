# Handoff

Read this first. It says what state the project is in, what to do next, and which
decisions are already settled so you don't re-litigate them.

**Project:** AEAS — a daily risk score for the WSA Banking ETF on the NSE.
**Plain-English overview:** `docs/what-this-does.md`
**Status:** everything that can be built without internet access is built and tested.
Five pieces need live sources and are stubbed.

---

## 1. Start here (15 minutes, no API keys needed)

```bash
docker compose up -d db

cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
pytest                          # should be all green
python -m app.cli seed          # 180 days of synthetic data
uvicorn app.main:app --reload
```

In a second terminal:

```bash
cd frontend && npm install && cp .env.local.example .env.local && npm run dev
```

Open http://localhost:3000. You should see a score, a threshold rail, a component
breakdown, and a 90-day trend. That's the whole system running on fake data.

Then:

```bash
cd backend && python -m app.cli backtest
```

That prints how often the current weights would have flipped the signal. Look at it —
it's the first real feedback the system gives you.

---

## 2. What's done

| Area | State |
|---|---|
| Database schema + migration | Done. `alembic upgrade head` works on a fresh DB. |
| Persistence layer (`db/repository.py`) | Done, tested. Every write is an upsert, so re-running a job never duplicates or crashes. |
| Snapshot builder (`services/snapshot.py`) | Done, tested. Applies staleness limits: an old reading becomes `None`, not a stale number on a dashboard. |
| Scoring engine (`scoring/`) | Done, tested. All tunable numbers isolated in `weights.py`. |
| Exit-cost maths (`alerting/fees.py`) | Done, tested. |
| Alert throttling (`alerting/thresholds.py`) | Done, tested. Fires on signal *changes* only, with a 3-day cooldown. |
| Alert wording (`alerting/composer.py`) | Done, tested. |
| Email delivery (`alerting/notifier.py`) | Written. Needs your SMTP credentials to verify. |
| Job orchestration (`jobs/scheduler.py`) | Done. Jobs run end-to-end; they skip unbuilt connectors with a log line rather than crashing. |
| API (`api/routes/`) | Done. All endpoints the dashboard uses. |
| Dashboard (`frontend/`) | Done. Handles loading, error, and empty states. |
| PDF text loading (`parser/pdf_loader.py`) | Done. |
| Extraction verification (`parser/llm_extractor.py`) | Done, tested — this is the important half. |
| Demo seeding + backtest (`tools/`) | Done, tested. |

**Test coverage sits on the decision-making code**, which is where a bug costs money.
`pytest` runs on in-memory SQLite with no Docker, no network, no keys.

---

## 3. What's not done, and why

Five things need something I couldn't see offline. Each is a stub that raises
`NotImplementedError` with a note.

| File | What's missing | What unblocks it |
|---|---|---|
| `ingestion/cbk_rates.py` | Parsing the CBK rates page | Save one copy of the page to `tests/fixtures/` |
| `ingestion/knbs_cpi.py` | Parsing the KNBS CPI release | Same — save one release |
| `ingestion/bond_yields.py` | Parsing treasury auction results | Same |
| `ingestion/nse_prices.py` | Mapping the price API's JSON to `PricePoint` | One sample API response |
| `parser/llm_extractor.py` (provider calls) | Written but never run against a live API | An API key; expect to adjust response parsing on first call |

The pattern for each: **save a real sample into `backend/tests/fixtures/` first, write the
parser against the file, then wire it up.** That keeps every connector testable offline
and means a website redesign gives you a failing test instead of a silently wrong score.

---

## 4. Next actions, in order

1. **Register for market data** and get an LLM API key. Do this first — approval time
   is the most common schedule slip, and everything else can proceed while you wait.
2. **Save fixtures.** One CBK rates page, one KNBS CPI release, one treasury auction
   result, one bank quarterly PDF → `backend/tests/fixtures/`.
3. **Build the price connector first.** It's a clean JSON API and it proves the whole
   fetch → upsert → score path with real data.
4. **Then CBR, then treasury yields, then CPI.** One at a time: write `fetch()`, write a
   test against the fixture, wire the upsert, confirm `python -m app.cli macro` works.
5. **Run the PDF parser** on a real report: `python -m app.cli parse report.pdf KCB 2026Q1`.
   Check what it extracted against the PDF by eye. Only after you trust it should you set
   `needs_review=false` on a row.
6. **Clear the demo data** (`python -m app.tools.seed_demo --clear`) and backtest on real
   history. Write what you change, and why, into `docs/scoring-notes.md`.
7. **Configure SMTP**, force a signal change, confirm the email arrives and the cooldown
   suppresses the follow-up.
8. **Deploy**, set `SCHEDULER_PAUSED=false`, add an uptime check on `/health`. A monitor
   that dies silently is worse than no monitor.
9. **Paper-run for several weeks** before any money follows a signal.

---

## 5. Decisions already made (don't undo these without a reason)

- **Connectors return dataclasses, never database rows.** Fetch, return, persist are three
  separate things. This is what makes connectors testable without a database.
- **All arguable numbers live in `scoring/weights.py`.** The engine has no constants. When
  the backtest says a band is wrong, you change one file.
- **Missing or stale data scores neutral (50), never badly.** A stale CPI reading must not
  manufacture a SELL.
- **Extracted PDF figures are quarantined** with `needs_review=True` and excluded from
  scoring until confirmed. The model must quote the source line, and the number must
  appear in that line. A hallucinated NPL ratio is the most expensive failure available.
- **NPL needs at least two confirmed banks** before it counts. One bank is not a sector.
- **Alerts fire on signal changes only, with a cooldown.** An alert channel you learn to
  ignore is worse than none.
- **Exit cost is a gate on SELL, not a footnote.** Round trip is exit fee + re-entry fee
  + buffer.
- **Score components are stored as JSON alongside each score**, so a reading from three
  months ago is still explainable after you re-tune the weights.

---

## 6. Things that will bite you

- **`.env` is read relative to the working directory.** Run `uvicorn` and the CLI from
  `backend/`, not from the repo root.
- **Seeded demo data looks completely real on the dashboard.** Clear it before you look
  at anything and draw a conclusion.
- **The weights are untested guesses.** Nothing has been validated against Kenyan market
  history. Any signal is provisional until step 6 above is done.
- **The ETF is new**, so there's little price history to backtest momentum against. That
  component will be the least trustworthy for a while.
- **Liquidity isn't modelled.** A signal you can't act on at a reasonable spread isn't
  worth acting on. Watch the actual order book before trusting a SELL.
- **The LLM provider calls have never been executed.** Expect to fix the response parsing
  the first time you run them. The prompt design and verification logic are the parts
  that were worth getting right offline, and those are tested.

---

## 7. If you're handing this to another developer or an AI coding session

Point them at, in order: `docs/what-this-does.md`, then this file, then
`docs/architecture.md`, then `docs/build-order.md`. Tell them:

> The scoring, alerting, persistence, and API layers are complete and tested. Do not
> refactor them. The work is in `app/ingestion/` — four connectors, each of which fetches
> from one source and returns the dataclasses defined in `app/ingestion/base.py`. Build
> each against a saved fixture in `tests/fixtures/` so it can be tested without network
> access. Do not let a connector write to the database directly.
