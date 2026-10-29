# Data workflow examples

Five local-folder exercises. Examples 1–3 use synthetic October 2026 Shopsy training data; Example 4 uses a larger synthetic January–September dataset; Example 5 uses your connected Supabase database. Open an example folder in Claude Cowork, read its README, and paste its prompt. Review the proposed architecture before approving execution.

| Example | Objective | Workflow | Final outputs |
| --- | --- | --- | --- |
| [Example 1](example%201/README.md) | Report regional sales performance | Clean → summarize → PowerPoint and dashboard in parallel | Executive slide and regional dashboard |
| [Example 2](example%202/README.md) | Compare seller sales and advertising efficiency | Process two files in parallel → combine → two outputs in parallel | Seller scorecard and budget review brief |
| [Example 3](example%203/README.md) | Repair unreliable sales data without guessing | Audit → repair → independent review → targeted rework if needed | Clean data, quarantine file and quality report |
| [Example 4](example%204/README.md) | Report on a roughly 100 MB file | Profile → full-file aggregation → independent verification and report | Regional summary, report and processing checks |
| [Example 5](example%205/README.md) | Report from Supabase transactions and customers | Discover schema → query and reconcile → report | Customer KPIs, HTML report and query checks |

Examples 1–4 include local CSV inputs. Example 5 requires your authenticated read-only Supabase connection. Agent definitions, `CLAUDE.md`, `working/` and `outputs/` are created by Cowork only after approval. These reporting workflows have not been executed.

The existing `download_files.zip` remains the Examples 1–3 package. Download Example 4 separately from [example_4_download.zip](example_4_download.zip), and Example 5 from [example_5_download.zip](example_5_download.zip). Each new ZIP includes its own example folder and instructions.

Examples 1–4 use INR and fictional, simplified data. For Examples 1–3, GMV is booking value across all statuses; delivered GMV filters `DELIVERED`. Neither is profit. Their seller regions mean seller location. Example 4 uses customer regions and its own data notes. Example 5 must verify currency, geography and measure definitions from the actual schema.

Use actual subagents where available. If unavailable, the AI must disclose the limitation and perform the same roles sequentially with saved handoffs. Keep source files unchanged and work within the selected local folder.
