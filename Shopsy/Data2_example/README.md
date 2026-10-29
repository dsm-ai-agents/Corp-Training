# Data workflow examples

Three local-folder exercises using synthetic Shopsy training data for 1–28 October 2026. Open an example folder in Claude Cowork, read its README, and paste its prompt. Review the proposed architecture before approving execution.

| Example | Objective | Workflow | Final outputs |
| --- | --- | --- | --- |
| [Example 1](example%201/README.md) | Report regional sales performance | Clean → summarize → PowerPoint and dashboard in parallel | Executive slide and regional dashboard |
| [Example 2](example%202/README.md) | Compare seller sales and advertising efficiency | Process two files in parallel → combine → two outputs in parallel | Seller scorecard and budget review brief |
| [Example 3](example%203/README.md) | Repair unreliable sales data without guessing | Audit → repair → independent review → targeted rework if needed | Clean data, quarantine file and quality report |

Each `inputs/` folder contains the required CSVs. Agent definitions, `CLAUDE.md`, `working/` and `outputs/` are created by Cowork only after approval. These workflows have not been executed.

All amounts are INR. GMV is booking value across all statuses; delivered GMV filters `DELIVERED`. Neither is profit. The data is fictional and simplified. Seller region means seller location, not customer location.

Use actual subagents where available. If unavailable, the AI must disclose the limitation and perform the same roles sequentially with saved handoffs. Keep source files unchanged and work within the selected local folder.
