"use client";

import { useEffect, useState } from "react";

import { AlertFeed } from "@/components/AlertFeed";
import { ComponentBreakdown } from "@/components/ComponentBreakdown";
import { Sparkline } from "@/components/Sparkline";
import { ThresholdRail } from "@/components/ThresholdRail";
import { ApiError, api } from "@/lib/api";
import type { Alert, SectorScore } from "@/lib/types";

const SIGNAL_CLASS = { BUY: "signal-buy", HOLD: "signal-hold", SELL: "signal-sell" } as const;

export default function Dashboard() {
  const [score, setScore] = useState<SectorScore | null>(null);
  const [history, setHistory] = useState<SectorScore[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [noScoreYet, setNoScoreYet] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [latest, series, feed] = await Promise.all([
          api.latestScore().catch((err) => {
            if (err instanceof ApiError && err.status === 404) return null;
            throw err;
          }),
          api.scoreHistory(90).catch(() => []),
          api.alerts(20).catch(() => []),
        ]);
        if (cancelled) return;
        setScore(latest);
        setNoScoreYet(latest === null);
        setHistory(series);
        setAlerts(feed);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Something went wrong.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="shell">
      <header className="masthead">
        <h1>Sector Health</h1>
        <div className="eyebrow">
          WSA Banking ETF · Nairobi Securities Exchange
          {score ? ` · reading of ${score.scored_on}` : ""}
        </div>
      </header>

      {loading && (
        <section className="panel">
          <div className="state">Loading the latest reading…</div>
        </section>
      )}

      {!loading && error && (
        <section className="panel">
          <div className="state">
            <strong>The dashboard can&apos;t read the API</strong>
            {error} Start the backend with <code>uvicorn app.main:app --reload</code> and reload
            this page.
          </div>
        </section>
      )}

      {!loading && !error && noScoreYet && (
        <section className="panel">
          <div className="state">
            <strong>No score has been calculated yet</strong>
            Fill the database with demo data to see the dashboard working:{" "}
            <code>python -m app.cli seed</code>. For a real reading once your data
            sources are connected, run <code>python -m app.cli score</code>.
          </div>
        </section>
      )}

      {!loading && !error && score && (
        <>
          <section className="panel">
            <div className="reading">
              <div className="reading-value">{score.score.toFixed(0)}</div>
              <div>
                <div className="eyebrow">out of 100</div>
                <div className={`signal-tag ${SIGNAL_CLASS[score.signal]}`}>{score.signal}</div>
              </div>
            </div>
            <ThresholdRail score={score.score} components={score.components} />
          </section>

          <section className="panel">
            <div className="panel-head">
              <h2>What moved the score</h2>
              <span className="eyebrow">weights set in scoring/weights.py</span>
            </div>
            <ComponentBreakdown components={score.components} />
          </section>

          {history.length > 1 && (
            <section className="panel">
              <div className="panel-head">
                <h2>Score, last 90 days</h2>
                <span className="eyebrow">{history.length} readings</span>
              </div>
              <Sparkline values={[...history].reverse().map((row) => row.score)} />
            </section>
          )}
        </>
      )}

      <section className="panel">
        <div className="panel-head">
          <h2>Alerts</h2>
          <span className="eyebrow">signal changes only</span>
        </div>
        <AlertFeed alerts={alerts} />
      </section>

      <p className="footnote">
        Readings are generated from public macroeconomic data and filed bank results. They describe
        conditions, not outcomes, and they are not investment advice.
      </p>
    </main>
  );
}
