# What would change the verdict (pre-registered)

Written on 2026-10-02, before the next reading, for ABSI v0.1. The thresholds below are the author's judgment, not statistically derived. They are fixed in advance so that results cannot be reinterpreted afterwards. Changing a threshold requires a new version (v0.2) and a journal entry saying why.

The Protocol asks: "What would prove the bubble thesis wrong?" This file turns that into numbers, and it also states what would strengthen the thesis, so the test is symmetric.

## A. Evidence that would lower stress or weaken the bubble thesis

| # | Condition | Threshold | Where it stands now (2026-10-02) |
|---|---|---|---|
| A1 | Identifiable AI revenue covers required revenue. Required revenue is the revenue one year of capex must earn to return 10% over a 5.5-year server life, at a 60% gross margin (about $352B for $750B of capex, see METHODOLOGY). | Coverage of 75% or more counts as strong support; 100% or more rejects the thesis on the monetization dimension. | About 38% using only the two frontier labs' run rates ($65B Anthropic + $70B OpenAI = $135B). This excludes cloud-provider and software AI revenue, so it understates; run rates also overstate recognized revenue. |
| A2 | Frontier-lab gross margin | At least 50% for two consecutive reported quarters. | Not reliably reported. A secondary source puts OpenAI near 33-39%; unconfirmed. |
| A3 | Leading-edge GPU utilization | Independent evidence of utilization at or above 80% while installed capacity keeps growing. | No public series. |
| A4 | Hyperscaler cash coverage of capex | Combined free cash flow stays at or above zero while capex still grows. | Amazon's trailing free cash flow is negative (-$7.6B per one source). |
| A5 | Financing | Debt share of capex falls below 20%, or 5-to-7-year hyperscaler bond spreads return to the 2025 level (about 50bp). | Debt share about 32%; spreads about 60bp. |
| A6 | Valuation adjusts without a fundamentals collapse | CAPE below 30 while hyperscaler and Nvidia revenue is still growing. | CAPE about 41. |
| A7 | Productivity | US nonfarm business labor productivity growth above its 2010-2019 average for four consecutive quarters, with at least one independent study attributing a share to AI. | Not yet collected. |

## B. Evidence that would raise stress or strengthen the bubble thesis

| # | Condition | Threshold |
|---|---|---|
| B1 | Demand stops outrunning supply | Frontier-lab revenue growth falls below hyperscaler capex growth for two consecutive quarters. |
| B2 | Spending is cut without a revenue offset | Any of the four large hyperscalers cuts full-year capex guidance by 10% or more. |
| B3 | Compute prices fall while capex rises | A published GPU rental price index falls 30% or more over six months while aggregate capex guidance rises. |
| B4 | Capital markets close | A pulled or sharply discounted mega-IPO (priced below the initial range), or 5-to-7-year hyperscaler spreads widen by 50bp or more. |
| B5 | Customer concentration bites | A top customer of a frontier lab or of Nvidia reduces commitments, or a disclosed related-party customer share rises. |

## How these are used

- Each condition is checked at every update and logged in the research journal as met, not met, or no data.
- A condition with no data counts as "no data", never as "not met". Most A-conditions currently have no data or only partial data; this is one reason confidence is low.
- Meeting A1 or several A-conditions at once should push the matching component scores down. Meeting several B-conditions should push them up. The index weights themselves do not change within a version.
- If the score rises over time while several A-conditions are being met, that conflict is itself reported as a finding.
