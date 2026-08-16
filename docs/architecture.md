# Architecture

## Shape

One FastAPI service, one Postgres database, one Next.js dashboard. No queue, no
microservices. The workload is a handful of scheduled fetches per day against slow-moving
data — anything more elaborate is cost without benefit.

```
  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │ CBK / KNBS   │   │ MyStocks /   │   │ Bank PDFs    │
  │ macro pages  │   │ NSE prices   │   │ (quarterly)  │
  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
         │                  │                  │
         └────────┬─────────┴──────────────────┘
                  ▼
        app/ingestion/*  +  app/parser/*
                  │  plain dataclasses, no DB coupling
                  ▼
        ┌───────────────────────┐
        │ Postgres              │  macro_indicators · price_bars
        │                       │  bank_reports · sector_scores · alerts
        └──────────┬────────────┘
                   ▼
        app/scoring/engine.py  ──►  Sector Health Score (1–100) + signal
                   │
                   ▼
        app/alerting/*  ──►  email (only on a signal change that clears exit cost)
                   │
                   ▼
        FastAPI /api/*  ──►  Next.js dashboard
```

## Design decisions worth defending

**Connectors return dataclasses, not ORM rows.** `app/ingestion/base.py` defines
`MacroPoint` and `PricePoint`. Persistence happens in the job layer. This means every
connector is testable against a saved HTML fixture with no database running.

**All the arguable numbers live in `scoring/weights.py`.** Bands, weights, and signal
thresholds are data. `scoring/engine.py` and `scoring/rules.py` are pure functions with
no constants. When a backtest says the CBR band is wrong, you change one file and re-run
the tests.

**Missing data scores neutral, it does not score badly.** A stale CPI reading shouldn't
manufacture a SELL. Each component has a staleness limit in `MAX_STALENESS_DAYS`; past
it, the input drops to 50 and the dashboard says so.

**Extracted figures are quarantined.** The LLM parser must return the verbatim source
line for every number. If that line isn't in the document, the row is stored with
`needs_review=True` and excluded from scoring. A hallucinated NPL ratio is the single
most expensive failure this system can have.

**Alerts fire on signal *changes*, with a cooldown.** A daily "still HOLD" email gets
ignored within a week, and an ignored alert channel is worse than none.

**Exit cost is a gate, not a footnote.** `alerting/fees.py` models the round trip — exit
fee plus re-entry fee plus a buffer. A SELL only escalates when the expected loss clears
it.

## Data model

| Table | Grain | Notes |
|---|---|---|
| `macro_indicators` | one code, one date | Unique on (code, observed_on) — jobs upsert, never blind-insert |
| `price_bars` | one ticker, one trading day | Unique on (ticker, traded_on) |
| `bank_reports` | one bank, one quarter | Holds extraction confidence and the review flag |
| `sector_scores` | one per day | Stores the component breakdown as JSON so past readings stay explainable after weights change |
| `alerts` | one per delivery decision | Includes suppressed ones, for auditing the alert rule |

Storing the component breakdown alongside the score matters: when you re-tune weights in
month three, you can still explain why month one said SELL.

## Where this grows

- **More constituents** — add tickers to `CONSTITUENT_TICKERS`; nothing else changes.
- **Backtesting** — the scoring engine takes an `IndicatorSnapshot` and returns a result.
  Feed it historical snapshots in a loop; no new architecture needed.
- **SMS or push** — add a function beside `notifier.send_email` and call it from the same
  place.
