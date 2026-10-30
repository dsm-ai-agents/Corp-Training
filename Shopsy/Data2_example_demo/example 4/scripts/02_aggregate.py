"""Agent 2 - Transaction Analyst.

Streams every row of inputs/regional_transactions_100mb.csv once (standard library only,
decimal.Decimal for money), computes headline KPIs, breakdowns, trends and exceptions,
reconciles to Agent 1's control totals in working/profile.json, and writes:
  working/analysis.json
  working/monthly_region_summary.csv
(working/analysis_summary.md is written by Agent 2 from these outputs.)
Exit code 0 = reconciliation passed, 1 = a control-total check failed.
"""
import calendar
import csv
import json
import os
import sys
import time
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "inputs", "regional_transactions_100mb.csv")
PROFILE = os.path.join(ROOT, "working", "profile.json")
OUT_JSON = os.path.join(ROOT, "working", "analysis.json")
OUT_CSV = os.path.join(ROOT, "working", "monthly_region_summary.csv")
OUT_MD = os.path.join(ROOT, "working", "analysis_summary.md")

ZERO = Decimal("0")
CENT = Decimal("0.01")
EXCEPTION_PP = Decimal("1.5")

# Accumulator slots
ORD, GROSS, DISC, BOOK, DELIV, REF, SHIP, N_DEL, N_RET, N_CAN, N_RTS, DD_SUM, DD_N, UNITS = range(14)


def new_acc():
    return [0, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO, 0, 0, 0, 0, 0, 0, 0]


def q2(x):
    return float(Decimal(x).quantize(CENT, rounding=ROUND_HALF_UP))


def pct(num, den):
    """Percentage as Decimal (unrounded) or None."""
    if not den:
        return None
    return Decimal(num) * 100 / Decimal(den)


def pct2(num, den):
    v = pct(num, den)
    return None if v is None else q2(v)


def summarise(a):
    orders = a[ORD]
    return {
        "orders": orders,
        "units": a[UNITS],
        "gross_inr": q2(a[GROSS]),
        "discount_inr": q2(a[DISC]),
        "booked_inr": q2(a[BOOK]),
        "delivered_value_inr": q2(a[DELIV]),
        "refunds_inr": q2(a[REF]),
        "shipping_fees_inr": q2(a[SHIP]),
        "aov_inr": q2(a[BOOK] / orders) if orders else None,
        "delivered_orders": a[N_DEL],
        "returned_orders": a[N_RET],
        "cancelled_orders": a[N_CAN],
        "ready_to_ship_orders": a[N_RTS],
        "return_rate_pct": pct2(a[N_RET], a[N_DEL] + a[N_RET]),
        "return_rate_of_all_orders_pct": pct2(a[N_RET], orders),
        "cancellation_rate_pct": pct2(a[N_CAN], orders),
        "effective_discount_pct": pct2(a[DISC], a[GROSS]),
        "avg_delivery_days_delivered": q2(Decimal(a[DD_SUM]) / a[DD_N]) if a[DD_N] else None,
    }


def main():
    t0 = time.time()
    with open(PROFILE, encoding="utf-8") as f:
        profile = json.load(f)
    ct = profile["control_totals"]

    total = new_acc()
    dims = {k: {} for k in ("month", "region", "month_region", "category", "channel",
                            "payment_method", "status", "city", "order_hour")}
    customers, sellers, products = set(), set(), set()
    dates_by_month = {}
    rows = 0

    with open(SRC, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        ix = {name: i for i, name in enumerate(header)}
        i_cust, i_sell, i_prod = ix["customer_id"], ix["seller_id"], ix["product_id"]
        i_date, i_hour, i_reg, i_city = ix["order_date"], ix["order_hour"], ix["region"], ix["city"]
        i_cat, i_chan, i_pay, i_stat = ix["category"], ix["channel"], ix["payment_method"], ix["status"]
        i_units, i_gross, i_disc, i_book = ix["units"], ix["gross_amount_inr"], ix["discount_amount_inr"], ix["booked_amount_inr"]
        i_ref, i_ship, i_dd = ix["refund_amount_inr"], ix["shipping_fee_inr"], ix["delivery_days"]
        d_month, d_region, d_mr, d_cat = dims["month"], dims["region"], dims["month_region"], dims["category"]
        d_chan, d_pay, d_stat, d_city, d_hour = dims["channel"], dims["payment_method"], dims["status"], dims["city"], dims["order_hour"]

        for r in reader:
            rows += 1
            month = r[i_date][:7]
            region = r[i_reg]
            status = r[i_stat]
            units = int(r[i_units])
            gross = Decimal(r[i_gross])
            disc = Decimal(r[i_disc])
            book = Decimal(r[i_book])
            ref = Decimal(r[i_ref])
            ship = Decimal(r[i_ship])
            dd = r[i_dd]
            customers.add(r[i_cust]); sellers.add(r[i_sell]); products.add(r[i_prod])
            dates_by_month.setdefault(month, set()).add(r[i_date])

            keys = (
                (d_month, month), (d_region, region), (d_mr, (month, region)),
                (d_cat, r[i_cat]), (d_chan, r[i_chan]), (d_pay, r[i_pay]),
                (d_stat, status), (d_city, r[i_city]), (d_hour, int(r[i_hour])),
            )
            accs = [total]
            for d, k in keys:
                a = d.get(k)
                if a is None:
                    a = d[k] = new_acc()
                accs.append(a)

            is_del = status == "DELIVERED"
            for a in accs:
                a[ORD] += 1
                a[UNITS] += units
                a[GROSS] += gross
                a[DISC] += disc
                a[BOOK] += book
                a[REF] += ref
                a[SHIP] += ship
                if is_del:
                    a[DELIV] += book
                    a[N_DEL] += 1
                    a[DD_SUM] += int(dd)
                    a[DD_N] += 1
                elif status == "RETURNED":
                    a[N_RET] += 1
                elif status == "CANCELLED":
                    a[N_CAN] += 1
                elif status == "READY_TO_SHIP":
                    a[N_RTS] += 1

    elapsed = time.time() - t0

    # ---------------- Reconciliation ----------------
    checks = []

    def chk(name, actual, expected):
        checks.append({"check": name, "actual": str(actual), "expected": str(expected),
                       "pass": str(actual) == str(expected)})

    chk("row_count", rows, ct["row_count"])
    chk("units_total", total[UNITS], ct["units_total"])
    sums = ct["sums_inr"]
    chk("gross_amount_inr", total[GROSS], Decimal(sums["gross_amount_inr"]))
    chk("discount_amount_inr", total[DISC], Decimal(sums["discount_amount_inr"]))
    chk("booked_amount_inr", total[BOOK], Decimal(sums["booked_amount_inr"]))
    chk("refund_amount_inr", total[REF], Decimal(sums["refund_amount_inr"]))
    chk("shipping_fee_inr", total[SHIP], Decimal(sums["shipping_fee_inr"]))
    for st, n in ct["rows_by_status"].items():
        chk(f"rows_status_{st}", dims["status"].get(st, new_acc())[ORD], n)
    for st, s in ct["sums_by_status_inr"].items():
        chk(f"booked_status_{st}", dims["status"].get(st, new_acc())[BOOK], Decimal(s["booked_amount_inr"]))
    for m, n in ct["rows_by_month"].items():
        chk(f"rows_month_{m}", dims["month"].get(m, new_acc())[ORD], n)
    chk("delivered_value_equals_DELIVERED_booked", total[DELIV], Decimal(ct["sums_by_status_inr"]["DELIVERED"]["booked_amount_inr"]))
    chk("booked_equals_gross_minus_discount", total[BOOK], total[GROSS] - total[DISC])
    recon_pass = all(c["pass"] for c in checks)

    # ---------------- Breakdowns ----------------
    def table(d, key_name, sort_key=None, reverse=False):
        items = list(d.items())
        items.sort(key=sort_key or (lambda kv: kv[0]), reverse=reverse)
        out = []
        for k, a in items:
            row = {key_name: k}
            row.update(summarise(a))
            out.append(row)
        return out

    by_month = table(dims["month"], "month")
    for row in by_month:
        days = len(dates_by_month[row["month"]])
        y, mo = map(int, row["month"].split("-"))
        row["days_with_orders"] = days
        row["calendar_days"] = calendar.monthrange(y, mo)[1]
        row["booked_per_day_inr"] = q2(dims["month"][row["month"]][BOOK] / days)
        row["orders_per_day"] = q2(Decimal(row["orders"]) / days)

    by_region = table(dims["region"], "region", lambda kv: kv[1][BOOK], True)
    by_mr = []
    for (m, reg), a in sorted(dims["month_region"].items()):
        row = {"month": m, "region": reg}
        row.update(summarise(a))
        by_mr.append(row)
    by_category = table(dims["category"], "category", lambda kv: kv[1][BOOK], True)
    by_channel = table(dims["channel"], "channel", lambda kv: kv[1][BOOK], True)
    by_payment = table(dims["payment_method"], "payment_method", lambda kv: kv[1][BOOK], True)
    by_status = table(dims["status"], "status", lambda kv: kv[1][ORD], True)
    by_city = table(dims["city"], "city", lambda kv: kv[1][BOOK], True)[:15]
    by_hour = table(dims["order_hour"], "order_hour")

    # ---------------- Trends ----------------
    months = sorted(dims["month"])
    regions = sorted(dims["region"])

    def mom(series):
        out = []
        prev = None
        for m, v in series:
            out.append({"month": m, "booked_inr": q2(v),
                        "mom_change_pct": None if prev in (None, ZERO) else q2((v - prev) * 100 / prev)})
            prev = v
        return out

    mom_overall = mom([(m, dims["month"][m][BOOK]) for m in months])
    per_day = [(m, dims["month"][m][BOOK] / len(dates_by_month[m])) for m in months]
    mom_per_day = []
    prev = None
    for m, v in per_day:
        mom_per_day.append({"month": m, "booked_per_day_inr": q2(v),
                            "mom_change_pct": None if prev is None else q2((v - prev) * 100 / prev)})
        prev = v
    mom_region = {reg: mom([(m, dims["month_region"].get((m, reg), new_acc())[BOOK]) for m in months])
                  for reg in regions}

    # ---------------- Exceptions ----------------
    def ret_rate(a):
        return pct(a[N_RET], a[N_DEL] + a[N_RET])

    def can_rate(a):
        return pct(a[N_CAN], a[ORD])

    def best_worst(dname, fn, label):
        items = [(k, fn(a)) for k, a in dims[dname].items()]
        items.sort(key=lambda kv: kv[1])
        return {"best_lowest": {label: items[0][0], "rate_pct": q2(items[0][1])},
                "worst_highest": {label: items[-1][0], "rate_pct": q2(items[-1][1])},
                "spread_pp": q2(items[-1][1] - items[0][1])}

    overall_ret = ret_rate(total)
    overall_can = can_rate(total)
    extremes = {
        "region_return_rate": best_worst("region", ret_rate, "region"),
        "region_cancellation_rate": best_worst("region", can_rate, "region"),
        "category_return_rate": best_worst("category", ret_rate, "category"),
        "category_cancellation_rate": best_worst("category", can_rate, "category"),
    }
    threshold = overall_ret + EXCEPTION_PP
    exceptions = []
    for (m, reg), a in sorted(dims["month_region"].items()):
        r = ret_rate(a)
        if r is not None and r > threshold:
            exceptions.append({"month": m, "region": reg, "return_rate_pct": q2(r),
                               "pp_above_overall": q2(r - overall_ret),
                               "returned_orders": a[N_RET], "delivered_plus_returned": a[N_DEL] + a[N_RET]})
    mr_rates = sorted(((ret_rate(a), m, reg) for (m, reg), a in dims["month_region"].items()), reverse=True)
    top_mr_return = [{"month": m, "region": reg, "return_rate_pct": q2(r), "pp_vs_overall": q2(r - overall_ret)}
                     for r, m, reg in mr_rates[:5]]
    bottom_mr_return = [{"month": m, "region": reg, "return_rate_pct": q2(r), "pp_vs_overall": q2(r - overall_ret)}
                        for r, m, reg in mr_rates[-5:]]

    # ---------------- Headline KPIs ----------------
    head = summarise(total)
    kpis = {
        "orders": rows,
        "units": total[UNITS],
        "gross_inr": head["gross_inr"],
        "discount_inr": head["discount_inr"],
        "booked_value_inr": head["booked_inr"],
        "delivered_value_inr": head["delivered_value_inr"],
        "refunds_inr": head["refunds_inr"],
        "shipping_fees_inr": head["shipping_fees_inr"],
        "aov_inr": head["aov_inr"],
        "effective_discount_pct": head["effective_discount_pct"],
        "return_rate_pct": head["return_rate_pct"],
        "return_rate_of_all_orders_pct": head["return_rate_of_all_orders_pct"],
        "cancellation_rate_pct": head["cancellation_rate_pct"],
        "ready_to_ship_share_pct": pct2(total[N_RTS], rows),
        "avg_delivery_days_delivered": head["avg_delivery_days_delivered"],
        "unique_customers": len(customers),
        "unique_sellers": len(sellers),
        "unique_products": len(products),
        "delivered_orders": total[N_DEL],
        "returned_orders": total[N_RET],
        "cancelled_orders": total[N_CAN],
        "ready_to_ship_orders": total[N_RTS],
    }

    definitions = {
        "orders": "row count (one row = one single-line order)",
        "booked_value": "sum booked_amount_inr, all statuses",
        "delivered_value": "sum booked_amount_inr where status=DELIVERED (refunds not subtracted again)",
        "refunds": "sum refund_amount_inr (RETURNED rows only)",
        "shipping_fees": "sum shipping_fee_inr, reported separately; excluded from booked/refunds",
        "aov": "sum booked / order count of the same population",
        "effective_discount_pct": "sum discount_amount_inr / sum gross_amount_inr x 100",
        "return_rate_pct": "RETURNED orders / (DELIVERED + RETURNED orders) x 100",
        "return_rate_of_all_orders_pct": "RETURNED orders / all orders x 100 (secondary view)",
        "cancellation_rate_pct": "CANCELLED orders / all orders x 100",
        "avg_delivery_days_delivered": "mean delivery_days over DELIVERED rows only",
        "mom_change_pct": "(booked this month - booked prior month) / booked prior month x 100",
        "exception_rule": "month x region cell with return rate > overall return rate + 1.5 percentage points",
        "rounding": "money and rates rounded half-up to 2 dp; rates are percentages",
    }

    analysis = {
        "agent": "agent-2-analyst",
        "script": "scripts/02_aggregate.py",
        "source_file": "inputs/regional_transactions_100mb.csv",
        "processing": {"rows_streamed": rows, "complete": True, "sampled": False,
                       "single_pass": True, "money_type": "decimal.Decimal",
                       "libraries": "standard library only", "seconds": round(elapsed, 1)},
        "definitions": definitions,
        "headline_kpis": kpis,
        "breakdowns": {
            "by_month": by_month, "by_region": by_region, "by_month_region": by_mr,
            "by_category": by_category, "by_channel": by_channel, "by_payment_method": by_payment,
            "by_status": by_status, "by_city_top15_by_booked": by_city, "by_order_hour": by_hour,
        },
        "trends": {"mom_booked_overall": mom_overall, "mom_booked_per_day_overall": mom_per_day,
                   "mom_booked_by_region": mom_region},
        "exceptions": {
            "overall_return_rate_pct": q2(overall_ret),
            "overall_cancellation_rate_pct": q2(overall_can),
            "extremes": extremes,
            "month_region_return_rate_threshold_pct": q2(threshold),
            "month_region_return_rate_exceptions": exceptions,
            "top5_month_region_return_rate": top_mr_return,
            "bottom5_month_region_return_rate": bottom_mr_return,
        },
        "reconciliation": {"against": "working/profile.json control_totals", "all_passed": recon_pass,
                           "checks": checks},
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)

    # ---------------- CSV ----------------
    cols = ["month", "region", "orders", "units", "gross_inr", "discount_inr", "booked_inr",
            "delivered_value_inr", "refunds_inr", "shipping_fees_inr", "aov_inr", "delivered_orders",
            "returned_orders", "cancelled_orders", "ready_to_ship_orders", "return_rate_pct",
            "return_rate_of_all_orders_pct", "cancellation_rate_pct", "effective_discount_pct",
            "avg_delivery_days_delivered", "booked_mom_change_pct"]
    mom_lookup = {(reg, e["month"]): e["mom_change_pct"] for reg, lst in mom_region.items() for e in lst}
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for row in by_mr:
            row = dict(row)
            row["booked_mom_change_pct"] = mom_lookup.get((row["region"], row["month"]))
            w.writerow(["" if row.get(c) is None else row.get(c) for c in cols])

    print(json.dumps({"rows": rows, "seconds": round(elapsed, 1), "reconciliation_pass": recon_pass,
                      "failed_checks": [c for c in checks if not c["pass"]]}, indent=2))
    return 0 if recon_pass else 1


if __name__ == "__main__":
    sys.exit(main())
