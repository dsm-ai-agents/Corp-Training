# Example 1 — Regional executive reporting

**Problem and objective:** Regional managers need one consistent view of sales performance, exceptions and priorities.

**Inputs:** `03_Daily_Sales.csv` and `01_Seller_Master.csv` in `inputs/`. Join on seller ID; `seller_zone` defines region.

**Processing:** Clean and validate → calculate regional KPIs and trends → create two presentations of the same results in parallel.

**Outputs:** Validated data and KPI summary in `working/`; `executive_slide.pptx` and `regional_dashboard.html` in `outputs/`.

**Challenges:** Duplicate joins, missing regions, booked versus delivered GMV, and inconsistent figures across outputs. Regions describe sellers, not customers.

## Prompt

```text
Create an executive reporting pipeline from the regional data in inputs/.
Before creating files, show the architecture, workflow, folders and outputs for approval.
After approval, first create CLAUDE.md with the project goal, workflow, folders, inputs, outputs and agent roles.
Create and use these agents in agents/:
- agent_1_data_clean.md: clean, join sales to sellers, validate keys and reconcile totals; save merged data and checks in working/.
- agent_2_summary.md: create regional KPI, trend, exception and performance summaries from validated data in working/.
- agent_3_powerpoint.md: create outputs/executive_slide.pptx, a one-slide executive PowerPoint.
- agent_4_html.md: create outputs/regional_dashboard.html, a self-contained KPI dashboard for regional managers.
Run 1 → 2 → [3 and 4 in parallel]. Both outputs must use the same KPI summary and agree on totals. Separate booked and delivered GMV.
Work in this local folder, preserve inputs, and disclose any unavailable tools or subagent support.
```
