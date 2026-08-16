"use client";

import { useEffect, useState } from "react";

import { AlertFeed } from "@/components/AlertFeed";
import { ComponentBreakdown } from "@/components/ComponentBreakdown";
import { KpiCard } from "@/components/KpiCard";
import { Sidebar } from "@/components/Sidebar";
import { Sparkline } from "@/components/Sparkline";
import { ThresholdRail } from "@/components/ThresholdRail";
import { ApiError, api } from "@/lib/api";
import type { Alert, SectorScore } from "@/lib/types";

const SIGNAL_CLASS = { BUY: "signal-buy", HOLD: "signal-hold", SELL: "signal-sell" } as const;
const SIGNAL_TONE = { BUY: "calm", HOLD: "watch", SELL: "risk" } as const;

function recentAlertCount(alerts: Alert[], days: number): number {
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;
  return alerts.filter((alert) => new Date(alert.created_at).getTime() >= cutoff).length;
}

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

  const previousScore = history.length > 1 ? history[1].score : null;
  const delta = score && previousScore !== null ? score.score - previousScore : null;
  const recentAlerts = recentAlertCount(alerts, 30);
  const latestAlert = alerts[0];

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="content">
        <header className="topbar">
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
            <div className="kpi-row">
              <KpiCard
                icon="Σ"
                iconTone={SIGNAL_TONE[score.signal]}
                value={score.score.toFixed(0)}
                label="Sector Health Score, out of 100"
                pill={score.signal}
                pillTone={SIGNAL_TONE[score.signal]}
              />
              <KpiCard
                icon="Δ"
                iconTone={delta === null ? "muted" : delta >= 0 ? "calm" : "risk"}
                value={delta === null ? "—" : `${delta > 0 ? "+" : ""}${delta.toFixed(1)}`}
                label="Change since previous reading"
              />
              <KpiCard
                icon="◷"
                iconTone="muted"
                value={new Date(score.scored_on).toLocaleDateString("en-KE", {
                  day: "2-digit",
                  month: "short",
                })}
                label="Most recent reading"
              />
              <KpiCard
                icon="⚑"
                iconTone={recentAlerts > 0 ? SIGNAL_TONE[latestAlert?.signal ?? "HOLD"] : "muted"}
                value={recentAlerts}
                label="Alerts in the last 30 days"
              />
            </div>

            <section className="panel" id="reading">
              <div className="reading">
                <div className="reading-value">{score.score.toFixed(0)}</div>
                <div>
                  <div className="eyebrow">out of 100</div>
                  <div className={`signal-tag ${SIGNAL_CLASS[score.signal]}`}>{score.signal}</div>
                </div>
              </div>
              <ThresholdRail score={score.score} components={score.components} />
            </section>

            <div className="grid-2">
              <section className="panel" id="breakdown">
                <div className="panel-head">
                  <h2>What moved the score</h2>
                  <span className="eyebrow">weights set in scoring/weights.py</span>
                </div>
                <ComponentBreakdown components={score.components} />
              </section>

              <section className="panel" id="alerts">
                <div className="panel-head">
                  <h2>Alerts</h2>
                  <span className="eyebrow">signal changes only</span>
                </div>
                <AlertFeed alerts={alerts} />
              </section>
            </div>

            {history.length > 1 && (
              <section className="panel" id="trend">
                <div className="panel-head">
                  <h2>Score, last 90 days</h2>
                  <span className="eyebrow">{history.length} readings</span>
                </div>
                <Sparkline values={[...history].reverse().map((row) => row.score)} />
                <div className="trend-foot">
                  <span>{[...history].reverse()[0].scored_on}</span>
                  <span>{history[0].scored_on}</span>
                </div>
              </section>
            )}
          </>
        )}

        {!loading && !error && noScoreYet && (
          <section className="panel" id="alerts">
            <div className="panel-head">
              <h2>Alerts</h2>
              <span className="eyebrow">signal changes only</span>
            </div>
            <AlertFeed alerts={alerts} />
          </section>
        )}

        <p className="footnote">
          Readings are generated from public macroeconomic data and filed bank results. They
          describe conditions, not outcomes, and they are not investment advice.
        </p>
      </main>
    </div>
  );
}
