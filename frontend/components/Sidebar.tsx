/**
 * MARS is a single-page dashboard, not a multi-section app, so this isn't a
 * router — the links are anchors into the sections on this page. No item
 * points anywhere the app doesn't actually go.
 */
const SECTIONS = [
  { href: "#reading", label: "Today's reading" },
  { href: "#breakdown", label: "Component breakdown" },
  { href: "#trend", label: "Score trend" },
  { href: "#alerts", label: "Alerts" },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">M</div>
        <div>
          <div className="brand-name">MARS</div>
          <div className="brand-sub">Sector Health</div>
        </div>
      </div>

      <nav className="nav-group">
        <div className="nav-label">On this page</div>
        {SECTIONS.map((section) => (
          <a key={section.href} className="nav-item" href={section.href}>
            <span className="nav-dot" />
            {section.label}
          </a>
        ))}
      </nav>

      <p className="sidebar-footnote">
        WSA Banking ETF · Nairobi Securities Exchange. A monitoring tool, not
        investment advice.
      </p>
    </aside>
  );
}
