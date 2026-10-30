# Example 2 — Sales and advertising efficiency

**Problem and objective:** Identify sellers whose advertising spend needs review alongside delivered sales performance.

**Inputs:** `03_Daily_Sales.csv` and `05_Daily_Advertising.csv` in `inputs/`.

**Processing:** Analyze each file independently in parallel → combine at seller/date level → produce a scorecard and decision brief in parallel.

**Outputs:** Two aggregates and a reconciled combined table in `working/`; `seller_scorecard.xlsx` and `budget_review.md` in `outputs/`.

**Challenges:** Detailed joins inflate totals. Budget repeats across campaign segments. ROAS uses attributed revenue, not total seller sales; it does not measure profit. Compare daily averages across unequal periods.

## Prompt

```text
Create a seller sales and advertising review from inputs/.
Before creating files, show the architecture, workflow, folders and outputs for approval.
After approval, create CLAUDE.md covering the goal, inputs, outputs, workflow and agent roles. Create agents/:
- agent_1_sales.md: validate sales and save seller/date booked and delivered sales aggregates in working/.
- agent_2_ads.md: validate advertising and save seller/date spend, clicks, impressions and attributed revenue in working/; count budget once per campaign/day.
- agent_3_combine.md: combine both aggregates on seller/date, flag unmatched records, reconcile totals and calculate weighted ROAS, CPC and trends.
- agent_4_scorecard.md: create outputs/seller_scorecard.xlsx from the combined results.
- agent_5_brief.md: create outputs/budget_review.md with three evidence-backed priorities, caveats and proposed experiments.
Run [1 and 2 in parallel] → 3 → [4 and 5 in parallel]. Save shared calculations in working/ and verify both outputs agree. Do not equate ROAS with profit.
Work in this local folder, preserve inputs, and disclose any unavailable tools or subagent support.
```
