# AI Bubble Stress Engine

By Aldrin Joseph

A research project that measures how financially fragile the global AI investment cycle is, using public evidence, and that is built to reach conclusions that contradict its author's starting belief.

**Central question:** is the economic value created by AI growing quickly enough, profitably enough and sustainably enough to justify the capital being committed to it?

**[View the live dashboard](https://elmaj22.github.io/ai-bubble-stress-engine/)**: current score, history, and the evidence for and against.

<!-- ABSI:START -->
## Current reading (ABSI v0.2, data as of 2026-10-05)

| | |
|---|---|
| **Composite stress** | **57 / 100** (Elevated to high stress; 53 to 57 across three weighting schemes) |
| **Confidence** | **about 25 / 100** (18 of about 34 planned indicators have data) |
| **Provisional regime** | Speculative expansion |

| Component | Stress (0-100) |
|---|---|
| Market exuberance | 84 |
| Valuation | 76 |
| Capex / monetization | 67 |
| Profitability / cash flow | 60 |
| Capital flow / financing | 41 |
| Physical infrastructure | 35 |
| Supply vs demand | 19 |

This is a **stress score, not a probability of a crash.** Low confidence means the number is a rough position, not a measurement.
<!-- ABSI:END -->

Evidence **against** the bubble thesis (Nvidia revenue +106% at 75% gross margin, lab revenue growing faster than capex, scarce leading-edge compute) is listed next to the supporting evidence in [`data/evidence_2026-10-02.json`](data/evidence_2026-10-02.json).

## Automatic updates (ABSI v0.2)

A GitHub Actions job (`.github/workflows/daily.yml`) runs every weekday. It runs the tests, then `scripts/update_data.py` fetches two free public series, re-scores the index and commits the result:

- **Shiller CAPE** (monthly, Yale): refreshes the valuation indicator. Same definition and anchors as v0.1.
- **US investment-grade credit spread** (daily, FRED/ICE BofA): a new measured financing indicator with anchors fixed in advance (0.8 points = no stress, 2.5 = maximum).

Everything else (company capex and revenue, AI-lab figures, concentration, and the judgment rows) is **not** automated and keeps its launch values until it is updated by hand and recorded in the journal. If a source fails, the last value is kept, the failure is shown in the block above, and the indicator's confidence is halved once the value is stale. The number therefore moves on credit conditions and monthly valuation, not on every news item. See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) section 9.

The block above is rewritten by the job; the history is in [`data/snapshots.csv`](data/snapshots.csv) and the latest details in `data/latest.json`.

## How robust is the number?

The 58 depends on how the seven components are weighted. Re-scoring under 1,000 random weightings gives a median of 57, with 90% of results between 44 and 68 (full range 30 to 77). Shifting every judgment row by up to 10 points in either direction barely changes that band. So the reliable statement is "moderate to elevated stress, with a confident verdict impossible at current data quality", not "exactly 58". This test covers weighting choices only, not errors in the data itself.

## What would change the verdict

[`docs/FALSIFICATION.md`](docs/FALSIFICATION.md) lists, with numeric thresholds written down in advance, what would lower the score (for example identifiable AI revenue covering 75% of the revenue that capex must earn) and what would raise it. Today about 38% of that required revenue is covered by the two frontier labs' run rates alone, which understates total AI revenue.

## Reproduce the score

Needs Python 3 only, no extra packages.

```
python scripts/absi_score.py
```

It reads the data files and prints the composite, the three weighting schemes, the component scores and the weight-robustness test.

## What is in this repository

| Path | What it is |
|---|---|
| [`docs/PROTOCOL.md`](docs/PROTOCOL.md) | The research rules: hypotheses, falsification, data integrity, avoiding double counting and false precision |
| [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) | Exactly how the score is computed in v0.1 |
| [`docs/FALSIFICATION.md`](docs/FALSIFICATION.md) | Pre-registered conditions that would lower or raise the score |
| [`docs/RESEARCH_JOURNAL.md`](docs/RESEARCH_JOURNAL.md) | Dated record of results, weaknesses and next steps |
| `data/indicators_*.json` | Every indicator: value, anchors, confidence, type, source link |
| `data/evidence_*.json` | Evidence for and against the bubble thesis, with sources |
| `data/config_v0.1.json` | Weights, planned indicator counts, required-revenue settings, known data gaps |
| `data/snapshots.csv` | Score history |
| `scripts/absi_score.py` | The scoring formula |
| `scripts/update_data.py` | Daily fetch, re-score and snapshot |
| `tests/` | Unit tests (parsing, scoring, outputs) |
| `.github/workflows/daily.yml` | The daily job |
| `data/config_v0.2.json`, `data/auto_state.json` | v0.2 settings and the last fetched values |

## Known weaknesses (stated up front)

- Only 17 of about 34 planned indicators have data. GPU utilization, token economics, productivity and funding flows are not yet measured.
- 10 of the 17 indicators are the analyst's scored judgments of reported facts, not computed values. They are marked `judgment`.
- AI lab revenue is run rate, not recognized revenue. Private-company figures are company-reported, leaked or from secondary sources; some OpenAI figures (valuation talks, 2026 projections, share of Microsoft's backlog) come from one secondary source, conflict with reported numbers or are unconfirmed, and are marked as such.
- The weights and anchors are a starting hypothesis and have not been backtested against past bubbles.
- Indicators that measure the same phenomenon are group-averaged, but the dependency map is still crude.

## Versioning

The methodology is frozen per version. Any change to weights, anchors or indicators creates a new version (v0.2) with a journal entry explaining why, so the index cannot be quietly tuned after the fact.

## Disclosure

The author (Aldrin Joseph) personally suspects AI valuations are stretched, and built this to test that suspicion rather than assume it. The analysis was prepared with AI assistance (Claude, made by Anthropic). Anthropic's own planned IPO is the subject of one indicator, so independently check the AI-lab rows. Nothing here is investment advice.

## License

MIT, see [`LICENSE`](LICENSE).
