import type { Metadata } from "next";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteNav } from "@/components/SiteNav";

export const metadata: Metadata = {
  title: "Docs — MARS",
  description: "Run it yourself, in about ten minutes.",
};

const STEPS = [
  { n: "1", title: "Database", code: "docker compose up -d db" },
  {
    n: "2",
    title: "Backend",
    code: "cd backend\npython -m venv .venv && source .venv/bin/activate\npip install -r requirements.txt\ncp .env.example .env\nalembic upgrade head\nuvicorn app.main:app --reload",
  },
  {
    n: "3",
    title: "Frontend",
    code: "cd frontend\nnpm install\ncp .env.local.example .env.local\nnpm run dev",
  },
  { n: "4", title: "See it working, no API keys", code: "cd backend && python -m app.cli seed" },
];

const GUIDES = [
  {
    title: "What this does",
    desc: "A plain-English explanation of the problem and the four inputs, no jargon.",
    file: "docs/what-this-does.md",
    href: "https://github.com/cypher-30/M.A.R.S/blob/master/docs/what-this-does.md",
  },
  {
    title: "Architecture",
    desc: "How ingestion, parsing, scoring, and alerting fit together.",
    file: "docs/architecture.md",
    href: "https://github.com/cypher-30/M.A.R.S/blob/master/docs/architecture.md",
  },
  {
    title: "Build order",
    desc: "The step-by-step plan the system was built in.",
    file: "docs/build-order.md",
    href: "https://github.com/cypher-30/M.A.R.S/blob/master/docs/build-order.md",
  },
  {
    title: "Scoring notes",
    desc: "A running log of weight and threshold decisions, and why they changed.",
    file: "docs/scoring-notes.md",
    href: "https://github.com/cypher-30/M.A.R.S/blob/master/docs/scoring-notes.md",
  },
];

const CLI = [
  { cmd: "python -m app.cli macro", desc: "Refresh CBR, CPI, and treasury yields." },
  { cmd: "python -m app.cli score", desc: "Recalculate today's score, alert if the signal changed." },
  { cmd: "python -m app.cli reports", desc: "Look for new quarterly bank filings." },
  { cmd: "python -m app.cli parse report.pdf KCB 2026Q1", desc: "Parse one downloaded bank report." },
  { cmd: "python -m app.cli seed", desc: "Fill the database with 180 days of demo data." },
  { cmd: "python -m app.cli backtest", desc: "Replay history through the current weights." },
];

const CONFIG = [
  { key: "DATABASE_URL", desc: "Postgres connection string." },
  { key: "MYSTOCKS_API_KEY", desc: "Price data for the ETF and constituents." },
  { key: "LLM_PROVIDER / OPENAI_API_KEY / GEMINI_API_KEY", desc: "The document parser." },
  { key: "SMTP_* / ALERT_EMAIL_TO", desc: "Where alerts are delivered." },
  { key: "BROKERAGE_EXIT_FEE_PCT", desc: "Your all-in exit cost — check your broker's schedule." },
];

export default function Docs() {
  return (
    <div className="page">
      <SiteNav />

      <div className="page-section" style={{ paddingTop: "5rem", paddingBottom: "1.25rem" }}>
        <div className="eyebrow">Documentation</div>
        <h1 style={{ fontSize: "2.4rem", margin: "1rem 0", maxWidth: 640 }}>
          Run it yourself, in about ten minutes.
        </h1>
        <p style={{ fontSize: "1rem", lineHeight: 1.6, color: "#454b54", maxWidth: 600, margin: 0 }}>
          Prerequisites: Python 3.11+, Node 20+, Docker (or a local Postgres 16).
        </p>
      </div>

      <div className="page-section" style={{ paddingBottom: "3.5rem" }}>
        <h2 style={{ fontSize: "1.4rem", marginBottom: "1.1rem" }}>Quick start</h2>
        <div className="docs-steps">
          {STEPS.map((step) => (
            <div className="docs-step" key={step.n}>
              <div className="docs-step-label">
                {step.n} · {step.title}
              </div>
              <pre>{step.code}</pre>
            </div>
          ))}
        </div>
      </div>

      <div className="page-section" style={{ paddingBottom: "3.5rem" }}>
        <h2 style={{ fontSize: "1.4rem", marginBottom: "1.1rem" }}>Guides</h2>
        <div className="docs-guides">
          {GUIDES.map((guide) => (
            <a href={guide.href} className="docs-guide-card" key={guide.file} target="_blank" rel="noreferrer">
              <div className="docs-guide-title">{guide.title}</div>
              <div className="docs-guide-desc">{guide.desc}</div>
              <div className="docs-guide-file">{guide.file} ↗</div>
            </a>
          ))}
        </div>
      </div>

      <div className="page-section" style={{ paddingBottom: "3.5rem" }}>
        <h2 style={{ fontSize: "1.4rem", marginBottom: "1.1rem" }}>CLI reference</h2>
        <div className="docs-table">
          {CLI.map((row) => (
            <div className="docs-table-row" key={row.cmd}>
              <code className="docs-table-key">{row.cmd}</code>
              <span className="docs-table-desc">{row.desc}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="page-section">
        <h2 style={{ fontSize: "1.4rem", marginBottom: "1.1rem" }}>Configuration</h2>
        <div className="docs-table">
          {CONFIG.map((row) => (
            <div className="docs-table-row" key={row.key}>
              <code className="docs-table-key">{row.key}</code>
              <span className="docs-table-desc">{row.desc}</span>
            </div>
          ))}
        </div>
        <p style={{ fontSize: "0.82rem", color: "var(--muted-2)", marginTop: "1rem" }}>
          Full list in{" "}
          <a
            href="https://github.com/cypher-30/M.A.R.S/blob/master/backend/.env.example"
            target="_blank"
            rel="noreferrer"
          >
            backend/.env.example ↗
          </a>
          .
        </p>
      </div>

      <SiteFooter />
    </div>
  );
}
