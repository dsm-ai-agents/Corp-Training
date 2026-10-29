# Example 5 — Supabase customer reporting

**Problem and objective:** Combine customer and transaction data to report purchasing patterns, customer activity and returns.

**Inputs:** Project **DSM INTERNAL OPS** (`yntdrviikfsedihhcfdy`), `public.tbl_trasnactions` and `public.tbl_customers`, an approved reporting period and a read-only connection. The spelling `tbl_trasnactions` is intentional. Exact columns and types are in `SCHEMA_REFERENCE.md`.

**Processing:** Verify schema and definitions → join on `"Customer_ID"` and reconcile → create the report.

**Outputs:** `customer_kpis.csv`, `customer_report.html` and `query_checks.md` in `outputs/`; read-only queries and definitions in `working/`.

**Challenges:** Mixed-case columns require SQL double quotes. Purchase dates are text. All columns are nullable and neither table has declared key constraints. Price, discount units and currency need confirmation; do not invent revenue formulas.

## Prompt

```text
Create a customer performance report in Supabase project DSM INTERNAL OPS (yntdrviikfsedihhcfdy).
Use public.tbl_trasnactions: "Transaction_ID", "Date_of_Purchase", "Customer_ID", "Product_Category", "Product_Name", "Units", "Price", "Discounts", "Returned", "Mode_of_Payment", "Purchase_Channel".
Join to public.tbl_customers on "Customer_ID"; use "Location" for geography. Other customer columns are "Customer_Name", "Customer_Email", "Customer_Number", "Age", "Gender"; do not export personal contact details.
Before creating files or querying business data, confirm the reporting period and show the workflow, folders and outputs for approval.
After approval, create CLAUDE.md with the goal, inputs, outputs and agent roles. Create agents/:
- agent_1_validate.md: verify SCHEMA_REFERENCE.md, validate text purchase dates, nulls and key uniqueness; confirm transaction grain, currency and Price/Discounts meaning before monetary calculations.
- agent_2_query.md: use read-only queries to join on "Customer_ID", preserve and flag unmatched transactions, reconcile counts and amounts, and save validated aggregates and queries in working/.
- agent_3_report.md: create outputs/customer_kpis.csv, outputs/customer_report.html and outputs/query_checks.md with purchase trends, units, returns, location/category/channel performance, active customers and repeat-customer share within the period. Include monetary KPIs only after definitions are confirmed.
Run 1 → 2 → 3. Quote mixed-case columns exactly. Do not assume keys are unique or dates are ISO; keep null Returned values distinct from false. Record filters, denominators and extraction time.
Keep reports local; respect access restrictions, verify result completeness and paginate when needed. Never change database data, schema or permissions. Disclose unavailable tools or subagent support.
```
