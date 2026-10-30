# Dataset definitions

Fictional transaction-line data, generated reproducibly with seed 20261029. Dates cover 1 January–30 September 2026. One unique `transaction_id` per row; each row is a complete, single-line order in this simplified model. Customers and sellers repeat. All monetary amounts are INR; timestamps and dates use Indian local time.

| Fields | Meaning |
| --- | --- |
| transaction_id, customer_id, seller_id | Synthetic identifiers; transaction ID is unique |
| order_date, order_hour | Order date and local hour, 0–23 |
| region, city | Customer region and city; each customer has a stable city |
| category, product_id | Product category and stable product identifier |
| channel, payment_method | Acquisition channel and payment method |
| status | DELIVERED, RETURNED, CANCELLED or READY_TO_SHIP at the synthetic reporting cutoff |
| units, unit_price_inr | Positive unit count and pre-discount unit price |
| discount_rate | Decimal discount fraction |
| gross_amount_inr | Units × unit price, before discount, across all statuses |
| discount_amount_inr | Gross amount × discount rate, rounded to two decimals |
| booked_amount_inr | Gross amount minus discount, including cancelled and returned bookings |
| refund_amount_inr | Full booked amount for RETURNED rows; zero otherwise |
| shipping_fee_inr | Separate modeled fee, excluded from booked amount and refund calculations |
| delivery_days | Days to delivery for delivered/returned rows; blank for cancelled/pending rows |

Delivered value filters `status=DELIVERED`. It already excludes returned rows; do not subtract refunds again. This dataset does not model accounting revenue, margin, tax, repeat order lifecycle events or customer identities.

Compute order counts by counting rows. Average order value uses the matching population's sum of booked amount divided by order count. Return rates must state their denominator. Do not sum or simply average row-level discount rates to report the overall effective discount.

File size targets 100,000,000 bytes (decimal 100 MB, about 95.4 MiB), rounded up to the next complete CSV record. ZIP compression reduces download size; the extracted CSV remains approximately 100 MB. The file is intentionally clean; observed commercial variation is synthetic, not a claim about Shopsy.
