"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { BrandMark } from "@/components/BrandMark";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/features", label: "Features" },
  { href: "/docs", label: "Docs" },
  { href: "/about", label: "About" },
];

export function SiteNav() {
  const pathname = usePathname();

  return (
    <div className="site-nav">
      <Link href="/" className="brand-lockup">
        <BrandMark />
        <span className="brand-wordmark">MARS</span>
      </Link>

      <nav className="site-nav-links">
        {LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`site-nav-link${pathname === link.href ? " active" : ""}`}
          >
            {link.label}
          </Link>
        ))}
      </nav>

      <div className="site-nav-actions">
        <a
          href="https://github.com/cypher-30/M.A.R.S"
          className="site-nav-github"
          target="_blank"
          rel="noreferrer"
        >
          GitHub ↗
        </a>
        <Link href="/dashboard" className="btn btn-primary">
          Open the dashboard
        </Link>
      </div>
    </div>
  );
}
