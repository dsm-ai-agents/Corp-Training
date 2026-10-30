# Regional Transactions → Gmail HTML Dashboard

## Goal
Turn the ~100 MB transaction file in `inputs/` into a colourful, readable HTML dashboard
and deliver it to stakeholders as a Gmail HTML email. Four agents run **one at a time**,
each reading the previous agent's files.

## Folders
| Folder | Purpose |
| --- | --- |
| `inputs/` | Source data. **Read-only — never modify.** |
| `scripts/` | Python written by the agents (`01_profile.py`, `02_aggregate.py`, `03_build_report.py`) |
| `working/` | Intermediate files passed between agents |
| `outputs/` | Final HTML dashboard and email log |
| `.claude/agents/` | The four subagent definitions |

## Inputs
- `inputs/regional_transactions_100mb.csv` — 640,393 rows, 21 columns, Jan–Sep 2026, INR
- `inputs/file_manifest.json` — expected row count, bytes, SHA-256
- `DATA_NOTES.md` — field definitions and metric rules (authoritative)

## Environment
- Python: `C:\Users\kunaa\AppData\Local\Programs\Python\Python312\python.exe` (not on PATH; call by full path)
- **Standard library only.** Smart App Control blocks pandas/numpy DLLs on this machine, so use
  `csv`, `json`, `hashlib`, `collections`, `decimal`. Stream the file row by row; never load it into the conversation.

## Agent pipeline (run sequentially: 1 → 2 → 3 → 4)
| # | Agent | Reads | Writes |
| --- | --- | --- | --- |
| 1 | `agent-1-profiler` | `inputs/`, `DATA_NOTES.md` | `scripts/01_profile.py`, `working/profile.json`, `working/profile_summary.md` |
| 2 | `agent-2-analyst` | `working/profile_summary.md`, `working/profile.json` | `scripts/02_aggregate.py`, `working/analysis.json`, `working/analysis_summary.md`, `working/monthly_region_summary.csv` |
| 3 | `agent-3-report-builder` | `working/analysis.json`, `working/analysis_summary.md` | `scripts/03_build_report.py`, `outputs/dashboard_email.html` |
| 4 | `agent-4-gmail-sender` | `outputs/dashboard_email.html` | Gmail draft, `outputs/email_log.json` |

## Metric rules (from DATA_NOTES.md)
- Order count = row count. Booked value = sum `booked_amount_inr` (all statuses).
- Delivered value = booked where `status=DELIVERED` — do **not** subtract refunds again.
- Refunds = sum `refund_amount_inr` (RETURNED rows). Shipping fees are separate.
- AOV = sum booked ÷ order count of the same population. Effective discount = sum discount ÷ sum gross (never average row rates).
- Every rate states its denominator. Use ratios of sums.

## Email rules
- Gmail-safe HTML: inline styles only, table layout, no JavaScript, no external CSS/fonts, max width ~680px.
- Default recipient: **draft** to datasciencemasterminds@gmail.com. Never send to anyone else without explicit user confirmation in chat.

## Rules
- Process the complete file — a preview or sample is never the dataset. Verify row count against the manifest.
- Disclose any incomplete processing or unsupported claim in the report.
