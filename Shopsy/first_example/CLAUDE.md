# Executive Reporting Pipeline: Shopsy regional sales (Oct 2026)

## Goal
Turn regional seller and daily sales data into two executive outputs that use one KPI summary and agree on every total:
a one-slide PowerPoint for leadership and a self-contained HTML dashboard for regional managers.

## Definitions (fixed, approved)
- Region = `seller_zone` (NORTH, SOUTH, WEST, EAST). City, state, manager and tier are drill-downs.
- Gross GMV = all rows.
- Booked GMV = DELIVERED + READY_TO_SHIP + RETURNED (gross minus CANCELLED).
- Delivered GMV = DELIVERED only. Never mix it with booked GMV.
- Returned and Cancelled GMV are shown separately as leakage.
- Reconciliation: Booked + Cancelled = Gross; Delivered + Ready to ship + Returned = Booked.
- Rates: delivered rate = delivered / booked; return rate = returned / booked; cancel rate = cancelled / gross.
- Currency: Rs, lakh format. No em dashes in any copy.

## Workflow
1 -> 2 -> [3 and 4 in parallel]. Agents 3 and 4 read only `working/kpi_summary.json`.
Run: `python scripts/run_pipeline.py` (or run each `scripts/agent_N_*.py` in order).

## Folders
- `input/`   original CSVs. Read only, never edited.
- `agents/`  one instruction file per agent.
- `scripts/` the code each agent runs.
- `working/` merged_sales.csv, validation_checks.json, kpi_summary.json, summary.md.
- `outputs/` executive_slide.pptx, regional_dashboard.html.

## Inputs
- `input/01_Seller_Master.csv`: seller_id, display_name, seller_city, seller_state, seller_zone, darwin_tier, owner.
- `input/03_Daily_Sales.csv`: sales_row_id, order_date, listing_id, seller_id, status, orders, units, selling_price_inr, gmv_inr.
- No `02_` file exists. Treat as intentional.

## Outputs
- `outputs/executive_slide.pptx`: one slide.
- `outputs/regional_dashboard.html`: self-contained, mobile friendly, no external requests.

## Agent roles
- Agent 1 (`agents/agent_1_data_clean.md`): clean, join, validate, reconcile. Stops the pipeline if a check fails.
- Agent 2 (`agents/agent_2_summary.md`): regional KPIs, trend, exceptions, performance. Writes the single KPI summary.
- Agent 3 (`agents/agent_3_powerpoint.md`): one executive slide.
- Agent 4 (`agents/agent_4_html.md`): regional manager dashboard.
