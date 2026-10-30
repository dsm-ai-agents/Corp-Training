# Data Profile - regional_transactions_100mb.csv

Profiled by `scripts/01_profile.py` by streaming **all 640,393 data rows** (no sampling, standard-library Python, `decimal.Decimal` for money).

## What the dataset is

Fictional (synthetic, seed 20261029) Shopsy-style e-commerce transactions, Jan-Sep 2026, amounts in INR, Indian local time. **Grain: one row = one transaction = one single-line order**, keyed by unique `transaction_id`. Customers, sellers and products repeat across rows.

## File checks (vs `inputs/file_manifest.json`)

| Check | Actual | Expected | Result |
| --- | --- | --- | --- |
| Bytes | 100,000,028 | 100,000,028 | PASS |
| SHA-256 | `2af0123cf1651903...` | `2af0123cf1651903...` | PASS |
| Data rows | 640,393 | 640,393 | PASS |
| Columns | 21 | 21 | PASS |
| Rows with wrong field count | 0 | 0 | PASS |

## Columns

| Column | Type | Blanks | Distinct | Min | Max | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| transaction_id | text | 0 | >5,000 (capped) |  |  | Unique synthetic transaction ID (one per row = one order) |
| customer_id | text | 0 | >5,000 (capped) |  |  | Synthetic customer ID (repeats) |
| seller_id | text | 0 | 1,500 |  |  | Synthetic seller ID (repeats) |
| order_date | date | 0 | 273 | 2026-01-01 | 2026-09-30 | Order date (IST) |
| order_hour | integer | 0 | 24 | 0 | 23 | Local order hour 0-23 |
| region | text | 0 | 4 |  |  | Customer region |
| city | text | 0 | 8 |  |  | Customer city (stable per customer) |
| category | text | 0 | 6 |  |  | Product category |
| product_id | text | 0 | >5,000 (capped) |  |  | Stable product ID |
| channel | text | 0 | 5 |  |  | Acquisition channel |
| payment_method | text | 0 | 4 |  |  | Payment method |
| status | text | 0 | 4 |  |  | Order status at reporting cutoff |
| units | integer | 0 | 5 | 1 | 5 | Positive unit count |
| unit_price_inr | decimal | 0 | 52 | 199.00 | 2774.00 | Pre-discount unit price, INR |
| discount_rate | decimal | 0 | 5 | 0.00 | 0.20 | Decimal discount fraction |
| gross_amount_inr | decimal | 0 | 260 | 199.00 | 13870.00 | units x unit_price, before discount |
| discount_amount_inr | decimal | 0 | 677 | 0.00 | 2774.00 | round(gross x discount_rate, 2) |
| booked_amount_inr | decimal | 0 | 1,247 | 159.20 | 13870.00 | gross - discount (all statuses) |
| refund_amount_inr | decimal | 0 | 1,248 | 0.00 | 13870.00 | = booked for RETURNED, else 0 |
| shipping_fee_inr | decimal | 0 | 3 | 0.00 | 49.00 | Separate modelled fee; excluded from booked/refund |
| delivery_days | integer | 71,004 | 10 | 1 | 10 | Days to delivery; blank for CANCELLED/READY_TO_SHIP |

## Categorical values (row counts)

- **region**: North 160,877, East 160,218, West 159,933, South 159,365
- **city**: Delhi 80,512, Jaipur 80,365, Kolkata 80,249, Mumbai 80,103, Bhubaneswar 79,969, Pune 79,830, Chennai 79,743, Bengaluru 79,622
- **category**: Grocery 107,153, Home 107,084, Electronics 106,901, Furniture 106,656, Lifestyle 106,371, Footwear 106,228
- **channel**: Organic 128,836, Paid_Search 128,030, Email 127,953, Social 127,849, Direct 127,725
- **payment_method**: Wallet 160,811, Card 160,095, COD 159,855, UPI 159,632
- **status**: DELIVERED 511,560, RETURNED 57,829, CANCELLED 45,099, READY_TO_SHIP 25,905
- **order_hour** (top 10 of 24): 13 27,024, 2 27,001, 3 26,983, 16 26,834, 7 26,829, 10 26,799, 9 26,795, 15 26,761, 14 26,716, 0 26,713

## Quality checks (tolerance INR 0.01)

| Check | Failures | Result |
| --- | --- | --- |
| Duplicate transaction_id | 0 | PASS |
| gross_ne_units_x_price | 0 | PASS |
| discount_ne_round_gross_x_rate | 0 | PASS |
| booked_ne_gross_minus_discount | 0 | PASS |
| refund_ne_booked_for_returned | 0 | PASS |
| refund_nonzero_for_non_returned | 0 | PASS |
| units_not_positive | 0 | PASS |
| unparseable_numeric | 0 | PASS |
| delivery_days blank pattern (blank for CANCELLED/READY_TO_SHIP; populated for DELIVERED/RETURNED) | 0 | PASS |

delivery_days by status: CANCELLED: blank 45,099 / filled 0; DELIVERED: blank 0 / filled 511,560; READY_TO_SHIP: blank 25,905 / filled 0; RETURNED: blank 0 / filled 57,829

**Overall quality: PASS**

## Control totals (INR)

| Measure | Total |
| --- | --- |
| Rows (orders) | 640,393 |
| Units | 1,922,717 |
| gross_amount_inr | 1,992,981,058.00 |
| discount_amount_inr | 166,461,354.70 |
| booked_amount_inr | 1,826,519,703.30 |
| refund_amount_inr | 164,809,285.60 |
| shipping_fee_inr | 16,675,608.00 |
| Effective discount (sum discount / sum gross) | 8.3524% |

| Status | Rows | Booked INR | Refund INR |
| --- | --- | --- | --- |
| CANCELLED | 45,099 | 128,375,104.50 | 0.00 |
| DELIVERED | 511,560 | 1,459,123,857.35 | 0.00 |
| READY_TO_SHIP | 25,905 | 74,211,455.85 | 0.00 |
| RETURNED | 57,829 | 164,809,285.60 | 164,809,285.60 |

Rows by month: 2026-01 72,570, 2026-02 65,292, 2026-03 72,930, 2026-04 70,209, 2026-05 72,609, 2026-06 70,535, 2026-07 72,762, 2026-08 72,912, 2026-09 70,574

Reconciliation: status rows sum to total PASS; sum booked = sum gross - sum discount PASS; sum refund = RETURNED booked PASS.

## Recommendations for Agent 2 (transaction-level analysis)

**Dimensions:** order_date (roll up to month `YYYY-MM`; also week/day-of-week), order_hour, region, city, category, channel, payment_method, status. High-cardinality IDs (customer_id, seller_id, product_id) suit top-N rankings or distinct counts, not chart axes.

**Metrics (ratios of sums, denominators stated):**
- Orders = row count; Units = sum units
- Gross = sum gross_amount_inr; Discount = sum discount_amount_inr; Booked = sum booked_amount_inr (all statuses)
- Delivered value = sum booked where status = DELIVERED (do not subtract refunds again)
- Refunds = sum refund_amount_inr (RETURNED rows only); Shipping = sum shipping_fee_inr (report separately)
- AOV = sum booked / orders of the same population
- Effective discount = sum discount / sum gross (never average discount_rate)
- Return rate = RETURNED rows / all rows (also offer RETURNED / (DELIVERED + RETURNED)); cancel rate = CANCELLED rows / all rows; state the denominator
- Avg delivery days = mean delivery_days over DELIVERED + RETURNED rows only (blank otherwise)

Agent 2 should re-verify its totals against the control totals above.
