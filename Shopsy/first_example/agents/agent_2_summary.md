# Agent 2: KPI summary
Run: `python scripts/agent_2_summary.py`
Reads: `working/merged_sales.csv`, `working/validation_checks.json` (must be all pass).
Writes: `working/kpi_summary.json` (single source of truth for agents 3 and 4) and `working/summary.md`.

Contents
- Totals: gross, booked, delivered, ready to ship, returned, cancelled GMV; orders, units, AOV; rates.
- Regional KPIs by zone, plus city, manager and tier cuts.
- Trend: daily and weekly (booked vs delivered), overall and by zone.
- Exceptions: sellers with return or cancel rate above 1.5x the overall rate, and sellers whose delivered rate is 10+ points below their zone.
- Performance: zone ranking, top and bottom 5 sellers by delivered GMV, headline messages.
Rules: booked and delivered are always separate fields. Round only at display time.
