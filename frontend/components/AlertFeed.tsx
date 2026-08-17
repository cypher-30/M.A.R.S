"use client";

import type { Alert } from "@/lib/types";

const SIGNAL_COLOR: Record<Alert["signal"], string> = {
  BUY: "var(--calm)",
  HOLD: "var(--watch)",
  SELL: "var(--risk)",
};

export function AlertFeed({ alerts }: { alerts: Alert[] }) {
  if (alerts.length === 0) {
    return (
      <div className="state">
        <strong>No alerts yet</strong>
        Alerts appear here when the signal changes. Nothing has crossed a threshold since the
        system started watching.
      </div>
    );
  }

  return (
    <div className="alert-list">
      {alerts.map((alert) => (
        <div className="alert-item" key={alert.id}>
          <div className="alert-stamp">
            {new Date(alert.created_at).toLocaleDateString("en-KE", {
              day: "2-digit",
              month: "short",
              year: "numeric",
            })}
            {" · "}
            <span className="alert-signal" style={{ color: SIGNAL_COLOR[alert.signal] }}>
              {alert.signal}
            </span>
          </div>
          <p className="alert-headline">{alert.headline}</p>
          <p className="alert-body">{alert.body}</p>
        </div>
      ))}
    </div>
  );
}
