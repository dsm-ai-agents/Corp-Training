# Agent 1: Data clean and validate
Run: `python scripts/agent_1_data_clean.py`
Reads: `input/01_Seller_Master.csv`, `input/03_Daily_Sales.csv` (read only; handle UTF-8 BOM).
Writes: `working/merged_sales.csv`, `working/validation_checks.json`.

Steps
1. Trim text, uppercase status, parse order_date, coerce numerics.
2. Check nulls, duplicate sales_row_id, duplicate seller_id in master.
3. Validate keys: every sales seller_id exists in master (orphans = 0); report master sellers with no sales.
4. Check units x selling_price_inr = gmv_inr per row; units >= orders; statuses limited to the four known values.
5. Left join sales to sellers on seller_id. Row count must equal raw sales rows.
6. Reconcile: merged GMV equals raw GMV; booked + cancelled = gross; delivered + ready to ship + returned = booked.
7. Save merged data and a checks file with pass/fail per check. Exit non-zero if any check fails.
