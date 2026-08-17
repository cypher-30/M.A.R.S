"use client";

import { useEffect, useState } from "react";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteNav } from "@/components/SiteNav";

const STEPS = [
  {
    n: "01",
    title: "Ingest",
    body: "Central Bank Rate, CPI inflation, treasury yields, and daily NSE closes land in Postgres automatically.",
  },
  {
    n: "02",
    title: "Parse",
    body: "Quarterly bank PDFs are read by an LLM to pull NPL ratio, profit after tax, and loan book — every figure checked against the source text.",
  },
  {
    n: "03",
    title: "Score",
    body: "Each input becomes a 0–100 sub-score, weighted into one Sector Health Score. The weights live in one readable file.",
  },
  {
    n: "04",
    title: "Alert",
    body: "A change in signal triggers an email — only when the expected move clears the round-trip cost of acting on it.",
  },
];

const KPIS = [
  { value: "78", label: "Sector Health Score, out of 100" },
  { value: "+4.2", label: "Change since previous reading" },
  { value: "12 Aug", label: "Most recent reading" },
  { value: "2", label: "Alerts in the last 30 days" },
];

const TARGET_SCORE = 78;

export default function Home() {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    if (typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setDisplayScore(TARGET_SCORE);
      return;
    }
    const duration = 1400;
    const start = performance.now();
    const ease = (t: number) => 1 - Math.pow(1 - t, 4);
    let frame: number;
    const tick = (now: number) => {
      const t = Math.min((now - start) / duration, 1);
      setDisplayScore(ease(t) * TARGET_SCORE);
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, []);

  const revealed = displayScore > 75.5;

  return (
    <div className="page">
      <SiteNav />

      <div className="hero">
        <div className="hero-copy">
          <div className="eyebrow">WSA Banking ETF · Nairobi Securities Exchange</div>
          <h1>A written-down rule, designed to be trusted.</h1>
          <p>
            MARS pulls Kenyan macro data and constituent-bank results, scores the banking sector
            from 1 to 100, and alerts you when the signal changes. It replaces ad-hoc monitoring
            with a rule you can read, test, and argue with.
          </p>
          <div className="hero-actions">
            <a href="/docs" className="btn btn-primary">
              Read the docs
            </a>
            <a
              href="https://github.com/cypher-30/M.A.R.S"
              className="btn btn-secondary"
              target="_blank"
              rel="noreferrer"
            >
              View on GitHub ↗
            </a>
          </div>
        </div>

        <div className="hero-card">
          <div className="panel">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "1.4rem" }}>
              <span className="eyebrow">Sector Health Score</span>
              <span
                className="pill pill-calm"
                style={{ opacity: revealed ? 1 : 0, transition: "opacity 300ms var(--ease)" }}
              >
                BUY
              </span>
            </div>
            <div className="reading-value" style={{ marginBottom: "1.4rem" }}>
              {displayScore.toFixed(0)}
            </div>
            <div className="rail-track">
              <div
                className="rail-marker"
                style={{ left: `${Math.min(Math.max(displayScore, 0), 100)}%` }}
              />
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "var(--data)", fontSize: "0.66rem", color: "var(--muted-2)", marginTop: "0.5rem" }}>
              <span>0 · SELL</span>
              <span>35</span>
              <span>70</span>
              <span>100 · BUY</span>
            </div>
          </div>
        </div>
      </div>

      <div className="page-section">
        <div className="page-section-rule">
          <h2>How the reading gets made</h2>
          <div className="process-steps">
            {STEPS.map((step) => (
              <div className="process-step" key={step.n}>
                <div className="process-step-n">{step.n}</div>
                <div className="process-step-title">{step.title}</div>
                <div className="process-step-body">{step.body}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="page-section">
        <div className="page-section-rule">
          <h2>What you actually see</h2>
          <p className="section-lede">
            One dashboard. Today&apos;s score, what moved it, and the alert history — the real
            screen, not a mockup.
          </p>
          <div className="preview-panel">
            {KPIS.map((kpi) => (
              <div className="preview-tile" key={kpi.label}>
                <div className="preview-tile-value">{kpi.value}</div>
                <div className="preview-tile-label">{kpi.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="closing-cta">
        <div className="closing-cta-inner">
          <div>
            <h2>Self-hosted, fully yours.</h2>
            <p>
              MARS is open source. Clone it, point it at your own data sources, and run it on your
              own schedule.
            </p>
          </div>
          <a
            href="https://github.com/cypher-30/M.A.R.S"
            className="btn btn-on-dark"
            target="_blank"
            rel="noreferrer"
          >
            View on GitHub ↗
          </a>
        </div>
      </div>

      <SiteFooter />
    </div>
  );
}
