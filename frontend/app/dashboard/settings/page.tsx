"use client";

import { useRef, useState } from "react";

import { DashboardNav } from "@/components/DashboardNav";
import { Toast } from "@/components/Toast";

const WEIGHTS = [
  { name: "Non-performing loans", pct: "30%" },
  { name: "Central Bank Rate", pct: "20%" },
  { name: "Inflation (CPI)", pct: "20%" },
  { name: "364-day T-bill yield", pct: "15%" },
  { name: "ETF price momentum", pct: "15%" },
];

export default function Settings() {
  const [email, setEmail] = useState("risk-desk@yourfund.co.ke");
  const [alertOnChange, setAlertOnChange] = useState(true);
  const [exitFee, setExitFee] = useState("4.0");
  const [schedulerOn, setSchedulerOn] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  function save() {
    setShowToast(true);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setShowToast(false), 3000);
  }

  return (
    <div className="app-shell">
      <DashboardNav />

      <main className="content" style={{ maxWidth: 760 }}>
        <h1 style={{ fontSize: "1.875rem", marginBottom: "2rem" }}>Settings</h1>

        <div className="settings-card">
          <h2>Alerts</h2>
          <p className="settings-card-hint">
            Emailed only when the signal changes — never a daily &quot;still fine.&quot;
          </p>
          <label className="field-label" htmlFor="alert-email">
            Alert email
          </label>
          <input
            id="alert-email"
            type="text"
            className="field-input"
            style={{ marginBottom: "1rem" }}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <label className="field-checkbox-row">
            <input type="checkbox" checked={alertOnChange} onChange={(e) => setAlertOnChange(e.target.checked)} />
            Email me when the signal changes
          </label>
        </div>

        <div className="settings-card">
          <h2>Exit cost</h2>
          <p className="settings-card-hint">
            A SELL only fires when the expected loss clears the round-trip cost of exiting.
          </p>
          <label className="field-label" htmlFor="exit-fee">
            Brokerage exit fee
          </label>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", maxWidth: 160 }}>
            <input
              id="exit-fee"
              type="text"
              className="field-input field-input-mono"
              value={exitFee}
              onChange={(e) => setExitFee(e.target.value)}
            />
            <span style={{ fontFamily: "var(--data)", fontSize: "0.85rem", color: "var(--muted-2)" }}>%</span>
          </div>
        </div>

        <div className="settings-card">
          <div className="settings-card-head">
            <h2>Scheduler</h2>
            <span className="pill pill-watch">{schedulerOn ? "Running" : "Paused"}</span>
          </div>
          <p className="settings-card-hint">Starts paused until your connectors return real data.</p>
          <label className="field-checkbox-row">
            <input type="checkbox" checked={schedulerOn} onChange={(e) => setSchedulerOn(e.target.checked)} />
            Run macro, score, and report jobs on schedule
          </label>
        </div>

        <div className="settings-card" style={{ marginBottom: "1.75rem" }}>
          <h2>Scoring weights</h2>
          <p className="settings-card-hint">
            Read-only here — edit{" "}
            <code style={{ fontFamily: "var(--data)", background: "var(--rule-soft)", padding: "0.1rem 0.3rem", borderRadius: 4 }}>
              backend/app/scoring/weights.py
            </code>{" "}
            and redeploy to change these.
          </p>
          {WEIGHTS.map((w) => (
            <div className="settings-weight-row" key={w.name}>
              <span>{w.name}</span>
              <span>{w.pct}</span>
            </div>
          ))}
        </div>

        <div className="settings-foot">
          <span className="settings-foot-hint">Changes apply on the next scheduled run.</span>
          <button className="btn btn-primary" onClick={save}>
            Save changes
          </button>
        </div>
      </main>

      <Toast title="Settings saved" body="Applied on the next scheduled run." visible={showToast} />
    </div>
  );
}
