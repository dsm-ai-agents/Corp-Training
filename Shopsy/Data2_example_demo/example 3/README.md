# Example 3 — Data quality rescue

**Problem and objective:** Make an unreliable sales extract usable while preserving evidence and isolating records that cannot be safely repaired.

**Inputs:** `10_Challenge_Dirty_Sales.csv`, `02_Listing_Master.csv` and `01_Seller_Master.csv` in `inputs/`. No clean sales answer file is supplied.

**Processing:** Audit → repair or quarantine → independent review → targeted rework when checks fail.

**Outputs:** Audit rules and change log in `working/`; `clean_sales.csv`, `quarantined_sales.csv` and `quality_report.md` in `outputs/`.

**Challenges:** Duplicate rows, orphan or conflicting IDs, invalid dates, missing values, inconsistent types and incorrect amounts. Some values cannot be recovered reliably; quarantine them rather than inventing corrections.

## Prompt

```text
Repair the sales extract in inputs/ using the listing and seller masters.
Before creating files, show the architecture, workflow, folders and outputs for approval.
After approval, create CLAUDE.md with the goal, workflow, inputs, outputs and agent roles. Create agents/:
- agent_1_audit.md: profile the files and save validation rules and a row-level issue log in working/.
- agent_2_repair.md: apply justified corrections, log old/new values and reasons, and save candidate clean and quarantine files in working/. Never guess missing business values.
- agent_3_review.md: independently check keys, dates, types, statuses, units/orders and GMV arithmetic; reconcile every input row to kept, quarantined or removed-duplicate records and explain amount changes.
Run 1 → 2 → 3. If review fails, return specific issues to Agent 2 and rerun review, up to two repair cycles; report unresolved issues explicitly.
Publish outputs/clean_sales.csv, outputs/quarantined_sales.csv and outputs/quality_report.md with corrections, exclusions and review results. Do not claim unresolved data is clean.
Work in this local folder, preserve inputs, and disclose any unavailable tools or subagent support.
```
