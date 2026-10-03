# ABSI Research Journal

Methodology is never changed silently. Every change is versioned and recorded here.

## Entry 1: 2026-10-02: ABSI v0.1 first read

**Hypothesis:** market-side stress (valuation, concentration, financing) is running ahead of fundamental support (demand growth, scarcity, supplier cash flow).

**Result (Protocol weights):** composite 58/100, confidence about 25/100. Across three weighting schemes (Protocol, equal, valuation halved) the range is 54 to 58. Provisional regime: speculative expansion.

**Component stress:** Valuation 74, Capex/monetization 67, Supply-demand 19, Profitability 60, Exuberance 84, Financing 57, Infrastructure 35.

**Evidence against the thesis (kept visible on purpose):** Nvidia revenue +106% at 75% gross margin; lab run rates growing faster than capex; leading-edge compute scarce; cloud growth accelerating; credit spreads only about 10bp wider.

**Weaknesses:**
- Confidence is low: only 17 of about 34 planned indicators have data. Utilization, token economics, productivity and venture-capital flows are not measured.
- 10 of 17 indicators are analyst judgments of reported facts, not computed values.
- Lab revenue is run rate, not recognized revenue. OpenAI figures come from a secondary source.
- No backtest yet, so weights and anchors are unvalidated.
- Several rows overlap (capex, concentration, debt). They are group-averaged, but the dependency map is still crude.
- Conflict of interest: the analysis was prepared with an AI model built by Anthropic, which is the subject of one indicator.

**Required-revenue scenario (one $750B vintage, servers only):** gross profit needed per year is $136B (5.5-year life, break-even) to $400B (3-year life, 20% return). At a 10% return and 5.5-year life it is $211B, about $352B of revenue at an assumed 60% gross margin.

**Next:** (1) collect forward P/E and reverse-DCF for Nvidia and hyperscalers; (2) find real utilization, token-price and power-queue series; (3) design the backtest on the subset of metrics with history, with weights frozen first; (4) replace judgment rows with measured ones, version as v0.2; (5) automate the daily market-data refresh.

## Entry 1a: 2026-10-02: pre-publication audit (no change to scores)

Before publishing, every figure was re-checked against its source. Wording corrections only; no indicator value, weight or anchor changed, so the v0.1 scores are unchanged (58 / 56.8 / 54.4).

- Capex/revenue (38%): the source does not state which companies are in the group. Relabelled as "hyperscaler capex" and noted.
- The "25-51% higher H2 spending" statement applies to Microsoft, Alphabet and Meta only, not Amazon. Corrected.
- OpenAI: secondary-source projections (about -$14B 2026 loss, ~$856B commitments, $1.4T valuation talks, 45% of Microsoft's backlog) conflict with or are not confirmed by reported figures (2025 net loss $38.5B on $13.07B revenue). They are now marked unconfirmed wherever used. They enter only the judgment rows, the lab valuation multiple and the commitments-to-revenue ratio.
- Cloud growth evidence (Google Cloud +63%, AWS +28%) is Q1 2026, not Q2. Labelled.

## Entry 1b: 2026-10-02: robustness and pre-registered falsification (no change to scores)

- **Weight robustness added to the script.** Under 1,000 random weightings the composite has median 57 and a 5th-95th percentile band of 44 to 68 (full range 30 to 77); jittering judgment rows by up to 10 points leaves the band unchanged. Conclusion: the headline 58 is not precise. The defensible reading is moderate to elevated stress at low confidence.
- **Falsification thresholds written down before the next reading** (`FALSIFICATION.md`). First coverage estimate: the two frontier labs' run rates ($135B) cover about 38% of the roughly $352B revenue that 2026 capex must earn for a 10% return, at a 5.5-year server life and 60% gross margin. This understates total AI revenue and run rates overstate recognized revenue.
- **Weakness:** the thresholds are judgment, not derived from data. They will be tested in the backtest.

## Entry 2: 2026-10-03: ABSI v0.2 automation

- **What changed:** a daily GitHub Actions job now refreshes CAPE and adds one measured indicator (US investment-grade credit spread). Weights and all other values are unchanged. Details in METHODOLOGY section 9.
- **Expected effect:** with spreads near 1 percentage point, the new indicator reads as low stress (about 6/100 at 0.9), which lowers the financing component and the composite by a few points. This is a consequence of adding a measured, counter-thesis indicator, not a change of view.
- **Weaknesses:** the spread is broad investment-grade credit, not AI debt specifically; the anchors (0.8 and 2.5) are judgment; the job was tested offline with fixtures and a generated spreadsheet, and its first live run against the real Yale and FRED files is the real test; most of the index still moves only when someone updates it by hand.
- **Next:** check the first live run, then replace judgment rows with measured ones (SEC filings for capex, revenue and cash flow), then the backtest.
