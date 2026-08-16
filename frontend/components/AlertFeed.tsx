"use client";

import type { Alert } from "@/lib/types";

const LEVEL_COLOR: Record<Alert["level"], string> = {
  INFO: "var(--muted)",
  WARNING: "var(--watch)",
  CRITICAL: "var(--risk)",
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
    <div>
      {alerts.map((alert) => (
        <div className="alert-item" key={alert.id}>
          <div className="alert-stamp" style={{ color: LEVEL_COLOR[alert.level] }}>
            {new Date(alert.created_at).toLocaleDateString("en-KE", {
              day: "2-digit",
              month: "short",
            })}
          </div>
          <div>
            <p className="alert-headline">{alert.headline}</p>
            <p className="alert-body">{alert.body}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
