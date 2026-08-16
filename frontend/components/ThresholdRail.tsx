"use client";

import { COMPONENT_LABELS, type ComponentScore } from "@/lib/types";

const SELL_BELOW = 35;
const BUY_ABOVE = 70;

/**
 * The signature element: one 0-100 rail carrying the composite score, the two
 * thresholds that trigger a signal, and a notch for every component so you can
 * see which input is pulling the score. Shows the decision, not just a number.
 */
export function ThresholdRail({
  score,
  components,
}: {
  score: number;
  components: ComponentScore[];
}) {
  return (
    <div className="rail">
      <div className="rail-track">
        <div className="rail-gate" style={{ left: `${SELL_BELOW}%` }}>
          <span>Sell below {SELL_BELOW}</span>
        </div>
        <div className="rail-gate" style={{ left: `${BUY_ABOVE}%` }}>
          <span>Buy above {BUY_ABOVE}</span>
        </div>
        <div
          className="rail-marker"
          style={{ left: `${Math.min(Math.max(score, 0), 100)}%` }}
          role="img"
          aria-label={`Sector health score ${score} out of 100`}
        />
      </div>

      <div className="rail-notches">
        {components.map((component) => (
          <div
            key={component.code}
            className="rail-notch"
            style={{ left: `${Math.min(Math.max(component.sub_score, 0), 100)}%` }}
            title={`${COMPONENT_LABELS[component.code]} — ${component.sub_score}`}
          >
            <i />
            <b>{component.code}</b>
          </div>
        ))}
      </div>
    </div>
  );
}
