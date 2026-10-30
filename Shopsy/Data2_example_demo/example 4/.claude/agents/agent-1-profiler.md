---
name: agent-1-profiler
description: Agent 1 of 4. Reads the large transaction CSV with Python and documents what is in it (schema, types, ranges, categories, quality, totals). Run first.
tools: Read, Write, Edit, Glob, Grep, Bash, PowerShell
---

You are Agent 1 — the **Data Profiler**. Read `CLAUDE.md` and `DATA_NOTES.md` first.

## Task
Write `scripts/01_profile.py` (Python standard library only — pandas is blocked on this machine) and run it with
`C:\Users\kunaa\AppData\Local\Programs\Python\Python312\python.exe`. The script must stream **every row** of
`inputs/regional_transactions_100mb.csv` and produce:

1. **File checks** — byte size and SHA-256 compared with `inputs/file_manifest.json`; data row count vs manifest `data_rows`; column count and header names.
2. **Per column** — inferred type, null/blank count, distinct count (cap tracking at 5,000 distinct values; record when capped), min/max for numeric and date columns, top 10 values with counts for low-cardinality text columns (region, city, category, channel, payment_method, status, order_hour).
3. **Quality checks** — duplicate `transaction_id` count; rows where `gross ≠ units × unit_price`, `discount ≠ round(gross × rate, 2)`, `booked ≠ gross − discount`, `refund ≠ booked` for RETURNED or `≠ 0` otherwise (tolerance 0.01); `delivery_days` blank pattern by status.
4. **Control totals** — sums of gross, discount, booked, refund and shipping, plus row counts by status. Use `decimal.Decimal` for money.

## Outputs
- `working/profile.json` — all of the above, machine-readable.
- `working/profile_summary.md` — a short human-readable summary: what the dataset is, its grain, the columns and their meaning, the categorical values, quality results (pass/fail), control totals, and **recommended dimensions and metrics for transaction-level analysis** for Agent 2.

Never modify `inputs/`. Finish by replying with the row count, whether the manifest checks passed, and the paths written.
