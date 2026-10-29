# Connection setup

Use **DSM INTERNAL OPS**, project reference `yntdrviikfsedihhcfdy`, and the verified tables `public.tbl_trasnactions` and `public.tbl_customers`. Supply the reporting period and reporting time zone before starting. Do not place passwords or API secrets in this folder or the prompt.

Use an authenticated Supabase connection supported by your AI environment, scoped to this project in read-only mode. Supabase MCP supports `project_ref` and `read_only=true`; follow the [official setup guide](https://supabase.com/docs/guides/ai-tools/mcp) for your client's authentication steps. Verify client support and available tools.

Only table listings and schema/constraint metadata were inspected on 30 October 2026. No business records were retrieved, no data was changed and no report was run. The package contains schema information, not customer data or credentials. Recheck the schema at execution time using `SCHEMA_REFERENCE.md`.

Reports must state accessible population and filters. Permission-limited results need not represent all company data. Use a consistent extraction snapshot where supported, or document the extraction window and any differences from concurrent updates.
