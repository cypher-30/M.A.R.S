import Link from "next/link";

import { BrandMark } from "@/components/BrandMark";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner">
        <div className="site-footer-top">
          <div className="site-footer-brand">
            <Link href="/" className="site-footer-lockup">
              <BrandMark size={22} ring="#8FB0DE" body="#F7F8F9" />
              <span className="brand-wordmark">MARS</span>
            </Link>
            <p className="site-footer-tagline">
              A daily risk reading for the WSA Banking ETF on the Nairobi Securities Exchange.
              Open source, self-hosted.
            </p>
          </div>

          <div className="site-footer-col">
            <div className="site-footer-col-title">Product</div>
            <div className="site-footer-links">
              <Link href="/features">Features</Link>
              <Link href="/docs">Docs</Link>
              <Link href="/dashboard">Dashboard</Link>
            </div>
          </div>

          <div className="site-footer-col">
            <div className="site-footer-col-title">Company</div>
            <div className="site-footer-links">
              <Link href="/about">About</Link>
              <a href="https://github.com/cypher-30/M.A.R.S" target="_blank" rel="noreferrer">
                GitHub
              </a>
            </div>
          </div>

          <div className="site-footer-col">
            <div className="site-footer-col-title">Legal</div>
            <div className="site-footer-links">
              <Link href="/privacy">Privacy</Link>
              <Link href="/terms">Terms</Link>
            </div>
          </div>
        </div>

        <div className="site-footer-bottom">
          <span>© 2026 MARS — MIT licensed, source on GitHub.</span>
          <span>A monitoring tool, not investment advice.</span>
        </div>
      </div>
    </footer>
  );
}
