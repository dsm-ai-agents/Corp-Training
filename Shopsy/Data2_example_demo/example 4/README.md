# Example 4 — Large dataset reporting

**Problem and objective:** Summarize a roughly 100 MB transaction file accurately without relying on a preview or loading all rows into the conversation.

**Input:** `inputs/regional_transactions_100mb.csv`, synthetic January–September 2026 data. See `DATA_NOTES.md` for fields and definitions; `inputs/file_manifest.json` records exact size, row count and checksum.

**Processing:** Inspect structure → process the complete file with a suitable local method → validate coverage and totals → report trends and exceptions.

**Outputs:** `monthly_region_summary.csv`, `large_data_report.md` and `processing_checks.json` in `outputs/`.

**Challenges:** Memory limits, truncated previews, incomplete processing, weighted averages, returns and cancelled transactions. The AI chooses the implementation; the prompt does not prescribe a language.

## Prompt

```text
Create a regional performance report from the large transaction file in inputs/.
Before creating files, show the architecture, workflow, processing approach and outputs for approval.
After approval, create CLAUDE.md with the goal, folders, inputs, outputs and agent roles. Create agents/:
- agent_1_profile.md: inspect the schema, data notes and manifest; choose a local approach that can process the entire file within available resources.
- agent_2_aggregate.md: process every record and save monthly/region/status summaries, KPIs and exceptions in working/. Separate booked value, delivered value and refunds.
- agent_3_verify_report.md: independently check processed row counts, keys and control totals, then create outputs/monthly_region_summary.csv, outputs/large_data_report.md and outputs/processing_checks.json.
Run 1 → 2 → 3. Do not treat a sample or preview as the full dataset. Use ratios of sums and disclose incomplete processing or unsupported claims.
Choose appropriate tools yourself. Keep processing local, preserve inputs, and disclose unavailable tools or subagent support.
```
