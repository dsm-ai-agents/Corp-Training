"""Agent 3 - Report Builder.
Reads working/analysis.json (+ inputs/file_manifest.json for the row check) and renders
outputs/dashboard_email.html: Gmail-safe (inline styles, tables, 680px, no scripts/URLs).
Every figure is read from the JSON; insight sentences are derived in code.
Standard library only.
"""
import json
import os
import datetime
from html import escape
from decimal import Decimal, ROUND_HALF_UP

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(BASE, "working", "analysis.json")
MANIFEST = os.path.join(BASE, "inputs", "file_manifest.json")
OUT = os.path.join(BASE, "outputs", "dashboard_email.html")

FONT = "Arial, Helvetica, sans-serif"
TXT, MUTED, BORDER = "#1f2937", "#4b5563", "#e5e7eb"
INDIGO = "#4338ca"
# (tint, accent) palette
PAL = {"indigo": ("#eef2ff", "#4338ca"), "emerald": ("#ecfdf5", "#047857"),
       "amber": ("#fffbeb", "#b45309"), "rose": ("#fff1f2", "#be123c"),
       "sky": ("#f0f9ff", "#0369a1"), "violet": ("#f5f3ff", "#6d28d9")}
REGION_COL = {"North": "#4338ca", "East": "#0891b2", "West": "#d97706", "South": "#059669"}
SERIES = ["#4338ca", "#0891b2", "#059669", "#d97706", "#db2777", "#7c3aed"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ---------- formatters ----------
def indian(n):
    """Group an integer Indian-style: 12,34,56,789."""
    s = str(int(round(abs(n))))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return ("-" if n < 0 else "") + s


def inr(v, dp=1):
    """Rupee value with Cr / L abbreviation for large values."""
    a = abs(v)
    if a >= 1e7:
        s = f"{a / 1e7:,.{dp}f} Cr"
    elif a >= 1e5:
        s = f"{a / 1e5:,.{dp}f} L"
    else:
        s = indian(a)
    return ("-" if v < 0 else "") + "₹" + s


def num(v):
    return indian(v)


def pct(v, dp=1, sign=False):
    if v is None:
        return "&ndash;"
    q = Decimal(repr(v)).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP)  # half-up, like the analyst
    return (f"{q:+}%" if sign else f"{q}%")


def mlabel(m):
    y, mo = m.split("-")
    return f"{MONTHS[int(mo) - 1]} {y}"


def share(part, whole):
    return part / whole * 100 if whole else 0.0


# ---------- HTML helpers ----------
def td(content, style="", **attr):
    a = "".join(f' {k}="{v}"' for k, v in attr.items())
    return f'<td style="font-family:{FONT};color:{TXT};font-size:14px;{style}"{a}>{content}</td>'


def table(rows_html, style="", width="100%"):
    return (f'<table role="presentation" width="{width}" cellpadding="0" cellspacing="0" border="0" '
            f'style="border-collapse:collapse;width:{width};{style}">{rows_html}</table>')


def bar_row(label, value_pct, color, right_text, label_w=130, right_w=120, sub=""):
    """Horizontal bar: label | nested-table bar (width = value_pct of max) | value text."""
    w = max(1, min(100, round(value_pct)))
    bar = table(f'<tr><td width="{w}%" style="background:{color};height:16px;font-size:0;line-height:0;'
                f'width:{w}%;">&nbsp;</td><td style="font-size:0;line-height:0;">&nbsp;</td></tr>',
                "background:#f3f4f6;")
    lab = escape(label) + (f'<br><span style="font-size:12px;color:{MUTED};">{sub}</span>' if sub else "")
    return ("<tr>" + td(lab, f"padding:5px 8px 5px 0;width:{label_w}px;font-weight:bold;", width=label_w)
            + td(bar, "padding:5px 0;")
            + td(right_text, f"padding:5px 0 5px 10px;width:{right_w}px;text-align:right;white-space:nowrap;",
                 width=right_w) + "</tr>")


def bars(items, color_fn, label_w=130, right_w=120):
    """items: list of (label, value, right_text[, sub]); bars scaled to the max value."""
    mx = max(i[1] for i in items) or 1
    rows = "".join(bar_row(i[0], i[1] / mx * 100, color_fn(k, i), i[2], label_w, right_w,
                           i[3] if len(i) > 3 else "") for k, i in enumerate(items))
    return table(rows)


def card(tone, value, label, context):
    tint, acc = PAL[tone]
    inner = (f'<div style="font-family:{FONT};font-size:12px;font-weight:bold;letter-spacing:0.5px;'
             f'text-transform:uppercase;color:{acc};">{label}</div>'
             f'<div style="font-family:{FONT};font-size:24px;font-weight:bold;color:{TXT};padding:6px 0 4px;">{value}</div>'
             f'<div style="font-family:{FONT};font-size:12px;color:{MUTED};line-height:16px;">{context}</div>')
    return td(inner, f"background:{tint};border-top:4px solid {acc};padding:14px 12px;vertical-align:top;",
              width="33%", valign="top")


def section(title, body, accent=INDIGO, intro=""):
    head = (f'<div style="font-family:{FONT};font-size:18px;font-weight:bold;color:{TXT};'
            f'border-left:5px solid {accent};padding:2px 0 2px 10px;margin:0 0 10px;">{title}</div>')
    if intro:
        head += f'<div style="font-family:{FONT};font-size:14px;color:{MUTED};margin:0 0 10px;line-height:20px;">{intro}</div>'
    return f'<tr><td style="padding:22px 24px 6px;background:#ffffff;">{head}{body}</td></tr>'


def badge(text, good):
    bg, fg = ("#dcfce7", "#166534") if good else ("#fee2e2", "#991b1b")
    return (f'<span style="font-family:{FONT};font-size:12px;font-weight:bold;background:{bg};color:{fg};'
            f'padding:2px 6px;border-radius:10px;white-space:nowrap;">{text}</span>')


def page(inner, preheader=""):
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Regional Performance Dashboard</title></head>'
            f'<body style="margin:0;padding:0;background:#f3f4f6;">'
            f'<div style="display:none;max-height:0;overflow:hidden;">{preheader}</div>'
            + table('<tr><td align="center" style="padding:16px 8px;">'
                    + table(inner, "max-width:680px;background:#ffffff;border:1px solid #e5e7eb;", "680")
                    .replace('width:680;', 'width:100%;')
                    + '</td></tr>', "background:#f3f4f6;")
            + '</body></html>')


# ---------- sections (added incrementally) ----------
def period(d):
    ms = [r["month"] for r in d["breakdowns"]["by_month"]]
    return f"{mlabel(ms[0])} &ndash; {mlabel(ms[-1])}"


def sec_header(d, man):
    p = d["processing"]
    inner = (f'<div style="font-family:{FONT};font-size:12px;letter-spacing:1px;text-transform:uppercase;color:#c7d2fe;">'
             f'Shopsy &middot; Transactions report</div>'
             f'<div style="font-family:{FONT};font-size:26px;font-weight:bold;color:#ffffff;padding:6px 0;">'
             f'Regional Performance Dashboard</div>'
             f'<div style="font-family:{FONT};font-size:14px;color:#e0e7ff;line-height:20px;">'
             f'Period: {period(d)} &nbsp;|&nbsp; {num(p["rows_streamed"])} orders processed (full file) '
             f'&nbsp;|&nbsp; Generated {datetime.date.today().strftime("%d %b %Y")}</div>')
    return f'<tr><td style="background:{INDIGO};padding:26px 24px;">{inner}</td></tr>'


def sec_kpis(d, man):
    k = d["headline_kpis"]
    deliv_share = share(k["delivered_value_inr"], k["booked_value_inr"])
    cards = [
        ("indigo", inr(k["booked_value_inr"]), "Booked value",
         f'All statuses &middot; {num(k["orders"])} orders'),
        ("emerald", inr(k["delivered_value_inr"]), "Delivered value",
         f'{pct(deliv_share)} of booked value'),
        ("amber", inr(k["aov_inr"], 0), "Avg order value",
         f'Booked &divide; orders &middot; {num(k["unique_customers"])} customers'),
        ("rose", pct(k["return_rate_pct"]), "Return rate",
         f'{num(k["returned_orders"])} of delivered + returned orders'),
        ("sky", pct(k["cancellation_rate_pct"]), "Cancellation rate",
         f'{num(k["cancelled_orders"])} of all orders'),
        ("violet", pct(k["effective_discount_pct"]), "Effective discount",
         f'{inr(k["discount_inr"])} off {inr(k["gross_inr"])} gross'),
    ]
    gap = '<td width="10" style="width:10px;font-size:0;">&nbsp;</td>'
    rows = ""
    for i in (0, 3):
        rows += "<tr>" + gap.join(card(*c) for c in cards[i:i + 3]) + "</tr>"
        if i == 0:
            rows += '<tr><td colspan="5" style="height:10px;font-size:0;line-height:0;">&nbsp;</td></tr>'
    return f'<tr><td style="padding:20px 24px 4px;background:#ffffff;">{table(rows)}</td></tr>'


DIMS = [("by_region", "region"), ("by_category", "category"), ("by_channel", "channel"),
        ("by_payment_method", "payment_method"), ("by_month", "month")]


def spread(rows, key):
    vals = [r[key] for r in rows]
    return min(vals), max(vals), max(vals) - min(vals)


def insights(d):
    k, b, ex = d["headline_kpis"], d["breakdowns"], d["exceptions"]
    booked = k["booked_value_inr"]
    st = {r["status"]: r for r in b["by_status"]}
    out = []
    # 1 delivered vs booked
    rest = " &middot; ".join(f'{s.replace("_", " ").lower()} {pct(share(st[s]["booked_inr"], booked))}'
                             for s in ("RETURNED", "CANCELLED", "READY_TO_SHIP") if s in st)
    out.append(f'<b>Delivered value is {pct(share(k["delivered_value_inr"], booked))} of booked</b> '
               f'({inr(k["delivered_value_inr"])} of {inr(booked)}). The rest of booked value is {rest}.')
    # 2 category concentration
    cats = sorted(b["by_category"], key=lambda r: -r["booked_inr"])
    t2 = cats[:2]
    sb = share(sum(r["booked_inr"] for r in t2), booked)
    so = share(sum(r["orders"] for r in t2), k["orders"])
    most = max(cats, key=lambda r: r["orders"])
    low = min(cats, key=lambda r: r["aov_inr"])
    lowtxt = (f'{escape(most["category"])} has the most orders ({num(most["orders"])}) and the lowest AOV '
              f'({inr(low["aov_inr"], 0)})' if most is low else
              f'{escape(most["category"])} has the most orders; {escape(low["category"])} the lowest AOV ({inr(low["aov_inr"], 0)})')
    out.append(f'<b>{t2[0]["category"]} + {t2[1]["category"]} drive {pct(sb)} of booked value from {pct(so)} of orders</b> '
               f'&mdash; an AOV gap ({inr(t2[0]["aov_inr"], 0)} and {inr(t2[1]["aov_inr"], 0)} vs {inr(k["aov_inr"], 0)} overall). {lowtxt}.')
    # 3 MoM swings are day-count effects
    mom = [r for r in d["trends"]["mom_booked_overall"] if r["mom_change_pct"] is not None]
    big = sorted(mom, key=lambda r: -abs(r["mom_change_pct"]))[:2]
    bm = {r["month"]: r for r in b["by_month"]}
    pd = [r["booked_per_day_inr"] for r in d["trends"]["mom_booked_per_day_overall"]]
    pd_sp = (max(pd) - min(pd)) / (sum(pd) / len(pd)) * 100
    sw = ", ".join(f'{mlabel(r["month"])} {pct(r["mom_change_pct"], sign=True)} ({bm[r["month"]]["calendar_days"]} days)'
                   for r in sorted(big, key=lambda r: r["month"]))
    out.append(f'<b>The biggest month-on-month swings are calendar effects</b>: {sw}. Booked value per day stays flat '
               f'at {inr(min(pd))}&ndash;{inr(max(pd))} (range {pct(pd_sp)} of the average).')
    # 4 regions
    reg = b["by_region"]
    lo, hi, _ = spread(reg, "booked_inr")
    e = ex["extremes"]
    out.append(f'<b>Regions are within {pct((hi - lo) / lo * 100)} of each other on booked value</b> '
               f'({inr(lo)}&ndash;{inr(hi)}). Return-rate spread is {e["region_return_rate"]["spread_pp"]:.2f} pp '
               f'and cancellation-rate spread {e["region_cancellation_rate"]["spread_pp"]:.2f} pp.')
    # 5 categories rates clustered
    cr, cc = e["category_return_rate"], e["category_cancellation_rate"]
    out.append(f'<b>Category return and cancellation rates are tightly clustered</b>: returns '
               f'{pct(cr["best_lowest"]["rate_pct"], 2)} ({cr["best_lowest"]["category"]}) to {pct(cr["worst_highest"]["rate_pct"], 2)} '
               f'({cr["worst_highest"]["category"]}); cancellations {pct(cc["best_lowest"]["rate_pct"], 2)} ({cc["best_lowest"]["category"]}) to '
               f'{pct(cc["worst_highest"]["rate_pct"], 2)} ({cc["worst_highest"]["category"]}) &mdash; spreads of {cr["spread_pp"]:.2f} and {cc["spread_pp"]:.2f} pp.')
    # 6 payment cancellation gap, compared with every other dimension
    pay = b["by_payment_method"]
    pmax = max(pay, key=lambda r: r["cancellation_rate_pct"])
    pmin = min(pay, key=lambda r: r["cancellation_rate_pct"])
    gaps = {key: spread(b[src], "cancellation_rate_pct")[2] for src, key in DIMS}
    widest = max(gaps, key=gaps.get) == "payment_method"
    out.append(f'<b>{pmax["payment_method"]} has the highest cancellation rate ({pct(pmax["cancellation_rate_pct"], 2)}) and '
               f'{pmin["payment_method"]} the lowest ({pct(pmin["cancellation_rate_pct"], 2)})</b> &mdash; a '
               f'{gaps["payment_method"]:.2f} pp gap, ' + ("the widest cancellation gap of any dimension"
               if widest else "one of the wider cancellation gaps")
               + f' (next: {max((v, n) for n, v in gaps.items() if n != "payment_method")[0]:.2f} pp). Still small in absolute terms.')
    # 7 discount uniform
    allr = [r["effective_discount_pct"] for src, _ in DIMS for r in b[src]]
    out.append(f'<b>Effective discount is uniform at {pct(min(allr), 2)}&ndash;{pct(max(allr), 2)}</b> across every region, '
               f'category, channel, payment method and month (overall {pct(k["effective_discount_pct"], 2)}).')
    # 8 exceptions
    t, bt = ex["top5_month_region_return_rate"][0], ex["bottom5_month_region_return_rate"][-1]
    n = len(ex["month_region_return_rate_exceptions"])
    lead = (f'<b>No month &times; region cell breaches the {pct(ex["month_region_return_rate_threshold_pct"], 2)} return-rate threshold</b>'
            if n == 0 else f'<b>{n} month &times; region cell(s) breach the {pct(ex["month_region_return_rate_threshold_pct"], 2)} threshold</b>')
    out.append(f'{lead} (overall {pct(ex["overall_return_rate_pct"], 2)} + {margin(d):g} pp). Highest: {mlabel(t["month"])} {t["region"]} '
               f'{pct(t["return_rate_pct"], 2)}; lowest: {mlabel(bt["month"])} {bt["region"]} {pct(bt["return_rate_pct"], 2)}.')
    return out


def sec_insights(d, man):
    rows = ""
    for i, s in enumerate(insights(d), 1):
        tone = list(PAL.values())[(i - 1) % 6]
        num_cell = (f'<div style="font-family:{FONT};width:26px;height:26px;line-height:26px;text-align:center;'
                    f'border-radius:13px;background:{tone[1]};color:#ffffff;font-weight:bold;font-size:13px;">{i}</div>')
        rows += ("<tr>" + td(num_cell, "padding:7px 10px 7px 0;width:30px;vertical-align:top;", width=30, valign="top")
                 + td(s, f"padding:7px 0;line-height:21px;border-bottom:1px solid {BORDER};") + "</tr>")
    return section("Key insights", table(rows), INDIGO)


def th(cells, aligns):
    return "<tr>" + "".join(td(c, f"padding:7px 6px;font-size:12px;font-weight:bold;color:{MUTED};text-transform:uppercase;"
                                  f"border-bottom:2px solid {BORDER};text-align:{a};") for c, a in zip(cells, aligns)) + "</tr>"


def mini_bar(w, color):
    w = max(1, min(100, round(w)))
    return table(f'<tr><td width="{w}%" style="background:{color};height:14px;font-size:0;line-height:0;width:{w}%;">&nbsp;</td>'
                 f'<td style="font-size:0;line-height:0;">&nbsp;</td></tr>', "background:#f3f4f6;")


def sec_monthly(d, man):
    bm = {r["month"]: r for r in d["breakdowns"]["by_month"]}
    pdm = {r["month"]: r for r in d["trends"]["mom_booked_per_day_overall"]}
    trend = d["trends"]["mom_booked_overall"]
    mx = max(r["booked_inr"] for r in trend)
    al = ["left", "left", "right", "center", "right", "center"]
    rows = th(["Month", "Booked value", "", "MoM", "Per day", "Per-day MoM"], al)
    for i, r in enumerate(trend):
        m, p = r["month"], pdm[r["month"]]
        mom = r["mom_change_pct"]
        cells = [f'<b>{MONTHS[int(m[5:]) - 1]}</b> <span style="font-size:12px;color:{MUTED};">{bm[m]["calendar_days"]}d</span>',
                 mini_bar(r["booked_inr"] / mx * 100, INDIGO), inr(r["booked_inr"]),
                 badge(pct(mom, sign=True), mom >= 0) if mom is not None else "&ndash;",
                 inr(p["booked_per_day_inr"]),
                 badge(pct(p["mom_change_pct"], sign=True), p["mom_change_pct"] >= 0) if p["mom_change_pct"] is not None else "&ndash;"]
        bg = "#f9fafb" if i % 2 else "#ffffff"
        styles = ["width:62px;", "", "width:78px;", "width:62px;", "width:70px;", "width:78px;"]
        rows += "<tr>" + "".join(td(c, f"padding:6px;background:{bg};text-align:{a};white-space:nowrap;{s}")
                                 for c, a, s in zip(cells, al, styles)) + "</tr>"
    tot = d["headline_kpis"]["booked_value_inr"]
    intro = (f'Booked value (all statuses), {inr(tot)} in total. Bars are scaled to the peak month. '
             f'Month-on-month swings track the number of calendar days; booked value <b>per day</b> is the like-for-like view.')
    return section("Monthly booked value trend", table(rows), "#0891b2", intro)


def grid(head, aligns, body_rows, styles=None):
    """Zebra table: head labels, alignments, list of cell lists."""
    styles = styles or [""] * len(head)
    out = th(head, aligns)
    for i, cells in enumerate(body_rows):
        bg = "#f9fafb" if i % 2 else "#ffffff"
        out += "<tr>" + "".join(td(c, f"padding:6px;background:{bg};text-align:{a};white-space:nowrap;{s}")
                                for c, a, s in zip(cells, aligns, styles)) + "</tr>"
    return table(out)


def margin(d):
    """Exception margin in pp, derived from the analyst's threshold (no hand-typed rule value)."""
    ex = d["exceptions"]
    return round(ex["month_region_return_rate_threshold_pct"] - ex["overall_return_rate_pct"], 2)


def light(rate, overall, mg):
    """Traffic light vs overall return rate: green <= overall, amber up to +mg pp, red above (exception rule)."""
    if rate <= overall:
        return "#059669", "#ecfdf5"
    return ("#b45309", "#fffbeb") if rate <= overall + mg else ("#be123c", "#fff1f2")


def dot(color):
    return f'<span style="color:{color};font-size:14px;">&#9679;</span>'


def sec_region(d, man):
    reg = sorted(d["breakdowns"]["by_region"], key=lambda r: -r["booked_inr"])
    tot = d["headline_kpis"]["booked_value_inr"]
    body = [[f'{dot(REGION_COL.get(r["region"], INDIGO))} <b>{r["region"]}</b>', num(r["orders"]), inr(r["booked_inr"]),
             pct(share(r["booked_inr"], tot)), inr(r["aov_inr"], 0), pct(r["return_rate_pct"], 2),
             pct(r["cancellation_rate_pct"], 2)] for r in reg]
    t = grid(["Region", "Orders", "Booked", "Share", "AOV", "Return", "Cancel"],
             ["left"] + ["right"] * 6, body)
    items = [(r["region"], r["booked_inr"], f'{inr(r["booked_inr"])} &middot; {pct(share(r["booked_inr"], tot))}') for r in reg]
    ch = bars(items, lambda k, i: REGION_COL.get(i[0], INDIGO), 80, 150)
    intro = "Return rate = returned &divide; (delivered + returned) orders. Cancellation rate = cancelled &divide; all orders."
    return section("Region performance", t + '<div style="height:12px;font-size:0;">&nbsp;</div>' + ch, "#059669", intro)


def sec_category(d, man):
    cats = sorted(d["breakdowns"]["by_category"], key=lambda r: -r["booked_inr"])
    k = d["headline_kpis"]
    ov = k["return_rate_pct"]
    mx = cats[0]["booked_inr"]
    al = ["left", "left", "right", "right", "right", "center"]
    body = []
    for i, r in enumerate(cats):
        fg, bg = light(r["return_rate_pct"], ov, margin(d))
        rr = (f'<span style="background:{bg};color:{fg};font-weight:bold;padding:2px 6px;border-radius:10px;">'
              f'{pct(r["return_rate_pct"], 2)}</span>')
        body.append([f'<b>{r["category"]}</b>', mini_bar(r["booked_inr"] / mx * 100, SERIES[i % 6]), inr(r["booked_inr"]),
                     pct(share(r["orders"], k["orders"])), inr(r["aov_inr"], 0), rr])
    t = grid(["Category", "Booked value", "", "Order share", "AOV", "Return rate"], al, body,
             ["width:82px;", "", "width:74px;", "width:70px;", "width:62px;", "width:84px;"])
    legend = (f'<div style="font-family:{FONT};font-size:12px;color:{MUTED};padding-top:8px;">Return-rate colours: '
              f'{dot("#059669")} at/below overall {pct(ov, 2)} &nbsp; {dot("#b45309")} above overall, within +{margin(d):g} pp '
              f'&nbsp; {dot("#be123c")} more than +{margin(d):g} pp above (exception)</div>')
    return section("Category performance", t + legend, "#d97706",
                   "Booked value bars scaled to the largest category; order share = category orders &divide; all orders.")


def subhead(t):
    return f'<div style="font-family:{FONT};font-size:14px;font-weight:bold;color:{TXT};padding:10px 0 4px;">{t}</div>'


def sec_mix(d, man):
    b, tot = d["breakdowns"], d["headline_kpis"]["booked_value_inr"]
    out = ""
    for src, key, title, col in (("by_channel", "channel", "Booked value share by channel", "#0369a1"),
                                 ("by_payment_method", "payment_method", "Booked value share by payment method", "#6d28d9")):
        rows = sorted(b[src], key=lambda r: -r["booked_inr"])
        cmax = max(r["cancellation_rate_pct"] for r in rows)
        items = [(r[key].replace("_", " "), share(r["booked_inr"], tot), f'{pct(share(r["booked_inr"], tot))} &middot; {inr(r["booked_inr"])}',
                  f'cancel {pct(r["cancellation_rate_pct"], 2)}' + (" (highest)" if r["cancellation_rate_pct"] == cmax else ""))
                 for r in rows]
        # share bars on an absolute 0-100% scale would be unreadably thin; scale to the largest share and say so
        out += subhead(title) + bars(items, lambda k, i, c=col: c, 120, 150)
    return section("Channel &amp; payment mix", out, "#0369a1",
                   "Shares of total booked value; bars scaled to the largest share in each group. "
                   "Cancellation rate = cancelled &divide; all orders in that group.")


def sec_exceptions(d, man):
    ex = d["exceptions"]
    n = len(ex["month_region_return_rate_exceptions"])
    thr = ex["month_region_return_rate_threshold_pct"]
    status = (f'<b>No exceptions:</b> none of the {len(d["breakdowns"]["by_month_region"])} month &times; region cells has a return rate above '
              f'{pct(thr, 2)} (overall {pct(ex["overall_return_rate_pct"], 2)} + {margin(d):g} pp).' if n == 0 else
              f'<b>{n} exception cell(s)</b> exceed {pct(thr, 2)}: ' + ", ".join(
                  f'{mlabel(e["month"])} {e["region"]} {pct(e["return_rate_pct"], 2)}' for e in ex["month_region_return_rate_exceptions"]))
    rows = ""
    for title, lst, col in (("Watch list &mdash; highest cells", ex["top5_month_region_return_rate"], "#be123c"),
                            ("Lowest cells", ex["bottom5_month_region_return_rate"], "#047857")):
        rows += f'<tr><td colspan="3" style="font-family:{FONT};font-size:13px;font-weight:bold;color:{col};padding:10px 0 4px;">{title}</td></tr>'
        for e in lst:
            rows += ("<tr>" + td(f'{mlabel(e["month"])} &middot; {e["region"]}', "padding:3px 0;")
                     + td(pct(e["return_rate_pct"], 2), "padding:3px 8px;text-align:right;width:70px;", width=70)
                     + td(f'{e["pp_vs_overall"]:+.2f} pp vs overall', f"padding:3px 0;text-align:right;color:{MUTED};width:150px;",
                          width=150) + "</tr>")
    e = ex["extremes"]
    ext = " &middot; ".join(f'{lab}: {v["best_lowest"][kk]} {pct(v["best_lowest"]["rate_pct"], 2)} to '
                            f'{v["worst_highest"][kk]} {pct(v["worst_highest"]["rate_pct"], 2)}'
                            for lab, kk, v in (("Region returns", "region", e["region_return_rate"]),
                                               ("Category returns", "category", e["category_return_rate"])))
    box = (f'<div style="font-family:{FONT};font-size:14px;color:{TXT};line-height:21px;">{status}</div>'
           + table(rows)
           + f'<div style="font-family:{FONT};font-size:12px;color:{MUTED};padding-top:10px;line-height:18px;">{ext}</div>')
    inner = table("<tr>" + td(box, "background:#fff1f2;border:1px solid #fecdd3;border-left:5px solid #be123c;padding:14px 16px;") + "</tr>")
    return section("Exceptions &amp; watch list", inner, "#be123c",
                   f"Rule: a month &times; region cell is flagged when its return rate exceeds the overall return rate by more than {margin(d):g} pp.")


def bullets(items):
    return "".join(f'<tr>{td("&bull;", "padding:3px 8px 3px 0;vertical-align:top;width:12px;", width=12, valign="top")}'
                   f'{td(s, "padding:3px 0;line-height:20px;")}</tr>' for s in items)


def sec_quality(d, man):
    rec, p, k, b = d["reconciliation"], d["processing"], d["headline_kpis"], d["breakdowns"]
    checks = rec["checks"]
    npass = sum(1 for c in checks if c["pass"])
    ok = rec["all_passed"] and npass == len(checks)
    rows_ok = p["rows_streamed"] == man["data_rows"]
    mark = lambda good: (f'<span style="color:#047857;font-weight:bold;">&#10004;</span>' if good
                         else f'<span style="color:#be123c;font-weight:bold;">&#10008;</span>')
    failed = [c["check"] for c in checks if not c["pass"]]
    status = bullets([
        f'{mark(ok)} Reconciliation: <b>{npass}/{len(checks)} checks passed</b> against {escape(rec["against"])} '
        f'(row count, units, gross, discount, booked, refunds, shipping, rows and booked by status, rows by month, identities)'
        + (f'. Failed: {escape(", ".join(failed))}' if failed else "") + ".",
        f'{mark(rows_ok)} Rows processed: <b>{num(p["rows_streamed"])}</b> vs manifest <b>{num(man["data_rows"])}</b> '
        f'&mdash; complete={p["complete"]}, sampled={p["sampled"]}, money as {escape(p["money_type"])}.',
    ])
    defs = ["booked_value", "delivered_value", "refunds", "aov", "effective_discount_pct", "return_rate_pct",
            "cancellation_rate_pct", "mom_change_pct", "exception_rule"]
    label = {"aov": "AOV", "mom_change_pct": "MoM change"}
    deftxt = bullets(f'<b>{label.get(x) or escape(x.replace("_pct", "").replace("_", " ").capitalize())}</b>: '
                     f'{escape(d["definitions"][x])}' for x in defs if x in d["definitions"])
    rts = [share(r["ready_to_ship_orders"], r["orders"]) for r in b["by_month"]]
    end = datetime.date.fromisoformat(man["period_end"]).strftime("%d %b %Y")
    caveats = bullets([
        ("Synthetic data" if man.get("synthetic") else "Source data") + f' (seed {man.get("seed", "n/a")}); not real Shopsy trading.',
        f'Booked value is not revenue: it includes returned ({inr(next(r["booked_inr"] for r in b["by_status"] if r["status"] == "RETURNED"))}), '
        f'cancelled and open orders. Refunds ({inr(k["refunds_inr"])}) and shipping fees ({inr(k["shipping_fees_inr"])}) are reported separately.',
        f'{num(k["ready_to_ship_orders"])} orders ({pct(k["ready_to_ship_share_pct"])}) were still READY_TO_SHIP at the {end} cutoff, '
        f'spread evenly across months ({pct(min(rts))}&ndash;{pct(max(rts))} per month), so final delivered and return figures may move.',
        f'Return-rate denominator is DELIVERED + RETURNED orders ({num(k["delivered_orders"] + k["returned_orders"])}); '
        f'as a share of all orders it is {pct(k["return_rate_of_all_orders_pct"])}.',
        f'Only {len(b["by_city_top15_by_booked"])} cities appear in the data, so city-level conclusions are limited.',
    ])
    body = table(status) + subhead("Metric definitions") + table(deftxt) + subhead("Caveats") + table(caveats)
    return section("Data quality &amp; method", body, "#6d28d9")


def sec_footer(d, man):
    return (f'<tr><td style="background:#eef2ff;padding:16px 24px;font-family:{FONT};font-size:12px;color:{MUTED};'
            f'text-align:center;line-height:18px;">Synthetic data &mdash; generated by the 4-agent pipeline<br>'
            f'Source: {escape(d["source_file"])} &middot; built by scripts/03_build_report.py from working/analysis.json</td></tr>')


SECTIONS = [sec_header, sec_kpis, sec_insights, sec_monthly, sec_region, sec_category, sec_mix, sec_exceptions,
            sec_quality, sec_footer]


def main():
    with open(ANALYSIS, encoding="utf-8") as f:
        d = json.load(f)
    with open(MANIFEST, encoding="utf-8") as f:
        man = json.load(f)
    if not d.get("reconciliation", {}).get("all_passed"):
        raise SystemExit("Reconciliation failed in analysis.json - refusing to build report.")
    html = page("".join(fn(d, man) for fn in SECTIONS), "Regional performance, Jan-Sep 2026")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"wrote {OUT} ({os.path.getsize(OUT):,} bytes, {len(SECTIONS)} sections)")


if __name__ == "__main__":
    main()
