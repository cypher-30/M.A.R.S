"use client";

import { useRef, useState } from "react";

import { DashboardNav } from "@/components/DashboardNav";
import { Toast } from "@/components/Toast";

type ReviewItem = {
  id: string;
  bank: string;
  quarter: string;
  field: string;
  value: string;
  page: number;
  snippet: string;
  extractedAt: string;
};

const SEED_ITEMS: ReviewItem[] = [
  {
    id: "kcb-npl",
    bank: "KCB Group",
    quarter: "2026 Q1",
    field: "Non-performing loans ratio",
    value: "13.2%",
    page: 42,
    snippet:
      "Gross non-performing loans stood at 13.2% of the total loan book, down from 14.6% in the prior quarter.",
    extractedAt: "2 hours ago",
  },
  {
    id: "equity-pat",
    bank: "Equity Group",
    quarter: "2026 Q1",
    field: "Profit after tax",
    value: "KES 18.4B",
    page: 12,
    snippet: "The Group recorded a profit after tax of KES 18.4 billion for the quarter ended 31 March 2026.",
    extractedAt: "2 hours ago",
  },
  {
    id: "coop-loans",
    bank: "Co-operative Bank",
    quarter: "2026 Q1",
    field: "Loan book",
    value: "KES 341B",
    page: 8,
    snippet: "Net loans and advances to customers grew to KES 341 billion, a 6.1% increase year on year.",
    extractedAt: "5 hours ago",
  },
  {
    id: "absa-npl",
    bank: "Absa Kenya",
    quarter: "2026 Q1",
    field: "Non-performing loans ratio",
    value: "10.8%",
    page: 37,
    snippet: "The NPL ratio improved to 10.8%, reflecting continued recoveries in the corporate banking segment.",
    extractedAt: "1 day ago",
  },
];

export default function ReviewQueue() {
  const [items, setItems] = useState(SEED_ITEMS);
  const [toast, setToast] = useState<{ title: string; body: string } | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  function resolve(id: string, kind: "confirmed" | "flagged") {
    const item = items.find((i) => i.id === id);
    setItems((prev) => prev.filter((i) => i.id !== id));
    if (item) {
      setToast(
        kind === "confirmed"
          ? { title: "Figure confirmed", body: `${item.bank} · ${item.field} now counts toward the score.` }
          : { title: "Flagged as wrong", body: `${item.bank} · ${item.field} held back pending re-extraction.` },
      );
      clearTimeout(toastTimer.current);
      toastTimer.current = setTimeout(() => setToast(null), 3000);
    }
  }

  return (
    <div className="app-shell">
      <DashboardNav />

      <main className="content" style={{ maxWidth: 900 }}>
        <h1 style={{ fontSize: "1.875rem", marginBottom: "0.5rem" }}>Review queue</h1>
        <p style={{ fontSize: "0.9rem", color: "var(--muted)", lineHeight: 1.6, marginBottom: "2rem", maxWidth: 600 }}>
          Every figure the PDF parser extracts is held here with{" "}
          <code style={{ fontFamily: "var(--data)", background: "var(--rule-soft)", padding: "0.1rem 0.3rem", borderRadius: 4, fontSize: "0.85em" }}>
            needs_review=True
          </code>{" "}
          until a human confirms it against the source text. Nothing reaches the score unconfirmed.
        </p>

        {items.length === 0 ? (
          <div className="state" style={{ textAlign: "center", borderStyle: "dashed" }}>
            <strong>Nothing needs review right now</strong>
            <div style={{ fontSize: "0.85rem" }}>
              New figures appear here after the next{" "}
              <code>python -m app.cli reports</code> run finds a filing.
            </div>
          </div>
        ) : (
          <div className="review-list">
            {items.map((item) => (
              <div className="review-card" key={item.id}>
                <div className="review-card-head">
                  <div>
                    <div className="review-card-title">
                      {item.bank} · {item.quarter}
                    </div>
                    <div className="review-card-field">{item.field}</div>
                  </div>
                  <div className="review-card-value">{item.value}</div>
                </div>
                <div className="review-snippet">
                  <div className="review-snippet-label">Source text, page {item.page}</div>
                  <div className="review-snippet-text">&quot;{item.snippet}&quot;</div>
                </div>
                <div className="review-card-foot">
                  <span className="review-stamp">extracted {item.extractedAt}</span>
                  <div className="review-actions">
                    <button className="btn-text-risk" onClick={() => resolve(item.id, "flagged")}>
                      Flag as wrong
                    </button>
                    <button className="btn-dark-sm" onClick={() => resolve(item.id, "confirmed")}>
                      Confirm figure
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <Toast title={toast?.title ?? ""} body={toast?.body ?? ""} visible={!!toast} />
    </div>
  );
}
