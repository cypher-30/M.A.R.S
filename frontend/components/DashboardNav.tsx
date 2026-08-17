"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { BrandMark } from "@/components/BrandMark";

const LINKS = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/review", label: "Review queue" },
  { href: "/dashboard/settings", label: "Settings" },
];

export function DashboardNav() {
  const pathname = usePathname();

  return (
    <div className="dashboard-nav">
      <div className="dashboard-nav-left">
        <Link href="/" className="brand-lockup">
          <BrandMark />
          <span className="brand-wordmark">MARS</span>
        </Link>

        <nav className="dashboard-nav-links">
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
      </div>

      <Link href="/" className="site-nav-github">
        ← Back to site
      </Link>
    </div>
  );
}
