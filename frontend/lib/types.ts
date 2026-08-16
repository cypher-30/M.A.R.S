export type Signal = "BUY" | "HOLD" | "SELL";

export type ComponentCode = "CBR" | "CPI" | "YIELD" | "NPL" | "MOMENTUM";

export interface ComponentScore {
  code: ComponentCode;
  raw_value: number | null;
  sub_score: number;
  weight: number;
  note: string;
}

export interface SectorScore {
  scored_on: string;
  score: number;
  signal: Signal;
  components: ComponentScore[];
}

export interface Alert {
  id: number;
  level: "INFO" | "WARNING" | "CRITICAL";
  signal: Signal;
  headline: string;
  body: string;
  delivered: boolean;
  created_at: string;
}

export interface PriceBar {
  ticker: string;
  traded_on: string;
  close: number;
  volume: number | null;
}

/** Labels the reader recognises, not the codes the database stores. */
export const COMPONENT_LABELS: Record<ComponentCode, string> = {
  CBR: "Central Bank Rate",
  CPI: "Inflation",
  YIELD: "364-day T-bill yield",
  NPL: "Non-performing loans",
  MOMENTUM: "ETF price, 30 days",
};

export const COMPONENT_UNITS: Record<ComponentCode, string> = {
  CBR: "%",
  CPI: "%",
  YIELD: "%",
  NPL: "%",
  MOMENTUM: "%",
};
