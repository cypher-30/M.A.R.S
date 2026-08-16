# What this system does, in plain terms

## The one-sentence version

It watches four things about Kenyan banks every day, turns them into a single
score out of 100, and emails you when that score crosses a line you set in advance.

---

## The problem it solves

You're putting money into a fund that tracks Kenyan bank shares. Whether that's a
good place for your money depends on things that change slowly and quietly —
interest rates, inflation, how many loans people are failing to repay.

Checking all that by hand is tedious, so most people don't. Then something goes
wrong, they panic, and they sell at the worst possible moment.

This system does the checking for you, every day, without getting emotional.

---

## How it works, in four steps

**1. It collects the numbers**

Four things, automatically:

| What it watches | Why it matters |
|---|---|
| The Central Bank's interest rate | When borrowing gets expensive, banks lend less and more borrowers struggle |
| Inflation | Prices rising fast means customers have less money and banks cost more to run |
| Government bond returns | If you can earn a safe 17% from government paper, big investors pull money out of shares |
| Bad loans at the big banks | The clearest sign the sector is actually in trouble, not just might be |

The first three come from websites and data feeds. The fourth is buried in the
long PDF reports banks publish every quarter — so the system reads those PDFs for
you and pulls the number out.

**2. It turns them into one score**

Each of the four gets marked out of 100, where 100 is healthy. Bad loans count for
the most (30%) because they measure real damage rather than predicting it. The
four marks get combined into one number: today's **Sector Health Score**.

**3. It compares that score to two lines**

```
  0 ─────────── 35 ──────────────── 70 ─────────── 100
      SELL            HOLD               BUY
```

Below 35, conditions look bad. Above 70, they look good. In between, sit tight.

**4. It emails you — but only when it should**

Two rules stop it from becoming noise you ignore:

- It only emails when the answer *changes*. No daily "still fine" messages.
- Before it says sell, it checks the maths on whether selling is worth it. Your
  broker takes roughly 2% on the way out and another 2% on the way back in. So a
  small dip isn't worth reacting to — the fees would cost you more than staying
  put. It only calls for a sell when the expected loss is bigger than the cost of
  leaving.

---

## What you actually see

A single web page showing:

- Today's score, big, with a marker on a 0–100 bar showing where it sits relative
  to the two lines
- Which of the four inputs is pulling the score up or down
- The score's trend over the last 90 days
- A list of past alerts

---

## The honest limitations

**It describes conditions. It does not predict prices.** A low score means the
environment looks difficult, not that the fund will fall.

**The scoring is your opinion, written down.** Someone else could weight bad loans
at 20% instead of 30% and get different answers. The point isn't that the numbers
are objectively right — it's that they're fixed in advance, so you can't talk
yourself into a different answer on a bad day.

**The PDF reader can misread.** That's why any figure it extracts is held aside
and marked "needs checking" until you confirm it, rather than quietly feeding into
the score.

**The weights are untested guesses right now.** They need testing against past
data before you trust a signal from them. That's why the plan has you running it
for weeks with no money following it first.

---

## Where the jargon lives, if you need it

| Term you'll see in the code | What it means |
|---|---|
| CBR | Central Bank Rate — the interest rate |
| CPI | The inflation measure |
| NPL | Non-performing loans — loans not being repaid |
| Sub-score | One input's mark out of 100 |
| Sector Health Score | The four sub-scores combined |
| Signal | The recommendation: BUY, HOLD, or SELL |
| Connector | A piece of code that fetches from one source |
| Snapshot | All four readings as they stood on one day |
