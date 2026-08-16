import type { ReactNode } from "react";

const TONE_CLASS = { calm: "pill-calm", watch: "pill-watch", risk: "pill-risk", muted: "pill-muted" } as const;

export function KpiCard({
  icon,
  iconTone = "muted",
  value,
  label,
  pill,
  pillTone = "muted",
}: {
  icon: ReactNode;
  iconTone?: keyof typeof TONE_CLASS;
  value: ReactNode;
  label: string;
  pill?: string;
  pillTone?: keyof typeof TONE_CLASS;
}) {
  return (
    <div className="kpi-card">
      <div className="kpi-top">
        <div className={`kpi-icon ${TONE_CLASS[iconTone]}`}>{icon}</div>
        {pill ? <span className={`pill ${TONE_CLASS[pillTone]}`}>{pill}</span> : null}
      </div>
      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>
    </div>
  );
}
