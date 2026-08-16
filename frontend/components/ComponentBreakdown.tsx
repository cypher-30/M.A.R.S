"use client";

import { COMPONENT_LABELS, COMPONENT_UNITS, type ComponentScore } from "@/lib/types";

function tone(subScore: number): "risk" | "watch" | "calm" {
  if (subScore < 35) return "risk";
  if (subScore < 70) return "watch";
  return "calm";
}

const TONE_VAR = { calm: "var(--calm)", watch: "var(--watch)", risk: "var(--risk)" } as const;
const TONE_SOFT_VAR = {
  calm: "var(--calm-soft)",
  watch: "var(--watch-soft)",
  risk: "var(--risk-soft)",
} as const;

/** Every input, its reading, how healthy that reading is, and how much it counts. */
export function ComponentBreakdown({ components }: { components: ComponentScore[] }) {
  return (
    <div className="component-list">
      {components.map((component) => {
        const t = tone(component.sub_score);
        return (
          <div className="component-row" key={component.code}>
            <div
              className="component-chip"
              style={{ background: TONE_SOFT_VAR[t], color: TONE_VAR[t] }}
            >
              {component.code.slice(0, 3)}
            </div>

            <div className="component-main">
              <div className="component-name">{COMPONENT_LABELS[component.code]}</div>
              <div className="component-meta">
                <span>
                  {component.raw_value === null
                    ? "no fresh data"
                    : `${component.raw_value.toFixed(1)}${COMPONENT_UNITS[component.code]}`}
                </span>
                <span>·</span>
                <span>sub-score {component.sub_score.toFixed(0)}</span>
              </div>
              {component.note ? <div className="component-stale">{component.note}</div> : null}
            </div>

            <div className="component-bar-wrap">
              <div className="component-bar-track">
                <span
                  className="component-bar-fill"
                  style={{
                    width: `${Math.min(Math.max(component.sub_score, 0), 100)}%`,
                    background: TONE_VAR[t],
                  }}
                />
              </div>
            </div>

            <div className="component-weight">{(component.weight * 100).toFixed(0)}%</div>
          </div>
        );
      })}
    </div>
  );
}
