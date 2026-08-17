import type { Metadata } from "next";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteNav } from "@/components/SiteNav";

export const metadata: Metadata = {
  title: "Terms — MARS",
  description: "MARS is open source software distributed under the MIT License.",
};

export default function Terms() {
  return (
    <div className="page">
      <SiteNav />

      <div className="prose-page narrow">
        <div className="eyebrow">Legal</div>
        <h1 style={{ fontSize: "2rem" }}>Terms</h1>

        <h2>License</h2>
        <p>
          MARS is open source software distributed under the MIT License. You may use, modify,
          and self-host it freely, including commercially, subject to that license&apos;s terms.
        </p>

        <h2>No warranty</h2>
        <p>
          The software is provided &quot;as is,&quot; without warranty of any kind. The
          maintainers are not liable for losses arising from its use, including errors in data
          ingestion, PDF extraction, or scoring.
        </p>

        <h2>Not investment advice</h2>
        <p>
          The Sector Health Score describes conditions; it does not predict prices and is not a
          recommendation to buy, hold, or sell any security. Treat a SELL signal as a prompt to
          look, not an instruction to act. Any decision you make based on MARS&apos;s output is
          your own.
        </p>

        <h2>Your deployment</h2>
        <p>
          You are responsible for the infrastructure you run MARS on, any API keys or costs you
          incur with third-party data or LLM providers, and compliance with those providers&apos;
          own terms of service.
        </p>

        <h2>Changes</h2>
        <p style={{ marginBottom: 0 }}>
          These terms may be updated as the project evolves. The current version always lives on{" "}
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
