# MARS design system — persistent rules

Source: approved design export (`M.A.R.S Banking Risk Platform.zip`, design.claude.com project
`cypher-30/M.A.R.S`, synced 2026-08-17). The `.dc.html` mockups themselves are throwaway preview
files, not implementation — this document is the durable record of what they specify, kept in the
repo so it survives past the session that unzipped them.

## Brand
- Logo: Concept G "The Orbit" — a ring with a single body on it, circling a fixed center. Used in
  Site Nav, Site Footer, and Dashboard Nav. SVG: circle r=22 stroke (ring), circle r=6 at top
  (orbiting body), circle r=4 at center (fixed point).
- Wordmark: Libre Caslon Display, "MARS" / "M.A.R.S." used contextually.
- Colors (hex, no green/teal as brand colors):
  - Primary · Cobalt: 50 #EEF3FB 100 #DCE7F6 200 #B9CFEC 300 #8FB0DE 400 #5F8CCB 500 #3E6BAF 600 #2F548C 700 #274571 800 #20385B 900 #1A2C48 950 #101B2E
  - Secondary · Plum: 50 #FAF1F6 100 #F3E0EC 200 #E4BFD8 300 #D096BF 400 #B96FA1 500 #9E4F85 600 #7F3E6B 700 #653255 800 #4F2843 900 #3B1E33 950 #251320
  - Accent · Ochre: 50 #FBF6EC 100 #F5EAD1 200 #E9D19E 300 #DAB56A 400 #C99940 500 #B37F2A 600 #92671F 700 #75521A 800 #5B4016 900 #453110 950 #2C1F0A
  - Neutral: 50 #F7F8F9 100 #EEF0F2 200 #DFE3E7 300 #C7CDD3 400 #A3ABB4 500 #7C848F 600 #5E6670 700 #454B54 800 #2E333A 900 #1B1F24 950 #101317
  - Semantic: success #2E7D5B / soft #E3F1EA · warning #B8872E / soft #F6ECD8 · error #B23B3B / soft #F6DEDD · info #3B7EA1 / soft #DDEEF5
  - Dark mode tokens exist (bg #101317, surface #181C21, border #262B31, text primary #F2F4F5, text muted #9AA2AA) but no shipped mockup uses them — not implemented as a toggle. Keep hues if a dark dashboard theme is built later.
- Type: display/headings = Libre Caslon Display (400 only); UI/body = Sora (400/500/600/700); data/numbers = IBM Plex Mono (400/500, tabular figures).
- Motion: ease `cubic-bezier(0.16,1,0.3,1)` (ease-out-expo) everywhere. Micro (hover/press) 120–160ms. Standard (dropdown/toast/modal) 200–280ms. Page-level 320–420ms. Style = fades + small translate (8–12px) or scale (0.96–0.98). No bounce/elastic/spring. Respect `prefers-reduced-motion`.
- No pricing page/model — MARS is open source. Marketing pages: Home, Features, Docs, About. Legal: Privacy, Terms (real content, not dead links).
- Cards: flat, 1px border, no shadow by default (`border:1px solid var(--rule); border-radius:14px`). No heavy drop shadows anywhere.
- Border radius caps at ~10–12px on large surfaces, ~8–9px on buttons/inputs. Nothing ≥16px.

## Anti-patterns to actively avoid (standing instruction)
No "X, but for Y" or "it's not X it's Y" headlines. No Inter/Space Grotesk/Geist. No gradient-fill
headline text. No em-dash overuse. No "seamless/frictionless/unlock/magic" copy. No fake
testimonials or stock headshots. No emoji as feature markers. No bento grids. No "3 feature cards
in a row" or "3 pricing tiers." No fake terminal typing demo. No "trusted by" logo tickers. No
giant dashed drag-and-drop zones. No custom green-circle checkmark bullets. No colored-dot or
left-border-accent indicators anywhere (alerts, lists, cards) — color-code the text/label itself
instead. No pure-white blinding backgrounds or purple/black neon dark mode. No glassmorphism. No
dot-grid backgrounds. No floating 3D blobs. No sparkle icons. No glowing radio orbs. No rainbow 1px
borders. No neon/pastel clashes. No hand-drawn wiggly arrows. No tilt/scale-15° hover cards. No
heavy multi-layer drop shadows. No pop-in without skeleton states. No fake Cmd+K mockup unless
real. No overlapping stock avatar clusters. No idealized fake UI mockups — screenshot the real
thing. Every page that should exist must exist (About, Privacy, Terms) with real content and
working links; primary CTA always leads somewhere real (GitHub repo, docs, dashboard), never a
dead "book a demo."

## Route map (implemented in `frontend/app/`)
- `/` — marketing Home (hero, 4-step process, product preview, closing CTA)
- `/features` — five-stage pipeline walkthrough (ingest/parse/score/alert/display)
- `/docs` — quick start, guides, CLI reference, configuration
- `/about` — what the score is/isn't, open source
- `/privacy`, `/terms` — real legal content
- `/dashboard` — Sector Health overview (KPIs, threshold rail, component breakdown, alerts, 90-day
  trend), wired to the live FastAPI backend via `lib/api.ts`
- `/dashboard/review` — PDF-extraction review queue (`needs_review=True` figures). UI only — no
  backend endpoint exists yet for this workflow.
- `/dashboard/settings` — alert email, exit-fee %, scheduler toggle, read-only scoring weights. UI
  only — not wired to a persistence endpoint yet.

Shared chrome: `components/SiteNav.tsx` + `components/SiteFooter.tsx` (marketing, light), and
`components/DashboardNav.tsx` (app, styled to match Site Nav exactly — light top bar, not a dark
sidebar). The five data-bound dashboard components (`KpiCard`, `ThresholdRail`,
`ComponentBreakdown`, `AlertFeed`, `Sparkline`) were restyled via CSS tokens only — their
props/logic are unchanged from the pre-redesign app.
