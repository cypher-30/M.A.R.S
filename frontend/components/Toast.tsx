"use client";

export function Toast({ title, body, visible }: { title: string; body: string; visible: boolean }) {
  return (
    <div
      className="toast"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(10px)",
        pointerEvents: "none",
      }}
    >
      <div className="toast-title">{title}</div>
      <div className="toast-body">{body}</div>
    </div>
  );
}
