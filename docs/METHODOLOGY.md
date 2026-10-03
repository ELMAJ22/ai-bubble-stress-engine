# ABSI v0.1 Methodology

Version frozen on 2026-10-02. Any change creates v0.2.

## 1. Indicator stress (0 to 100)

Each indicator gets a stress score:

- **Measured indicators** are placed between two anchors: `stress = clamp((value - low) / (high - low) * 100, 0, 100)`. The low anchor means no stress and the high anchor means maximum stress. Anchors are stated in each indicator's note (for example Shiller CAPE: 17 is the long-run median, 44 is about the 2000 peak).
- **Judgment indicators** (marked `judgment`) have a fixed 0-100 score assigned by the analyst from reported facts, with the reasoning in the note. These are the weakest rows and are the first to be replaced with measured data.

Every indicator has a **confidence** from 0 to 1 and a type: `actual`, `estimate`, `target`, `guidance`, `company`, `report` or `judgment`.

## 2. Avoiding double counting

Indicators that measure the same underlying phenomenon share an **overlap group** (for example both concentration measures sit in `concentration`). Inside a component, an indicator's weight is `(1 / number of indicators in its group) * confidence`, so two overlapping indicators count as one.

## 3. Component score

`component stress = sum(stress * weight) / sum(weight)` over its indicators.

`component confidence = average indicator confidence * min(1, indicators present / indicators planned)`.

Planned counts are V5, M5, S5, P5, E5, F5, I4, so a component with few of its planned indicators has low confidence even if each indicator is reliable.

## 4. Composite

Seven components with starting weights:

| Component | Weight |
|---|---|
| Valuation (V) | 25 |
| Capex / monetization (M) | 20 |
| Supply vs demand (S) | 20 |
| Profitability / cash flow (P) | 15 |
| Market exuberance (E) | 10 |
| Capital flow / financing (F) | 5 |
| Physical infrastructure (I) | 5 |

`composite = sum(component stress * weight) / sum(weights)`, and `confidence = sum(component confidence * weight) / sum of all seven weights` (a component with no data counts as zero confidence).

These weights are a hypothesis, not a result. Two alternative schemes are reported alongside: **equal weights** (100/7 each) and **valuation halved** (half of Valuation's weight moved equally to Financing and Infrastructure). If conclusions differ between schemes, the index is not robust.

## 4a. Weight robustness

`scripts/absi_score.py` re-scores the index under 1,000 random weightings (flat Dirichlet, seed 42, so every split of the weight points is equally likely), and again with every judgment score shifted by a random amount of up to 10 points. Result for v0.1: median 57, 5th-95th percentile 44 to 68, full range 30 to 77. This tests sensitivity to weighting and to judgment scores. It does not test data errors or whether the anchors are right.

## 5. Bands and regime (provisional)

| Composite | Band |
|---|---|
| below 35 | Low stress |
| 35 to 55 | Moderate stress |
| 55 to 75 | Elevated to high stress |
| 75 and above | Extreme stress |

The regime label is a simple provisional rule: composite below 35 is "Fundamental expansion"; 75 or above is "Bubble stress"; if the market side (Valuation and Exuberance average) is at least 70 while the fundamentals side (Supply/Demand and Profitability average) is below 50, the label is "Speculative expansion"; if both are high, "Fragility". The bands and rules have not been calibrated against history.

## 6. Required-revenue scenario thresholds

Not forecasts. For one year of capex `C` and a server life `L` years, the gross profit that capex must earn each year to return `r` is `C * (1/L + r)`. In v0.1: `C = $750B` (2026 big-tech capex guidance), `L` of 3, 5.5 and 6 years, `r` from 0% to 20%, and revenue is shown at an assumed 60% gross margin. This covers servers only: it ignores power, land and buildings, repeat annual vintages, and AI revenue that already exists.

## 7. Falsification

Conditions that would lower or raise the score are fixed in advance in [`FALSIFICATION.md`](FALSIFICATION.md).

## 8. Known limits of this method

- No historical backtest yet. Anchors and weights are unvalidated.
- Confidence is a transparent heuristic, not a statistical interval.
- Group averaging reduces but does not remove double counting (capex, Nvidia revenue and GPU demand all overlap economically).
- Run-rate revenue overstates recognized revenue for fast-growing firms.
- A score is not a probability. There is no probability model.
