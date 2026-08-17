"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { AlertFeed } from "@/components/AlertFeed";
import { ComponentBreakdown } from "@/components/ComponentBreakdown";
import { DashboardNav } from "@/components/DashboardNav";
import { KpiCard } from "@/components/KpiCard";
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

type TourStep = { title: string; body: string; targetId?: string };

const TOUR_LOADED: TourStep[] = [
  { title: "Welcome to MARS", body: "A 60-second tour of your dashboard. Skip anytime." },
  {
    title: "Today's reading",
    body: "The Sector Health Score, 1 to 100, recalculated daily from four inputs.",
    targetId: "tut-reading",
  },
  {
    title: "The threshold rail",
    body: "Sell below 35. Buy above 70. The marker shows exactly where today sits.",
    targetId: "tut-rail",
  },
  {
    title: "What moved it",
    body: "Every input, its sub-score, and how much weight it carries.",
    targetId: "tut-breakdown",
  },
  {
    title: "Alerts",
    body: "You're notified only when the signal itself changes — never daily noise.",
    targetId: "tut-alerts",
  },
  { title: "The trend", body: "90 days of history, so you can tell a blip from a pattern.", targetId: "tut-trend" },
  { title: "That's it", body: "Revisit this anytime from the tour button in the corner." },
];

const TOUR_EMPTY: TourStep[] = [
  { title: "Welcome to MARS", body: "Here's what you'll see once data starts flowing. Skip anytime." },
  {
    title: "No score yet",
    body: "Run python -m app.cli seed for demo data, or python -m app.cli score once real sources are connected.",
    targetId: "tut-empty",
  },
  {
    title: "You're set",
    body: "Once a score exists, this same tour walks you through the reading, the rail, and the alerts.",
  },
];

function useTour(steps: TourStep[], canStart: boolean) {
  const [active, setActive] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [rect, setRect] = useState<{ top: number; left: number; width: number; height: number } | null>(null);
  const startTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const scrollDebounce = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const recalc = useCallback(() => {
    const target = steps[stepIndex]?.targetId;
    if (!target) {
      setRect(null);
      return;
    }
    const el = document.getElementById(target);
    if (!el) {
      setRect(null);
      return;
    }
    const r = el.getBoundingClientRect();
    setRect({ top: r.top, left: r.left, width: r.width, height: r.height });
  }, [steps, stepIndex]);

  const goToStep = useCallback(
    (index: number, starting = false) => {
      if (index < 0) return;
      if (index >= steps.length) {
        try {
          localStorage.setItem("mars_tutorial_seen", "1");
        } catch {
          // localStorage unavailable — tour just won't remember it ran.
        }
        setActive(false);
        return;
      }
      setActive(true);
      setStepIndex(index);
      const step = steps[index];
      const target = step.targetId ? document.getElementById(step.targetId) : null;
      if (target) {
        const top = target.getBoundingClientRect().top + window.scrollY - 150;
        window.scrollTo({ top: Math.max(top, 0), behavior: starting ? "auto" : "smooth" });
      } else {
        window.scrollTo({ top: 0, behavior: starting ? "auto" : "smooth" });
      }
      setTimeout(recalc, starting ? 60 : 380);
    },
    [steps, recalc],
  );

  useEffect(() => {
    if (!canStart) return;
    try {
      if (localStorage.getItem("mars_tutorial_seen")) return;
    } catch {
      return;
    }
    startTimer.current = setTimeout(() => goToStep(0, true), 700);
    return () => clearTimeout(startTimer.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canStart]);

  useEffect(() => {
    if (!active) return;
    const onResize = () => recalc();
    const onScroll = () => {
      clearTimeout(scrollDebounce.current);
      scrollDebounce.current = setTimeout(recalc, 150);
    };
    window.addEventListener("resize", onResize);
    window.addEventListener("scroll", onScroll, true);
    return () => {
      window.removeEventListener("resize", onResize);
      window.removeEventListener("scroll", onScroll, true);
      clearTimeout(scrollDebounce.current);
    };
  }, [active, recalc]);

  const finish = useCallback(() => {
    try {
      localStorage.setItem("mars_tutorial_seen", "1");
    } catch {
      // ignore
    }
    setActive(false);
  }, []);

  return {
    active,
    step: steps[stepIndex] ?? steps[0],
    stepIndex,
    total: steps.length,
    rect,
    start: () => goToStep(0),
    next: () => goToStep(stepIndex + 1),
    prev: () => goToStep(stepIndex - 1),
    skip: finish,
  };
}

function TourOverlay({ tour }: { tour: ReturnType<typeof useTour> }) {
  if (!tour.active) return null;

  const pad = 10;
  const r = tour.rect;
  const holeTop = r ? r.top - pad : 0;
  const holeLeft = r ? r.left - pad : 0;
  const holeWidth = r ? r.width + pad * 2 : 0;
  const holeHeight = r ? r.height + pad * 2 : 0;
  const hasTarget = !!r;

  const vw = typeof window !== "undefined" ? window.innerWidth : 1200;
  const vh = typeof window !== "undefined" ? window.innerHeight : 800;
  const tooltipW = 300;
  const tooltipH = 172;
  const margin = 24;

  let tooltipTop: number;
  let tooltipLeft: number;
  if (r) {
    const spaceBelow = vh - (holeTop + holeHeight) - margin;
    tooltipTop = spaceBelow >= tooltipH ? holeTop + holeHeight + margin : Math.max(holeTop - margin - tooltipH, 16);
    tooltipLeft = holeLeft + holeWidth / 2 - tooltipW / 2;
  } else {
    tooltipTop = vh / 2 - tooltipH / 2;
    tooltipLeft = vw / 2 - tooltipW / 2;
  }
  tooltipTop = Math.min(Math.max(tooltipTop, 16), Math.max(vh - tooltipH - 16, 16));
  tooltipLeft = Math.min(Math.max(tooltipLeft, 16), Math.max(vw - tooltipW - 16, 16));

  const backdropStyle: React.CSSProperties = {
    position: "fixed",
    background: "rgba(16,19,23,0.55)",
    backdropFilter: "blur(3px)",
    transition: "all 320ms var(--ease)",
    zIndex: 90,
    pointerEvents: "none",
  };

  return (
    <>
      {hasTarget ? (
        <>
          <div style={{ ...backdropStyle, top: 0, left: 0, width: "100vw", height: holeTop }} />
          <div style={{ ...backdropStyle, top: holeTop + holeHeight, left: 0, width: "100vw", bottom: 0 }} />
          <div style={{ ...backdropStyle, top: holeTop, left: 0, width: holeLeft, height: holeHeight }} />
          <div
            style={{ ...backdropStyle, top: holeTop, left: holeLeft + holeWidth, right: 0, height: holeHeight }}
          />
        </>
      ) : (
        <div style={{ position: "fixed", inset: 0, background: "rgba(16,19,23,0.55)", backdropFilter: "blur(3px)", zIndex: 90 }} />
      )}

      <div
        style={{
          position: "fixed",
          top: tooltipTop,
          left: tooltipLeft,
          width: tooltipW,
          background: "var(--surface)",
          borderRadius: "var(--radius-md)",
          padding: "1.25rem",
          boxShadow: "0 20px 40px -16px rgba(16,19,23,0.35)",
          zIndex: 93,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
          <span className="eyebrow" style={{ color: "#a3abb4" }}>
            {tour.stepIndex + 1} of {tour.total}
          </span>
          <button
            onClick={tour.skip}
            style={{ fontFamily: "var(--body)", fontSize: "0.78rem", color: "var(--muted-2)", background: "transparent", border: "none", cursor: "pointer", padding: 0 }}
          >
            Skip tour
          </button>
        </div>
        <div style={{ fontWeight: 600, fontSize: "1rem", marginBottom: "0.4rem" }}>{tour.step.title}</div>
        <div style={{ fontSize: "0.85rem", color: "var(--muted)", lineHeight: 1.55, marginBottom: "1.1rem" }}>
          {tour.step.body}
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end", alignItems: "center", gap: "0.5rem" }}>
          <button
            onClick={tour.prev}
            disabled={tour.stepIndex === 0}
            style={{
              fontFamily: "var(--body)",
              fontWeight: 600,
              fontSize: "0.82rem",
              color: "var(--muted)",
              background: "transparent",
              border: "none",
              padding: "0.5rem 0.6rem",
              cursor: tour.stepIndex === 0 ? "default" : "pointer",
              opacity: tour.stepIndex === 0 ? 0.35 : 1,
            }}
          >
            Back
          </button>
          <button onClick={tour.next} className="btn-dark-sm">
            {tour.stepIndex === tour.total - 1 ? "Finish" : "Next"}
          </button>
        </div>
      </div>
    </>
  );
}

export default function DashboardOverview() {
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

  const ready = !loading && !error;
  const loadedSteps = history.length > 1 ? TOUR_LOADED : TOUR_LOADED.filter((s) => s.targetId !== "tut-trend");
  const tour = useTour(noScoreYet ? TOUR_EMPTY : loadedSteps, ready);

  return (
    <div className="app-shell">
      <DashboardNav />

      <main className="content">
        <header className="topbar">
          <h1>Sector Health</h1>
          <div className="eyebrow">
            WSA Banking ETF · Nairobi Securities Exchange
            {score ? ` · reading of ${score.scored_on}` : ""}
          </div>
        </header>

        {loading && (
          <>
            <div className="kpi-row">
              {[0, 1, 2, 3].map((i) => (
                <div key={i} className="skeleton" style={{ height: 96 }} />
              ))}
            </div>
            <div className="skeleton" style={{ height: 220 }} />
          </>
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
          <section className="panel" id="tut-empty">
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

            <section className="panel" id="tut-reading">
              <div className="reading">
                <div className="reading-value">{score.score.toFixed(0)}</div>
                <div>
                  <div className="eyebrow">out of 100</div>
                  <div className={`signal-tag ${SIGNAL_CLASS[score.signal]}`}>{score.signal}</div>
                </div>
              </div>
              <div id="tut-rail">
                <ThresholdRail score={score.score} components={score.components} />
              </div>
            </section>

            <div className="grid-2">
              <section className="panel" id="tut-breakdown">
                <div className="panel-head">
                  <h2>What moved the score</h2>
                  <span className="eyebrow">weights set in scoring/weights.py</span>
                </div>
                <ComponentBreakdown components={score.components} />
              </section>

              <section className="panel" id="tut-alerts">
                <div className="panel-head">
                  <h2>Alerts</h2>
                  <span className="eyebrow">signal changes only</span>
                </div>
                <AlertFeed alerts={alerts} />
              </section>
            </div>

            {history.length > 1 && (
              <section className="panel" id="tut-trend">
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
          <section className="panel" id="tut-alerts">
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

      {ready && !tour.active && (
        <button
          onClick={tour.start}
          style={{
            position: "fixed",
            bottom: 24,
            right: 24,
            fontFamily: "var(--body)",
            fontWeight: 600,
            fontSize: "0.82rem",
            color: "var(--ground)",
            background: "var(--ink)",
            border: "none",
            padding: "0.6rem 1.1rem",
            borderRadius: 999,
            cursor: "pointer",
            boxShadow: "0 8px 20px -8px rgba(27,31,36,0.35)",
            zIndex: 70,
            transition: "transform var(--dur-micro) var(--ease)",
          }}
        >
          Take the tour
        </button>
      )}

      <TourOverlay tour={tour} />
    </div>
  );
}
