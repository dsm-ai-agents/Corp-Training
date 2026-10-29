# Verified schema reference

Metadata inspected on 30 October 2026 in **DSM INTERNAL OPS** (`yntdrviikfsedihhcfdy`). No business rows were retrieved and no reporting workflow was executed. This example uses the `tbl_` pair; other similarly named tables in the project are outside its scope.

## public.tbl_trasnactions

| Exact column | PostgreSQL type |
| --- | --- |
| Transaction_ID | bigint |
| Date_of_Purchase | text |
| Customer_ID | bigint |
| Product_Category | text |
| Product_Name | text |
| Units | bigint |
| Price | double precision |
| Discounts | double precision |
| Returned | boolean |
| Mode_of_Payment | text |
| Purchase_Channel | text |

## public.tbl_customers

| Exact column | PostgreSQL type |
| --- | --- |
| Customer_ID | bigint |
| Customer_Name | text |
| Customer_Email | text |
| Customer_Number | text |
| Age | bigint |
| Gender | text |
| Location | text |

All listed columns are nullable. Catalog inspection returned no declared constraints on either table, including no primary, unique or foreign keys. Row-level security is enabled on both tables. These metadata facts do not establish data uniqueness, completeness or the rows visible through the participant's connection.

Candidate join: `t."Customer_ID" = c."Customer_ID"`. Validate uniqueness of the customer key and transaction grain before joining; use a left join after resolving duplicate keys so unmatched transactions remain visible. Do not silently pick one duplicate customer record.

`Date_of_Purchase` needs format validation before date filtering. Confirm whether `Price` is per unit or per transaction, whether `Discounts` is an amount or percentage and its basis, and the currency. No currency, explicit revenue or transaction-status column exists. Use `Returned` as a nullable Boolean, not a general payment or delivery status.

Count transactions only after validating `Transaction_ID` grain. Active customers are distinct non-null customer IDs with qualifying transactions in the period. Repeat-customer share is qualifying customers with at least two validated transactions divided by active customers; report unmatched customer IDs separately. Return-rate denominators and null treatment must be explicit. Monetary fields use floating-point storage, so agree rounding and reconciliation tolerance.

Identifiers in SQL require their exact spelling and casing, for example `public.tbl_trasnactions` and `t."Date_of_Purchase"`.
