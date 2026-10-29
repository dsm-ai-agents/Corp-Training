import csv, json, random, pathlib, collections, copy
import openpyxl

ROOT=pathlib.Path(__file__).resolve().parents[1]
SRC=ROOT.parents[1]/'Data1_provided'/'sample'
R=random.Random(29102026)
tables={}
def save(name, rows):
    tables[name]=rows
    d=ROOT/'csv'; d.mkdir(exist_ok=True)
    with (d/(name+'.csv')).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def money(x): return round(x,2)
audit=[]; sets={}
for f in sorted(SRC.glob('*.xlsx')):
    s=openpyxl.load_workbook(f,read_only=True,data_only=True).active
    vals=list(s.values); heads=vals[0]; rows=[dict(zip(heads,r)) for r in vals[1:6]]
    audit.append({'file':f.name,'columns':len(heads),'data_rows':s.max_row-1,'headers':heads,'first_five_rows':rows})
    sets[f.name]={k:{str(r[k]) for r in rows if r.get(k) is not None} for k in ('seller_id','listing_id','product_id','campaign_id') if k in heads}
(ROOT/'Source_Columns_and_First_Five_Rows.json').write_text(json.dumps(audit,indent=2,default=str),encoding='utf-8')
overlaps=[]
for a in sets:
    for b in sets:
        if a>=b: continue
        for k in sets[a].keys() & sets[b].keys(): overlaps.append(f'{a} <> {b}: {k}: {len(sets[a][k]&sets[b][k])} shared values')
(ROOT/'Source_Relationship_Review.txt').write_text('SOURCE SAMPLE REVIEW\nAll seven files contain five data rows.\n\n'+'\n'.join(overlaps)+'\n\nCandidate joins are not proof of actual matches. No cross-file ID match is invented in the original samples.\nBM_RAW campaign IDs repeat across brands; daily ads also repeat campaign/date across brands.\nSales repeats listing across status/date. Listing health has no listing_id and is a creation cohort aggregate.\nFunnel counts rise across hours: likely cumulative snapshots, but this needs owner confirmation. Do not sum these snapshots.\nSource dates differ: listing cohorts 2023, binder April 2026, sales/ads October 2026.\nThe normalized training pack below intentionally creates a common October population and explicit grains.\n',encoding='utf-8')
cats=[('Footwear','WomenFootwear','WomenWedges',285),('Home','CookingAndCookware','PanAndTawa',549),('Electronics','MobileProtection','ScreenGuard',149),('Lifestyle','KidClothing','KidSock',199),('BGM','FoodAndNutrition','SpicesMasala',179),('Furniture','LivingRoomSF','AquariumTank',799)]
cities=[('NEW DELHI','DELHI','NORTH'),('JAIPUR','RAJASTHAN','NORTH'),('CHENNAI','TAMIL NADU','SOUTH'),('MUMBAI','MAHARASHTRA','WEST'),('KOLKATA','WEST BENGAL','EAST')]
sellers=[]; listings=[]
for i in range(30):
    city,state,zone=cities[i%5]
    sellers.append(dict(seller_id=f'SYN-S{i+1:03}',display_name=f'Training Store {i+1:02}',seller_city=city,seller_state=state,seller_zone=zone,darwin_tier=['t1','t2','t3'][i%3],owner=f'Manager {i%5+1}'))
    bu,cat,vert,price=cats[i%6]
    for j in range(4):
        n=i*4+j+1
        listings.append(dict(listing_id=f'SYN-L{n:04}',product_id=f'SYN-P{n:04}',seller_id=sellers[-1]['seller_id'],product_title=f'{vert} Variant {j+1}',brand=f'Training Brand {i%10+1:02}',business_unit=bu,category=cat,vertical=vert,current_listing_status='INACTIVE' if n%17==0 else 'ACTIVE',current_fsp_inr=price+j*20,current_atp=0 if n%11==0 else R.randint(20,300),snapshot_date='2026-10-28'))
save('01_Seller_Master',sellers); save('02_Listing_Master',listings)
sales=[]; optins=[]; ads=[]; funnel=[]
for l in listings:
    num=int(l['listing_id'][-4:]); eligible=num%5!=0; opted=eligible and num%3!=0
    optins.append(dict(listing_id=l['listing_id'],promotion_id='SYN-OCT-FPO',eligible=eligible,opted_in=opted,start_date='2026-10-15',end_date='2026-10-28',discount_rate=0.10 if opted else 0.0))
    for day in range(1,29):
        date=f'2026-10-{day:02}'
        qty=R.randint(1,8)
        if opted and day>=15: qty+=3
        if l['category']=='WomenFootwear' and 20<=day<=23: qty=max(1,qty//3)
        if l['current_listing_status']=='INACTIVE' or (l['current_atp']==0 and day>=22): continue
        status=R.choices(['DELIVERED','RETURNED','CANCELLED','READY_TO_SHIP'],[72,15 if l['category']=='WomenFootwear' else 7,6,7])[0]
        if day>25 and status=='DELIVERED': status='READY_TO_SHIP'
        orders=max(1,qty-R.randint(0,1)); price=money(l['current_fsp_inr']*(.9 if opted and day>=15 else 1))
        sales.append(dict(sales_row_id=f'SYN-T{len(sales)+1:05}',order_date=date,listing_id=l['listing_id'],seller_id=l['seller_id'],status=status,orders=orders,units=qty,selling_price_inr=price,gmv_inr=money(qty*price)))
save('03_Daily_Sales',sales); save('04_Promotion_Optins',optins)
for si,s in enumerate(sellers):
    for day in range(1,29):
        date=f'2026-10-{day:02}'
        ss=[x for x in sales if x['seller_id']==s['seller_id'] and x['order_date']==date and x['status']=='DELIVERED']
        for b in range(2):
            impressions=R.randint(1800,7000); clicks=round(impressions*R.uniform(.015,.04)); spend=money(clicks*R.uniform(1.5,4))
            # Two brand rows share a campaign. Each gets a disjoint attribution allocation.
            units=int(sum(x['units'] for x in ss)*(.18 if b==0 else .12))
            rev=money(sum(x['gmv_inr'] for x in ss)*(.18 if b==0 else .12)) if units else 0
            if si%6==2 and day>=18: spend=money(spend*1.8); impressions=int(impressions*1.3)
            ads.append(dict(date=date,campaign_id=f'SYN-C{si+1:03}',seller_id=s['seller_id'],brand_segment=f'Segment {b+1}',channel=['accenture','dst','Unmanaged'][si%3],budget_type='DAILY_BUDGET',daily_budget_inr=800,impressions=impressions,clicks=clicks,actual_spend_inr=spend,attributed_units=units,attributed_revenue_inr=rev))
save('05_Daily_Advertising',ads)
summary=[]
for s in sellers:
    for b in range(2):
        a=[x for x in ads if x['seller_id']==s['seller_id'] and x['brand_segment']==f'Segment {b+1}']
        summary.append(dict(campaign_id=a[0]['campaign_id'],seller_id=s['seller_id'],brand_segment=a[0]['brand_segment'],period_start='2026-10-01',period_end='2026-10-28',**{k:money(sum(x[k] for x in a)) for k in ['impressions','clicks','actual_spend_inr','attributed_units','attributed_revenue_inr']}))
save('06_Campaign_Performance',summary)
health=[]
for s in sellers:
    ls=[l for l in listings if l['seller_id']==s['seller_id']]
    health.append(dict(snapshot_date='2026-10-28',seller_id=s['seller_id'],category=ls[0]['category'],total_listings=len(ls),active_listings=sum(l['current_listing_status']=='ACTIVE' for l in ls),active_instock_listings=sum(l['current_listing_status']=='ACTIVE' and l['current_atp']>0 for l in ls),total_products=len({l['product_id'] for l in ls})))
save('07_Listing_Health',health)
for day in range(1,29):
    for channel,base in [('Direct',18000),('PN',9000),('RT',13000)]:
        visits=int(base*R.uniform(.8,1.25)*(1.25 if day>=15 else 1)); ppv=int(visits*.55); cart=int(ppv*(.13 if channel=='PN' else .22)); checkout=int(cart*.86); pay=int(checkout*.81)
        orders=int(pay*(.27 if channel=='PN' and 20<=day<=23 else .48))
        funnel.append(dict(date=f'2026-10-{day:02}',traffic_channel=channel,visits=visits,product_page_views=ppv,add_to_cart=cart,checkout=checkout,payment=pay,orders=orders,units=round(orders*1.12)))
save('08_Channel_Funnel',funnel)
binder=[]; grouped=collections.defaultdict(list); lm={x['listing_id']:x for x in listings}
for x in sales: grouped[(x['seller_id'],lm[x['listing_id']]['category'],x['status'])].append(x)
for (seller,cat,status),xs in grouped.items(): binder.append(dict(month='2026-10',seller_id=seller,category=cat,status=status,orders=sum(x['orders'] for x in xs),units=sum(x['units'] for x in xs),gmv_inr=money(sum(x['gmv_inr'] for x in xs))))
save('09_Monthly_Seller_Sales',binder)
dirty=copy.deepcopy(sales[:200]); issues=[]
def change(i,k,v,reason):
    old=dirty[i][k]; dirty[i][k]=v; issues.append(dict(sales_row_id=dirty[i]['sales_row_id'],field=k,corrupt_value=v,expected_value=old,issue=reason))
change(3,'listing_id','SYN-L9999','Orphan listing ID'); change(12,'seller_id',' SYN-S001 ','Whitespace in key'); change(20,'order_date','2026-13-40','Invalid date'); change(37,'gmv_inr',-500,'Negative GMV'); change(56,'orders',None,'Missing order count'); change(75,'units',0,'Zero units with positive GMV'); change(92,'status','delivered','Status case mismatch'); change(111,'seller_id','SYN-S030','Seller conflicts with listing master'); change(130,'gmv_inr',99999,'GMV does not equal units times price'); change(155,'selling_price_inr','INR 285','Numeric field stored as text')
dirty.append(copy.deepcopy(dirty[1])); issues.append(dict(sales_row_id=dirty[1]['sales_row_id'],field='whole_row',corrupt_value='duplicate',expected_value='one row',issue='Exact duplicate row'))
save('10_Challenge_Dirty_Sales',dirty)
(ROOT/'trainer_only').mkdir(exist_ok=True)
with (ROOT/'trainer_only'/'Data_Quality_Answer_Key.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(issues[0])); w.writeheader(); w.writerows(issues)
checks=[]
assert len(lm)==len(listings)
assert all(x['seller_id']==lm[x['listing_id']]['seller_id'] for x in sales)
assert all(x['units']>=x['orders']>0 and abs(x['gmv_inr']-x['units']*x['selling_price_inr'])<.011 for x in sales)
assert abs(sum(x['gmv_inr'] for x in sales)-sum(x['gmv_inr'] for x in binder))<.01
assert abs(sum(x['actual_spend_inr'] for x in ads)-sum(x['actual_spend_inr'] for x in summary))<.01
assert len({(x['date'],x['campaign_id'],x['brand_segment']) for x in ads})==len(ads)
assert all(x['visits']>=x['product_page_views']>=x['add_to_cart']>=x['checkout']>=x['payment']>=x['orders'] for x in funnel)
metrics={'sales_rows':len(sales),'gross_gmv_inr_all_statuses':money(sum(x['gmv_inr'] for x in sales)),'delivered_gmv_inr':money(sum(x['gmv_inr'] for x in sales if x['status']=='DELIVERED')),'ad_spend_inr':money(sum(x['actual_spend_inr'] for x in ads)),'attributed_revenue_inr':money(sum(x['attributed_revenue_inr'] for x in ads)),'intentional_quality_issues':len(issues)}
metrics['roas']=metrics['attributed_revenue_inr']/metrics['ad_spend_inr']
(ROOT/'trainer_only'/'Validation_and_Control_Totals.json').write_text(json.dumps({'checks':'Passed: keys, foreign keys, row arithmetic, sales/monthly reconciliation, ad reconciliation, funnel nesting','row_counts':{k:len(v) for k,v in tables.items()},'controls':metrics},indent=2),encoding='utf-8')
(ROOT/'support'/'tables.json').write_text(json.dumps(tables),encoding='utf-8')
print(json.dumps(metrics)); print('Shared IDs in original samples:',[x for x in overlaps if not x.endswith('0 shared values')])
