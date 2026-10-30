# Agent 3: Executive slide
Run: `python scripts/agent_3_powerpoint.py`
Reads only: `working/kpi_summary.json`.
Writes: `outputs/executive_slide.pptx` (one 16:9 slide, native chart, no text overflow).
Slide: headline message, tiles for Booked GMV and Delivered GMV (separate), leakage (returned, cancelled), regional chart (booked vs delivered by zone), top exceptions, reconciliation footnote.
Rules: Rs lakh format, no em dashes, totals must match kpi_summary.json exactly.
