# Agent 4: Regional dashboard
Run: `python scripts/agent_4_html.py`
Reads only: `working/kpi_summary.json`.
Writes: `outputs/regional_dashboard.html` (one file, inline CSS, JS and data, no external requests, mobile friendly).
Contents: KPI tiles (booked and delivered separate), zone selector, regional table, weekly trend, manager and tier cuts, seller table with exceptions flagged, reconciliation strip.
Rules: Rs lakh format, no em dashes, totals must match kpi_summary.json exactly.
