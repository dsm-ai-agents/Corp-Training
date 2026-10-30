import pandas as pd, json, sys, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
chk = json.load(open(R/'working/validation_checks.json'))
if not chk['all_pass']: sys.exit('Validation failed; stop.')
d = pd.read_csv(R/'working/merged_sales.csv', parse_dates=['order_date'])
d['week'] = ((d.order_date.dt.day-1)//7+1).astype(int)
WL = {1:'Oct 1-7',2:'Oct 8-14',3:'Oct 15-21',4:'Oct 22-28'}
BK = ['DELIVERED','READY_TO_SHIP','RETURNED']
def kp(x):
    f = lambda st: float(x.loc[x.status==st,'gmv_inr'].sum())
    b = x[x.status.isin(BK)]
    gross, canc = float(x.gmv_inr.sum()), f('CANCELLED')
    booked, dl, rt, rs = float(b.gmv_inr.sum()), f('DELIVERED'), f('RETURNED'), f('READY_TO_SHIP')
    bo = int(b.orders.sum())
    return {'gross_gmv':gross,'booked_gmv':booked,'delivered_gmv':dl,'ready_to_ship_gmv':rs,'returned_gmv':rt,'cancelled_gmv':canc,
      'booked_orders':bo,'delivered_orders':int(x.loc[x.status=='DELIVERED','orders'].sum()),'booked_units':int(b.units.sum()),
      'aov_booked':booked/bo if bo else 0,
      'delivered_rate':dl/booked if booked else 0,'return_rate':rt/booked if booked else 0,'cancel_rate':canc/gross if gross else 0}
def cut(col, extra=None):
    out=[]
    for k,x in d.groupby(col):
        r = {'name':k,'sellers':int(x.seller_id.nunique()),**kp(x)}
        out.append(r)
    return sorted(out, key=lambda r:-r['delivered_gmv'])
tot = kp(d); tot['sellers']=int(d.seller_id.nunique()); tot['sales_rows']=len(d)
zones = cut('seller_zone')
for z in zones:
    zx = d[d.seller_zone==z['name']]
    z['share_of_delivered'] = z['delivered_gmv']/tot['delivered_gmv']
    z['cities'] = sorted(zx.seller_city.unique().tolist())
def trend(x, by, labels=None):
    out=[]
    for k,y in x.groupby(by):
        r = kp(y); out.append({'label': labels[k] if labels else str(k.date()), 'booked_gmv':r['booked_gmv'],'delivered_gmv':r['delivered_gmv'],'returned_gmv':r['returned_gmv'],'cancelled_gmv':r['cancelled_gmv']})
    return out
weekly = trend(d,'week',WL); daily = trend(d,'order_date')
zone_weekly = {z['name']: trend(d[d.seller_zone==z['name']],'week',WL) for z in zones}
# sellers and exceptions
sellers=[]
for sid,x in d.groupby('seller_id'):
    r = {'seller_id':sid,'name':x.display_name.iloc[0],'city':x.seller_city.iloc[0],'zone':x.seller_zone.iloc[0],'tier':x.darwin_tier.iloc[0],'manager':x.owner.iloc[0],**kp(x)}
    sellers.append(r)
zrate = {z['name']:z['delivered_rate'] for z in zones}
for r in sellers:
    fl=[]
    if r['return_rate']>1.5*tot['return_rate']: fl.append('High return rate')
    if r['cancel_rate']>1.5*tot['cancel_rate']: fl.append('High cancel rate')
    if r['delivered_rate']<zrate[r['zone']]-0.10: fl.append('Delivered rate 10+ pts below zone')
    r['flags']=fl
exc = sorted([r for r in sellers if r['flags']], key=lambda r:-(r['returned_gmv']+r['cancelled_gmv']))
ranked = sorted(sellers, key=lambda r:-r['delivered_gmv'])
L = lambda v: f"Rs {v/1e5:,.2f} lakh"
best, worst = zones[0], zones[-1]
heads = [
 f"Booked GMV {L(tot['booked_gmv'])}; delivered GMV {L(tot['delivered_gmv'])} ({tot['delivered_rate']*100:.1f}% of booked).",
 f"{best['name'].title()} leads on delivered GMV at {L(best['delivered_gmv'])} ({best['share_of_delivered']*100:.1f}% share); {worst['name'].title()} is lowest at {L(worst['delivered_gmv'])}.",
 f"Leakage: returned {L(tot['returned_gmv'])} ({tot['return_rate']*100:.1f}% of booked) and cancelled {L(tot['cancelled_gmv'])} ({tot['cancel_rate']*100:.1f}% of gross).",
 f"{len(exc)} of {len(sellers)} sellers flagged for exceptions.",
]
S = {'meta':{'period':f"{chk['date_min']} to {chk['date_max']}",'currency':'INR','region_field':'seller_zone',
  'definitions':{'booked':'DELIVERED + READY_TO_SHIP + RETURNED','delivered':'DELIVERED only','gross':'all rows','delivered_rate':'delivered / booked','return_rate':'returned / booked','cancel_rate':'cancelled / gross'}},
 'totals':tot,'reconciliation':{'gross_check':tot['booked_gmv']+tot['cancelled_gmv']-tot['gross_gmv'],'booked_check':tot['delivered_gmv']+tot['ready_to_ship_gmv']+tot['returned_gmv']-tot['booked_gmv'],'checks_passed':sum(c['pass'] for c in chk['checks']),'checks_total':len(chk['checks'])},
 'zones':zones,'cities':cut('seller_city'),'managers':cut('owner'),'tiers':cut('darwin_tier'),
 'weekly':weekly,'daily':daily,'zone_weekly':zone_weekly,'sellers':ranked,'exceptions':exc,
 'top5':ranked[:5],'bottom5':ranked[-5:][::-1],'headlines':heads}
json.dump(S, open(R/'working/kpi_summary.json','w'), indent=2)
md = ['# KPI summary ('+S['meta']['period']+')','']+['- '+h for h in heads]+['','## Zones','| Zone | Booked | Delivered | Returned | Cancelled | Delivered rate |','|---|---|---|---|---|---|']
md += [f"| {z['name']} | {L(z['booked_gmv'])} | {L(z['delivered_gmv'])} | {L(z['returned_gmv'])} | {L(z['cancelled_gmv'])} | {z['delivered_rate']*100:.1f}% |" for z in zones]
md += ['','## Exceptions']+[f"- {r['name']} ({r['zone']}, {r['manager']}): {', '.join(r['flags'])}" for r in exc]
open(R/'working/summary.md','w').write('\n'.join(md))
print('\n'.join(md))
