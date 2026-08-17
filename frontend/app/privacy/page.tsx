import type { Metadata } from "next";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteNav } from "@/components/SiteNav";

export const metadata: Metadata = {
  title: "Privacy — MARS",
  description: "MARS is self-hosted software. There is no MARS server collecting your data.",
};

export default function Privacy() {
  return (
    <div className="page">
      <SiteNav />

      <div className="prose-page narrow">
        <div className="eyebrow">Legal</div>
        <h1 style={{ fontSize: "2rem" }}>Privacy</h1>

        <p>
          MARS is self-hosted software. You run it on your own infrastructure, so the maintainers
          never see your data — there is no MARS server collecting it.
        </p>

        <h2>What your own instance processes</h2>
        <p>
          Public macroeconomic data (Central Bank Rate, CPI, treasury yields), NSE price data via
          your configured provider, and the bank PDF reports you feed it. All of it lives in the
          Postgres database you run — never sent anywhere by us.
        </p>

        <h2>This website</h2>
        <p>
          The marketing and documentation pages you&apos;re reading now don&apos;t use tracking
          cookies or analytics. Links to GitHub are subject to GitHub&apos;s own privacy policy.
        </p>

        <h2>Third-party services</h2>
        <p>
          If you configure an LLM provider (OpenAI or Gemini) for PDF parsing, or a price data
          API, the report text or tickers you send are subject to that provider&apos;s own terms —
          MARS just calls the API you point it at.
        </p>

        <h2>Questions</h2>
        <p style={{ marginBottom: 0 }}>
          Open an issue on{" "}
          <a href="https://github.com/cypher-30/M.A.R.S" target="_blank" rel="noreferrer">
            the GitHub repository ↗
          </a>
          .
        </p>
      </div>

      <SiteFooter />
    </div>
  );
}
