# Build order

Each step ends with something you can run and check. Don't move on until it does.

## Phase 1 — Foundations (weeks 1–2)

1. **Environment.** Clone, create the venv, `pip install -r requirements.txt`,
   `npm install`. Confirm `pytest` passes and `npm run dev` serves a page.
2. **Database.** `docker compose up -d db`, then generate and apply the first migration.
   Confirm `GET /health/db` returns `reachable`.
3. **API keys.** Register for market data; confirm the LLM key works with a one-line
   script. Do this early — key approval is the most common schedule slip.
4. **Save fixtures.** Download one CBK rates page, one KNBS CPI release, one treasury
   auction result, and one bank quarterly PDF into `backend/tests/fixtures/`. Every
   connector gets built against these, so you can work offline and test deterministically.

## Phase 2 — The engine (weeks 3–4)

5. **Connectors, one at a time.** Order: prices → CBR → treasury yields → CPI. Prices
   first because they're a clean JSON API and prove the persistence path. For each:
   write `fetch()`, write a test against the saved fixture, then wire the upsert.
6. **Document parser.** `pdf_loader.py` first (pure, testable), then
   `llm_extractor.py`. Build the verification step *before* you trust any output — check
   that each returned figure's evidence line actually appears in the PDF.
7. **Job wiring.** Fill in the three functions in `jobs/scheduler.py` so
   `python -m app.cli score` produces a real `sector_scores` row.
8. **Backtest.** Replay 12–24 months of snapshots through `scoring.engine.calculate`.
   Look at what the signals would have told you to do, and how often. If it flips more
   than a few times a year, widen the bands. Record what you changed and why in
   `scoring-notes.md`.

## Phase 3 — Surface (week 5)

9. **Dashboard against real data.** The frontend is already built to the API contract;
   it should light up once scores exist. Fix the gaps you find.
10. **Alerting.** Configure SMTP, force a signal change with a fabricated snapshot,
    confirm the email arrives and the cooldown suppresses the follow-up.
11. **Deploy.** Backend and Postgres on one small host; dashboard on Vercel or the same
    host. Set the scheduler to unpaused. Add an uptime check on `/health` — a monitoring
    system that dies silently is worse than none.

## Phase 4 — Launch

12. **Paper-run first.** Let it produce signals for at least a few weeks with no money
    following them. Compare what it said to what happened.
13. **Then go live** alongside the ETF listing, with the weights you actually believe.

## Rules of thumb while building

- Never let a connector write directly to the database. Fetch, return, persist — three
  separate things.
- Every new number that affects a decision goes in `weights.py`, not in a function body.
- If a test needs the network, it isn't a test.
