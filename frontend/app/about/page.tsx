import type { Metadata } from "next";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteNav } from "@/components/SiteNav";

export const metadata: Metadata = {
  title: "About — MARS",
  description: "A rule you can inspect and argue with.",
};

export default function About() {
  return (
    <div className="page">
      <SiteNav />

      <div className="prose-page">
        <div className="eyebrow">About</div>
        <h1>A rule you can inspect and argue with.</h1>

        <p className="lede">
          If you&apos;re putting money into a fund that tracks Kenyan bank shares, whether
          that&apos;s a good place for it depends on things that change slowly and quietly —
          interest rates, inflation, how many loans people are failing to repay. Checking all of
          that by hand is tedious, so most people don&apos;t. Then something goes wrong, they
          panic, and they sell at the worst possible moment.
        </p>
        <p style={{ marginBottom: "3rem" }}>
          MARS does that checking every day, without getting emotional, and writes down exactly
          why it says what it says.
        </p>

        <h2 className="display">What it is, and isn&apos;t</h2>
        <p>
          The score is a written-down opinion, not a prediction. It reflects a set of weights that
          are starting guesses until they&apos;re backtested against history — someone else could
          weight non-performing loans at 20% instead of 30% and get a different answer. The point
          isn&apos;t that the numbers are objectively correct. It&apos;s that they&apos;re fixed
          in advance, so you can&apos;t talk yourself into a different one on a bad day.
        </p>
        <p style={{ marginBottom: "3rem" }}>
          The PDF parser can misread a filing, which is why every figure it extracts is held for a
          human to confirm before it&apos;s allowed to move the score. This is a monitoring tool.
          It is not investment advice.
        </p>

        <h2 className="display">Open source</h2>
        <p style={{ marginBottom: "1.75rem" }}>
          MARS is built in the open and licensed under MIT. Read the code, change the weights,
          point it at a different exchange — nothing about how it decides is hidden behind an API.
        </p>
        <a
          href="https://github.com/cypher-30/M.A.R.S"
          className="btn btn-primary"
          target="_blank"
          rel="noreferrer"
        >
          View the source on GitHub ↗
        </a>
      </div>

      <SiteFooter />
    </div>
  );
}
