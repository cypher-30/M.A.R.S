# MARS : Market Analysis & Risk System

A daily risk reading for the WSA Banking ETF on the Nairobi Securities Exchange.

The system pulls Kenyan macro data and constituent-bank results, scores the banking
sector from 1 to 100, and sends an alert when the signal changes. Its purpose is to
replace ad-hoc monitoring with a written-down rule you can inspect and argue with.

---

## What it does

| Stage | What happens |
|---|---|
| **Ingest** | Central Bank Rate, CPI inflation, treasury yields, and daily NSE closes land in Postgres. |
| **Parse** | Quarterly bank PDFs are read by an LLM to extract NPL ratio, profit after tax, and loan book. Every figure is verified against the source text before it counts. |
| **Score** | Each input becomes a 0–100 sub-score, weighted into one Sector Health Score. |
| **Alert** | A change in signal (BUY / HOLD / SELL) triggers an email, but only when the expected loss clears the round-trip cost of exiting. |
| **Display** | A dashboard shows today's reading, which input moved it, and the alert history. |

Every number a human might disagree with lives in one file:
`backend/app/scoring/weights.py`. The scoring engine itself contains no constants.

---

## Repository layout

```
MARS/
├── README.md
├── docker-compose.yml          Postgres for local development
├── HANDOFF.md                  Start here: state of play and what to do next
├── docs/
│   ├── what-this-does.md       Plain-English explanation, no jargon
│   ├── architecture.md         How the pieces fit together
│   ├── build-order.md          The step-by-step build plan
│   └── scoring-notes.md        A log of weight and threshold decisions
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── alembic.ini             Migration config
│   ├── alembic/                Migration scripts (initial schema included)
│   ├── app/
│   │   ├── main.py             FastAPI entrypoint
│   │   ├── cli.py              Run any scheduled job on demand
│   │   ├── config.py           All settings, loaded from .env
│   │   ├── db/                 Engine, session, ORM models, repository
│   │   ├── schemas/            Pydantic request/response shapes
│   │   ├── api/routes/         HTTP endpoints
│   │   ├── ingestion/          One module per upstream data source
│   │   ├── parser/             PDF loading + LLM extraction
│   │   ├── scoring/            weights.py · rules.py · engine.py
│   │   ├── services/           snapshot.py — assembles the day's readings
│   │   ├── alerting/           thresholds.py · fees.py · composer.py · notifier.py
│   │   ├── jobs/scheduler.py   Cron definitions and the job bodies
│   │   └── tools/              seed_demo.py · backtest.py
│   └── tests/                  Runs on in-memory SQLite — no setup needed
└── frontend/
    ├── package.json
    ├── .env.local.example
    ├── app/                    Next.js App Router pages + styles
    ├── components/             Rail, breakdown, alert feed, sparkline
    └── lib/                    API client and shared types
```

---

## Setup

Prerequisites: **Python 3.11+**, **Node 20+**, **Docker** (or a local Postgres 16).

### 1. Database

```bash
docker compose up -d db
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                 # then fill in your API keys
alembic revision --autogenerate -m "initial schema"
alembic upgrade head

uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs · Health: http://localhost:8000/health

### 3. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Dashboard: http://localhost:3000

### 4. See it working, with no API keys

```bash
cd backend && python -m app.cli seed
```

This writes 180 days of synthetic data and scores every day of it. Reload the dashboard
and the whole system is live — score, breakdown, trend, thresholds. The numbers are
invented but the code path is the real one. Remove it with:

```bash
python -m app.tools.seed_demo --clear
```

### 5. Check the maths

```bash
cd backend && pytest
```

Around 40 tests covering the scoring rules, exit-cost arithmetic, the upsert layer, the
staleness rules, the PDF-extraction safety check, and the backtest. They run on
in-memory SQLite — no Docker, no network, no API keys. A test that needs infrastructure
doesn't get run, and a test that doesn't get run isn't a test.

---

## Running jobs by hand

```bash
cd backend
python -m app.cli macro                          # refresh CBR, CPI, treasury yields
python -m app.cli score                          # recalculate today's score, alert if needed
python -m app.cli reports                        # look for new quarterly filings
python -m app.cli parse report.pdf KCB 2026Q1    # parse one downloaded bank report
python -m app.cli seed                           # fill with demo data
python -m app.cli backtest                       # replay history through the current weights
```

The scheduler starts paused (`SCHEDULER_PAUSED=true`). Set it to `false` in `.env` once
your connectors return real data.

---

## Configuration

All settings come from `backend/.env` — see `.env.example` for the full list.
The ones you'll touch first:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection string |
| `MYSTOCKS_API_KEY` | Price data for the ETF and constituents |
| `SIMULATED_ETF_TICKER` / `ETF_LIVE_FROM` | Optional pre-launch proxy ticker with automatic cutover date |
| `LLM_PROVIDER` / `OPENAI_API_KEY` / `GEMINI_API_KEY` | The document parser |
| `SMTP_*` / `ALERT_EMAIL_TO` | Where alerts are delivered |
| `BROKERAGE_EXIT_FEE_PCT` | Your actual all-in exit cost — check your broker's schedule |

Never commit `.env`. It's already in `.gitignore`.

---

## A note on what this system is

The score is a written-down opinion, not a prediction. It reflects the weights in
`weights.py`, which are starting guesses until you backtest them. Treat a SELL signal as
a prompt to look, not an instruction to act — and remember that the LLM parser can
misread a PDF, which is why extracted figures are held with `needs_review=True` until
confirmed. This is a monitoring tool, not investment advice.
