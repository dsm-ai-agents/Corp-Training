import pandas as pd, json, sys, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
s = pd.read_csv(R/'input/03_Daily_Sales.csv', encoding='utf-8-sig')
m = pd.read_csv(R/'input/01_Seller_Master.csv', encoding='utf-8-sig')
raw_rows, raw_gmv = len(s), float(s.gmv_inr.sum())
for d in (s, m):
    for c in d.select_dtypes(include=['object','string']).columns: d[c] = d[c].astype(str).str.strip()
s['status'] = s.status.str.upper()
s['order_date'] = pd.to_datetime(s.order_date, errors='coerce')
for c in ['orders','units','selling_price_inr','gmv_inr']: s[c] = pd.to_numeric(s[c], errors='coerce')
for c in ['seller_zone','seller_city','seller_state']: m[c] = m[c].str.upper()
m['darwin_tier'] = m.darwin_tier.str.lower()
mg = s.merge(m, on='seller_id', how='left', validate='many_to_one')
B = mg.status.isin(['DELIVERED','READY_TO_SHIP','RETURNED'])
g = lambda st: float(mg.loc[mg.status==st,'gmv_inr'].sum())
gross, booked = float(mg.gmv_inr.sum()), float(mg.loc[B,'gmv_inr'].sum())
ok = lambda a,b: abs(a-b) < 0.01
checks = [
 ('no_nulls_sales', int(s.isna().sum().sum())==0),
 ('no_bad_dates', int(s.order_date.isna().sum())==0),
 ('unique_sales_row_id', s.sales_row_id.is_unique),
 ('unique_seller_id_master', m.seller_id.is_unique),
 ('no_orphan_sales_sellers', int(mg.seller_zone.isna().sum())==0),
 ('all_master_sellers_have_sales', set(m.seller_id)<=set(s.seller_id)),
 ('statuses_known', set(s.status)<={'DELIVERED','READY_TO_SHIP','RETURNED','CANCELLED'}),
 ('units_x_price_equals_gmv', int(((s.units*s.selling_price_inr-s.gmv_inr).abs()>0.01).sum())==0),
 ('units_ge_orders', int((s.units<s.orders).sum())==0),
 ('join_row_count_equals_raw', len(mg)==raw_rows),
 ('merged_gmv_equals_raw_gmv', ok(gross, raw_gmv)),
 ('booked_plus_cancelled_equals_gross', ok(booked+g('CANCELLED'), gross)),
 ('delivered_ready_returned_equals_booked', ok(g('DELIVERED')+g('READY_TO_SHIP')+g('RETURNED'), booked)),
]
out = {'raw_rows':raw_rows,'merged_rows':len(mg),'raw_gmv':raw_gmv,'gross_gmv':gross,'booked_gmv':booked,
 'delivered_gmv':g('DELIVERED'),'ready_to_ship_gmv':g('READY_TO_SHIP'),'returned_gmv':g('RETURNED'),'cancelled_gmv':g('CANCELLED'),
 'date_min':str(mg.order_date.min().date()),'date_max':str(mg.order_date.max().date()),
 'checks':[{'check':n,'pass':bool(p)} for n,p in checks],'all_pass':all(p for _,p in checks)}
mg['order_date'] = mg.order_date.dt.strftime('%Y-%m-%d')
mg.to_csv(R/'working/merged_sales.csv', index=False)
json.dump(out, open(R/'working/validation_checks.json','w'), indent=2)
for n,p in checks: print('PASS' if p else 'FAIL', n)
sys.exit(0 if out['all_pass'] else 1)
