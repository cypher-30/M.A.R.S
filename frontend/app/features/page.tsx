import type { Metadata } from "next";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteNav } from "@/components/SiteNav";

export const metadata: Metadata = {
  title: "Features — MARS",
  description: "Five stages, one score, no black box.",
};

const INGEST_ROWS = [
  { label: "Central Bank Rate", value: "12.50%" },
  { label: "CPI inflation", value: "6.10%" },
  { label: "364-day T-bill yield", value: "16.80%" },
  { label: "WSA ETF close", value: "KES 148.20" },
];

const SCORE_ROWS = [
  { name: "Non-performing loans", sub: 58, color: "var(--watch)" },
  { name: "Central Bank Rate", sub: 68, color: "var(--calm)" },
  { name: "ETF price momentum", sub: 81, color: "var(--calm)" },
];

export default function Features() {
  return (
    <div className="page">
      <SiteNav />

      <div className="page-section" style={{ paddingTop: "5rem", paddingBottom: "1.5rem" }}>
        <div className="eyebrow">Features</div>
        <h1 style={{ fontSize: "2.6rem", lineHeight: 1.15, margin: "1rem 0", maxWidth: 680 }}>
          Five stages, one score, no black box.
        </h1>
        <p style={{ fontSize: "1.03rem", lineHeight: 1.6, color: "#454b54", maxWidth: 600, margin: 0 }}>
          Every number that reaches the dashboard passed through the same pipeline — nothing
          hand-adjusted after the fact.
        </p>
      </div>

      <div className="page-section" style={{ display: "flex", flexDirection: "column", gap: "5.5rem", paddingTop: "1.5rem" }}>
        <div className="feature-row">
          <div className="feature-copy">
            <div className="process-step-n">01 · Ingest</div>
            <h2>The raw numbers, landed automatically</h2>
            <p>
              The Central Bank Rate, CPI inflation, treasury yields, and daily NSE closes land in
              Postgres on a schedule — no spreadsheet, no manual pull.
            </p>
          </div>
          <div className="feature-figure">
            {INGEST_ROWS.map((row) => (
              <div className="feature-figure-row" key={row.label}>
                <span>{row.label}</span>
                <span>{row.value}</span>
              </div>
            ))}
            <div style={{ fontFamily: "var(--data)", fontSize: "0.69rem", color: "#a3abb4", marginTop: "0.6rem" }}>
              updated 06:00 EAT
            </div>
          </div>
        </div>

        <div className="feature-row reverse">
          <div className="feature-figure">
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.6rem" }}>
              <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>KCB Group · 2026 Q1</span>
              <span style={{ fontFamily: "var(--data)", fontSize: "1.25rem", fontWeight: 500 }}>13.2%</span>
            </div>
            <div className="feature-quote">
              &quot;Gross non-performing loans stood at 13.2% of the total loan book...&quot;
            </div>
          </div>
          <div className="feature-copy">
            <div className="process-step-n">02 · Parse</div>
            <h2>Bank PDFs, read and checked</h2>
            <p>
              Quarterly bank reports are long, inconsistent PDFs. An LLM extracts NPL ratio,
              profit after tax, and loan book from each one — and every figure is held for
              confirmation against the source text before it counts.
            </p>
          </div>
        </div>

        <div className="feature-row">
          <div className="feature-copy">
            <div className="process-step-n">03 · Score</div>
            <h2>Weighted, not averaged</h2>
            <p>
              Each input becomes a 0–100 sub-score. Non-performing loans count for the most,
              because it measures damage that already happened rather than damage that might. The
              weights are one readable file, not a hidden model.
            </p>
          </div>
          <div className="feature-figure">
            {SCORE_ROWS.map((row) => (
              <div className="feature-bar-row" key={row.name}>
                <div className="feature-bar-head">
                  <span>{row.name}</span>
                  <span style={{ fontFamily: "var(--data)", color: "var(--muted)" }}>{row.sub}</span>
                </div>
                <div className="feature-bar-track">
                  <div className="feature-bar-fill" style={{ width: `${row.sub}%`, background: row.color }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="feature-row reverse">
          <div className="feature-figure">
            <div className="eyebrow" style={{ marginBottom: "0.3rem" }}>
              02 Aug 2026 · <span style={{ color: "var(--calm)", fontWeight: 600 }}>BUY</span>
            </div>
            <div style={{ fontWeight: 600, fontSize: "0.92rem", marginBottom: "0.25rem" }}>
              Signal moved HOLD → BUY
            </div>
            <div style={{ fontSize: "0.83rem", color: "var(--muted)", lineHeight: 1.5 }}>
              NPL and momentum both cleared their thresholds after Q2 filings.
            </div>
          </div>
          <div className="feature-copy">
            <div className="process-step-n">04 · Alert</div>
            <h2>Quiet until it isn&apos;t</h2>
            <p>
              You&apos;re emailed only when the signal changes — never a daily &quot;still
              fine.&quot; And before it ever calls for a sell, it checks that the expected loss
              clears the round-trip cost of exiting, so small dips don&apos;t trigger noise
              you&apos;ll learn to ignore.
            </p>
          </div>
        </div>

        <div className="feature-row">
          <div className="feature-copy">
            <div className="process-step-n">05 · Display</div>
            <h2>One dashboard, nothing extra</h2>
            <p>
              Today&apos;s reading, what moved it, the 90-day trend, and the alert history. The
              actual screen you&apos;d run this from — no separate marketing mockup.
            </p>
          </div>
          <div className="feature-figure">
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.9rem" }}>
              <span className="eyebrow">Sector Health</span>
              <span className="pill pill-calm">BUY</span>
            </div>
            <div style={{ fontFamily: "var(--data)", fontSize: "2rem", fontWeight: 500, marginBottom: "0.8rem" }}>
              78
            </div>
            <div className="rail-track" style={{ height: 8 }}>
              <div className="rail-marker" style={{ left: "78%" }} />
            </div>
          </div>
        </div>
      </div>

      <SiteFooter />
    </div>
  );
}
