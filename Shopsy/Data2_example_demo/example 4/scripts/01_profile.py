"""Agent 1 - Data Profiler.

Streams every row of inputs/regional_transactions_100mb.csv (standard library only)
and writes working/profile.json and working/profile_summary.md.
"""
import csv
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE, "inputs", "regional_transactions_100mb.csv")
MANIFEST_PATH = os.path.join(BASE, "inputs", "file_manifest.json")
WORK = os.path.join(BASE, "working")
DISTINCT_CAP = 5000
TOL = Decimal("0.01")
TOP_COLS = ["region", "city", "category", "channel", "payment_method", "status", "order_hour"]
MONEY = ["unit_price_inr", "gross_amount_inr", "discount_amount_inr", "booked_amount_inr",
         "refund_amount_inr", "shipping_fee_inr"]
INT_COLS = ["order_hour", "units", "delivery_days"]
DEC_COLS = MONEY + ["discount_rate"]
DATE_COLS = ["order_date"]
TOTAL_COLS = ["gross_amount_inr", "discount_amount_inr", "booked_amount_inr",
              "refund_amount_inr", "shipping_fee_inr"]


def file_checks(manifest):
    size = os.path.getsize(CSV_PATH)
    h = hashlib.sha256()
    with open(CSV_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    sha = h.hexdigest()
    return {
        "bytes_actual": size, "bytes_expected": manifest["bytes"],
        "bytes_match": size == manifest["bytes"],
        "sha256_actual": sha, "sha256_expected": manifest["sha256"],
        "sha256_match": sha == manifest["sha256"].lower(),
    }


class ColStats:
    def __init__(self, name):
        self.name = name
        self.blank = 0
        self.distinct = set()
        self.capped = False
        self.counter = Counter() if name in TOP_COLS else None
        self.min = None
        self.max = None
        self.kinds = Counter()  # int / decimal / date / text

    def add(self, v):
        if v is None or v.strip() == "":
            self.blank += 1
            return
        if not self.capped:
            self.distinct.add(v)
            if len(self.distinct) > DISTINCT_CAP:
                self.capped = True
                self.distinct = None
        if self.counter is not None:
            self.counter[v] += 1
        n = self.name
        val = None
        if n in INT_COLS:
            try:
                val = int(v); self.kinds["integer"] += 1
            except ValueError:
                self.kinds["text"] += 1
        elif n in DEC_COLS:
            try:
                val = Decimal(v); self.kinds["decimal"] += 1
            except InvalidOperation:
                self.kinds["text"] += 1
        elif n in DATE_COLS:
            try:
                val = date.fromisoformat(v); self.kinds["date"] += 1
            except ValueError:
                self.kinds["text"] += 1
        else:
            self.kinds["text"] += 1
        if val is not None:
            if self.min is None or val < self.min:
                self.min = val
            if self.max is None or val > self.max:
                self.max = val

    def result(self, rows):
        kind = self.kinds.most_common(1)[0][0] if self.kinds else "empty"
        out = {
            "inferred_type": kind,
            "type_parse_counts": dict(self.kinds),
            "null_blank_count": self.blank,
            "non_blank_count": rows - self.blank,
            "distinct_count": None if self.capped else len(self.distinct),
            "distinct_capped": self.capped,
            "distinct_cap": DISTINCT_CAP,
        }
        if self.capped:
            out["distinct_count_note"] = f"more than {DISTINCT_CAP} distinct values"
        if self.min is not None:
            out["min"] = str(self.min)
            out["max"] = str(self.max)
        if self.counter is not None:
            out["top_values"] = [[k, c] for k, c in self.counter.most_common(10)]
            out["all_value_count"] = len(self.counter)
        return out


def main():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)
    checks = file_checks(manifest)

    rows = 0
    bad_width = 0
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        idx = {c: i for i, c in enumerate(header)}
        stats = [ColStats(c) for c in header]
        seen_ids = set()
        dup_ids = 0
        q = Counter()
        q_examples = defaultdict(list)
        delivery_pattern = defaultdict(lambda: {"blank": 0, "non_blank": 0})
        totals = {c: Decimal("0") for c in TOTAL_COLS}
        by_status = defaultdict(lambda: {"rows": 0, **{c: Decimal("0") for c in TOTAL_COLS}})
        units_total = 0
        months = Counter()

        def flag(name, tid):
            q[name] += 1
            if len(q_examples[name]) < 5:
                q_examples[name].append(tid)

        for r in reader:
            rows += 1
            if len(r) != len(header):
                bad_width += 1
                continue
            for i, s in enumerate(stats):
                s.add(r[i])
            tid = r[idx["transaction_id"]]
            if tid in seen_ids:
                dup_ids += 1
            else:
                seen_ids.add(tid)
            status = r[idx["status"]]
            try:
                units = int(r[idx["units"]])
                price = Decimal(r[idx["unit_price_inr"]])
                rate = Decimal(r[idx["discount_rate"]])
                gross = Decimal(r[idx["gross_amount_inr"]])
                disc = Decimal(r[idx["discount_amount_inr"]])
                booked = Decimal(r[idx["booked_amount_inr"]])
                refund = Decimal(r[idx["refund_amount_inr"]])
                ship = Decimal(r[idx["shipping_fee_inr"]])
            except (ValueError, InvalidOperation):
                flag("unparseable_numeric", tid)
                continue
            if abs(gross - units * price) > TOL:
                flag("gross_ne_units_x_price", tid)
            if abs(disc - (gross * rate).quantize(Decimal("0.01"))) > TOL:
                flag("discount_ne_round_gross_x_rate", tid)
            if abs(booked - (gross - disc)) > TOL:
                flag("booked_ne_gross_minus_discount", tid)
            if status == "RETURNED":
                if abs(refund - booked) > TOL:
                    flag("refund_ne_booked_for_returned", tid)
            elif abs(refund) > TOL:
                flag("refund_nonzero_for_non_returned", tid)
            if units <= 0:
                flag("units_not_positive", tid)
            dd = r[idx["delivery_days"]].strip()
            delivery_pattern[status]["blank" if dd == "" else "non_blank"] += 1
            units_total += units
            months[r[idx["order_date"]][:7]] += 1
            vals = {"gross_amount_inr": gross, "discount_amount_inr": disc,
                    "booked_amount_inr": booked, "refund_amount_inr": refund,
                    "shipping_fee_inr": ship}
            bs = by_status[status]
            bs["rows"] += 1
            for c in TOTAL_COLS:
                totals[c] += vals[c]
                bs[c] += vals[c]

    checks["data_rows_actual"] = rows
    checks["data_rows_expected"] = manifest["data_rows"]
    checks["data_rows_match"] = rows == manifest["data_rows"]
    checks["columns_actual"] = len(header)
    checks["columns_expected"] = manifest["columns"]
    checks["columns_match"] = len(header) == manifest["columns"]
    checks["header"] = header
    checks["rows_with_wrong_field_count"] = bad_width
    checks["all_passed"] = all(checks[k] for k in
                               ["bytes_match", "sha256_match", "data_rows_match", "columns_match"]) and bad_width == 0

    # delivery_days rule: blank for CANCELLED/READY_TO_SHIP, filled for DELIVERED/RETURNED
    dd_viol = 0
    for st, p in delivery_pattern.items():
        if st in ("DELIVERED", "RETURNED"):
            dd_viol += p["blank"]
        else:
            dd_viol += p["non_blank"]

    quality_names = ["gross_ne_units_x_price", "discount_ne_round_gross_x_rate",
                     "booked_ne_gross_minus_discount", "refund_ne_booked_for_returned",
                     "refund_nonzero_for_non_returned", "units_not_positive", "unparseable_numeric"]
    quality = {
        "tolerance_inr": str(TOL),
        "duplicate_transaction_id_count": dup_ids,
        "unique_transaction_ids": len(seen_ids),
        "checks": {n: {"failures": q[n], "pass": q[n] == 0, "example_ids": q_examples[n]}
                   for n in quality_names},
        "delivery_days_by_status": {k: dict(v) for k, v in sorted(delivery_pattern.items())},
        "delivery_days_rule": "blank for CANCELLED/READY_TO_SHIP; populated for DELIVERED/RETURNED",
        "delivery_days_rule_violations": dd_viol,
    }
    quality["all_passed"] = (dup_ids == 0 and dd_viol == 0
                             and all(v["pass"] for v in quality["checks"].values()))

    def s(d):
        return {k: (str(v) if isinstance(v, Decimal) else v) for k, v in d.items()}

    control = {
        "row_count": rows,
        "units_total": units_total,
        "sums_inr": s(totals),
        "effective_discount_rate_sum_discount_over_sum_gross":
            str((totals["discount_amount_inr"] / totals["gross_amount_inr"]).quantize(Decimal("0.000001"))),
        "rows_by_status": {k: v["rows"] for k, v in sorted(by_status.items())},
        "sums_by_status_inr": {k: s(v) for k, v in sorted(by_status.items())},
        "rows_by_month": dict(sorted(months.items())),
        "reconciliation": {
            "sum_status_rows_equals_total": sum(v["rows"] for v in by_status.values()) == rows,
            "booked_equals_gross_minus_discount":
                totals["booked_amount_inr"] == totals["gross_amount_inr"] - totals["discount_amount_inr"],
            "refund_equals_returned_booked":
                totals["refund_amount_inr"] == by_status["RETURNED"]["booked_amount_inr"],
        },
    }

    profile = {
        "source_file": "inputs/regional_transactions_100mb.csv",
        "processing": {"rows_streamed": rows, "complete": True, "sampled": False,
                       "python": sys.version.split()[0], "libraries": "standard library only"},
        "file_checks": checks,
        "columns": {c: st.result(rows) for c, st in zip(header, stats)},
        "quality": quality,
        "control_totals": control,
    }
    os.makedirs(WORK, exist_ok=True)
    with open(os.path.join(WORK, "profile.json"), "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    write_summary(profile)
    print(json.dumps({"rows": rows, "file_checks_passed": checks["all_passed"],
                      "bytes_match": checks["bytes_match"], "sha256_match": checks["sha256_match"],
                      "rows_match": checks["data_rows_match"], "quality_passed": quality["all_passed"],
                      "dup_ids": dup_ids, "dd_violations": dd_viol,
                      "quality_failures": {n: q[n] for n in quality_names},
                      "control": control["sums_inr"], "by_status": control["rows_by_status"],
                      "eff_disc": control["effective_discount_rate_sum_discount_over_sum_gross"]},
                     indent=1))


MEANING = {
    "transaction_id": "Unique synthetic transaction ID (one per row = one order)",
    "customer_id": "Synthetic customer ID (repeats)",
    "seller_id": "Synthetic seller ID (repeats)",
    "order_date": "Order date (IST)",
    "order_hour": "Local order hour 0-23",
    "region": "Customer region",
    "city": "Customer city (stable per customer)",
    "category": "Product category",
    "product_id": "Stable product ID",
    "channel": "Acquisition channel",
    "payment_method": "Payment method",
    "status": "Order status at reporting cutoff",
    "units": "Positive unit count",
    "unit_price_inr": "Pre-discount unit price, INR",
    "discount_rate": "Decimal discount fraction",
    "gross_amount_inr": "units x unit_price, before discount",
    "discount_amount_inr": "round(gross x discount_rate, 2)",
    "booked_amount_inr": "gross - discount (all statuses)",
    "refund_amount_inr": "= booked for RETURNED, else 0",
    "shipping_fee_inr": "Separate modelled fee; excluded from booked/refund",
    "delivery_days": "Days to delivery; blank for CANCELLED/READY_TO_SHIP",
}


def pf(b):
    return "PASS" if b else "FAIL"


def fmt(x):
    return f"{Decimal(x):,.2f}"


def write_summary(p):
    fc, qu, ct, cols = p["file_checks"], p["quality"], p["control_totals"], p["columns"]
    L = []
    L.append("# Data Profile - regional_transactions_100mb.csv\n")
    L.append(f"Profiled by `scripts/01_profile.py` by streaming **all {fc['data_rows_actual']:,} data rows** "
             "(no sampling, standard-library Python, `decimal.Decimal` for money).\n")
    L.append("## What the dataset is\n")
    L.append("Fictional (synthetic, seed 20261029) Shopsy-style e-commerce transactions, Jan-Sep 2026, amounts in INR, "
             "Indian local time. **Grain: one row = one transaction = one single-line order**, keyed by unique "
             "`transaction_id`. Customers, sellers and products repeat across rows.\n")
    L.append("## File checks (vs `inputs/file_manifest.json`)\n")
    L.append("| Check | Actual | Expected | Result |\n| --- | --- | --- | --- |")
    L.append(f"| Bytes | {fc['bytes_actual']:,} | {fc['bytes_expected']:,} | {pf(fc['bytes_match'])} |")
    L.append(f"| SHA-256 | `{fc['sha256_actual'][:16]}...` | `{fc['sha256_expected'][:16]}...` | {pf(fc['sha256_match'])} |")
    L.append(f"| Data rows | {fc['data_rows_actual']:,} | {fc['data_rows_expected']:,} | {pf(fc['data_rows_match'])} |")
    L.append(f"| Columns | {fc['columns_actual']} | {fc['columns_expected']} | {pf(fc['columns_match'])} |")
    L.append(f"| Rows with wrong field count | {fc['rows_with_wrong_field_count']} | 0 | {pf(fc['rows_with_wrong_field_count'] == 0)} |\n")
    L.append("## Columns\n")
    L.append("| Column | Type | Blanks | Distinct | Min | Max | Meaning |\n| --- | --- | --- | --- | --- | --- | --- |")
    for c, r in cols.items():
        d = f">{DISTINCT_CAP:,} (capped)" if r["distinct_capped"] else f"{r['distinct_count']:,}"
        L.append(f"| {c} | {r['inferred_type']} | {r['null_blank_count']:,} | {d} | {r.get('min', '')} | "
                 f"{r.get('max', '')} | {MEANING.get(c, '')} |")
    L.append("\n## Categorical values (row counts)\n")
    for c in TOP_COLS:
        r = cols[c]
        extra = "" if r["all_value_count"] <= 10 else f" (top 10 of {r['all_value_count']})"
        vals = ", ".join(f"{k} {v:,}" for k, v in r["top_values"])
        L.append(f"- **{c}**{extra}: {vals}")
    L.append("\n## Quality checks (tolerance INR 0.01)\n")
    L.append("| Check | Failures | Result |\n| --- | --- | --- |")
    L.append(f"| Duplicate transaction_id | {qu['duplicate_transaction_id_count']:,} | {pf(qu['duplicate_transaction_id_count'] == 0)} |")
    for n, v in qu["checks"].items():
        L.append(f"| {n} | {v['failures']:,} | {pf(v['pass'])} |")
    L.append(f"| delivery_days blank pattern ({qu['delivery_days_rule']}) | {qu['delivery_days_rule_violations']:,} | "
             f"{pf(qu['delivery_days_rule_violations'] == 0)} |")
    L.append("\ndelivery_days by status: " + "; ".join(
        f"{k}: blank {v['blank']:,} / filled {v['non_blank']:,}" for k, v in qu["delivery_days_by_status"].items()))
    L.append(f"\n**Overall quality: {pf(qu['all_passed'])}**\n")
    L.append("## Control totals (INR)\n")
    L.append("| Measure | Total |\n| --- | --- |")
    L.append(f"| Rows (orders) | {ct['row_count']:,} |")
    L.append(f"| Units | {ct['units_total']:,} |")
    for k, v in ct["sums_inr"].items():
        L.append(f"| {k} | {fmt(v)} |")
    L.append(f"| Effective discount (sum discount / sum gross) | {Decimal(ct['effective_discount_rate_sum_discount_over_sum_gross']) * 100:.4f}% |")
    L.append("\n| Status | Rows | Booked INR | Refund INR |\n| --- | --- | --- | --- |")
    for st, v in ct["sums_by_status_inr"].items():
        L.append(f"| {st} | {v['rows']:,} | {fmt(v['booked_amount_inr'])} | {fmt(v['refund_amount_inr'])} |")
    L.append("\nRows by month: " + ", ".join(f"{k} {v:,}" for k, v in ct["rows_by_month"].items()))
    rc = ct["reconciliation"]
    L.append(f"\nReconciliation: status rows sum to total {pf(rc['sum_status_rows_equals_total'])}; "
             f"sum booked = sum gross - sum discount {pf(rc['booked_equals_gross_minus_discount'])}; "
             f"sum refund = RETURNED booked {pf(rc['refund_equals_returned_booked'])}.\n")
    L.append("## Recommendations for Agent 2 (transaction-level analysis)\n")
    L.append("**Dimensions:** order_date (roll up to month `YYYY-MM`; also week/day-of-week), order_hour, region, city, "
             "category, channel, payment_method, status. High-cardinality IDs (customer_id, seller_id, product_id) "
             "suit top-N rankings or distinct counts, not chart axes.\n")
    L.append("**Metrics (ratios of sums, denominators stated):**")
    L.append("- Orders = row count; Units = sum units")
    L.append("- Gross = sum gross_amount_inr; Discount = sum discount_amount_inr; Booked = sum booked_amount_inr (all statuses)")
    L.append("- Delivered value = sum booked where status = DELIVERED (do not subtract refunds again)")
    L.append("- Refunds = sum refund_amount_inr (RETURNED rows only); Shipping = sum shipping_fee_inr (report separately)")
    L.append("- AOV = sum booked / orders of the same population")
    L.append("- Effective discount = sum discount / sum gross (never average discount_rate)")
    L.append("- Return rate = RETURNED rows / all rows (also offer RETURNED / (DELIVERED + RETURNED)); cancel rate = CANCELLED rows / all rows; state the denominator")
    L.append("- Avg delivery days = mean delivery_days over DELIVERED + RETURNED rows only (blank otherwise)")
    L.append("\nAgent 2 should re-verify its totals against the control totals above.")
    with open(os.path.join(WORK, "profile_summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
