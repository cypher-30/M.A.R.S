"use client";

import { COMPONENT_LABELS, COMPONENT_UNITS, type ComponentScore } from "@/lib/types";

function barColor(subScore: number): string {
  if (subScore < 35) return "var(--risk)";
  if (subScore < 70) return "var(--watch)";
  return "var(--calm)";
}

/** Every input, its reading, how healthy that reading is, and how much it counts. */
export function ComponentBreakdown({ components }: { components: ComponentScore[] }) {
  return (
    <table className="components">
      <thead>
        <tr>
          <th>Input</th>
          <th className="num">Reading</th>
          <th className="bar-cell">Health</th>
          <th className="num">Sub-score</th>
          <th className="num">Weight</th>
        </tr>
      </thead>
      <tbody>
        {components.map((component) => (
          <tr key={component.code}>
            <td>
              {COMPONENT_LABELS[component.code]}
              {component.note ? <div className="stale">{component.note}</div> : null}
            </td>
            <td className="num">
              {component.raw_value === null
                ? "—"
                : `${component.raw_value.toFixed(1)}${COMPONENT_UNITS[component.code]}`}
            </td>
            <td className="bar-cell">
              <span
                className="bar"
                style={{
                  width: `${Math.min(Math.max(component.sub_score, 0), 100)}%`,
                  background: barColor(component.sub_score),
                }}
              />
            </td>
            <td className="num">{component.sub_score.toFixed(0)}</td>
            <td className="num">{(component.weight * 100).toFixed(0)}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
