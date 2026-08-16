# Scoring notes

A log of why the numbers in `backend/app/scoring/weights.py` are what they are. Add an
entry whenever you change one. Future-you will not remember the reasoning, and an
unexplained weight is an unmaintainable one.

## Starting weights (pre-backtest)

| Input | Weight | Reasoning |
|---|---|---|
| NPL | 30% | The only input that measures realised credit distress rather than forecasting it. Slow-moving but rarely wrong. |
| CBR | 20% | Leads loan growth and margins. Fast to observe. |
| Treasury yield | 20% | Proxy for capital rotating out of equities into risk-free paper. |
| Momentum | 15% | Catches what the other four miss, but is also the noisiest. Deliberately capped. |
| CPI | 15% | Real but indirect: it acts on banks through costs and consumer capacity. |

These are guesses. They have not been backtested. Treat any signal they produce as
provisional until step 8 of `build-order.md` is done.

## Open questions to settle with the backtest

- Do the CBR bands hold across a full tightening cycle, or does the score sit at SELL for
  months at a time?
- Is a 30-day momentum window too short? A single volatile fortnight can swing it.
- Should NPL be a level or a rate of change? A stable 13% is a different signal from 9%
  climbing to 13%.
- How thin is the ETF's order book in practice? A signal you can't act on at a reasonable
  spread isn't worth acting on.

## Changelog

| Date | Change | Why |
|---|---|---|
| — | Initial weights set | Starting point, pre-data |
| — | Extraction check compares parsed numbers, not digit strings | Substring matching broke on `12450000000.0` vs `KES 12,450,000,000` and would have accepted 13 as a match for 13.4 |
