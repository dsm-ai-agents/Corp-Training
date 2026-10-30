import json, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
S = json.load(open(R/'working/kpi_summary.json'))
html = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Regional Dashboard</title>
<style>
:root{--bg:#f6f8fa;--card:#fff;--ink:#14213d;--mut:#555f6d;--line:#dde3ea;--navy:#14213d;--teal:#0f766e;--warn:#c2410c}
@media(prefers-color-scheme:dark){:root{--bg:#0e1420;--card:#18212f;--ink:#eef2f6;--mut:#a3adbb;--line:#2a3547;--navy:#8fb0ff;--teal:#2dd4bf;--warn:#fb923c}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 Calibri,Segoe UI,Arial,sans-serif}
main{max-width:1100px;margin:0 auto;padding:16px}h1{font-size:24px;margin:8px 0 2px}h2{font-size:17px;margin:0 0 10px}
.sub{color:var(--mut);margin:0 0 14px}.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin-bottom:14px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}.tile{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px}
.tile b{display:block;font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.03em}.tile span{font-size:22px;font-weight:700}.tile small{display:block;color:var(--mut)}
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}button{border:1px solid var(--line);background:var(--card);color:var(--ink);padding:8px 14px;border-radius:999px;font:inherit;cursor:pointer}
button.on{background:var(--navy);color:var(--bg);border-color:var(--navy)}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:560px}th,td{padding:7px 8px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
th:first-child,td:first-child{text-align:left}th{color:var(--mut);font-size:12px;text-transform:uppercase}
.flag{color:var(--warn);font-size:12px;white-space:normal;text-align:left}.rec{font-size:12px;color:var(--mut)}
.bar{display:flex;align-items:flex-end;gap:14px;height:170px;padding-top:8px}.grp{flex:1;display:flex;flex-direction:column;align-items:center;height:100%;justify-content:flex-end}
.pair{display:flex;align-items:flex-end;gap:4px;height:130px}.pair i{display:block;width:26px;border-radius:4px 4px 0 0}.lab{font-size:12px;color:var(--mut);text-align:center;margin-top:4px}
.lg{font-size:12px;color:var(--mut);margin-bottom:4px}.lg i{display:inline-block;width:10px;height:10px;border-radius:2px;margin:0 4px 0 10px}
</style></head><body><main>
<h1>Regional sales dashboard</h1><p class="sub" id="sub"></p>
<div class="tabs" id="tabs"></div><div class="tiles" id="tiles"></div>
<div class="card" style="margin-top:14px"><h2>Weekly trend: booked vs delivered GMV (Rs lakh)</h2><div class="lg"><i style="background:var(--navy)"></i>Booked<i style="background:var(--teal)"></i>Delivered</div><div class="bar" id="trend"></div></div>
<div class="card"><h2>Regions</h2><div class="scroll"><table id="zt"></table></div></div>
<div class="card"><h2>Managers</h2><div class="scroll"><table id="mt"></table></div></div>
<div class="card"><h2>Sellers (flagged first)</h2><div class="scroll"><table id="st"></table></div></div>
<div class="card rec" id="rec"></div>
<p class="rec">Booked = Delivered + Ready to ship + Returned. Delivered rate = delivered / booked. Return rate = returned / booked. Cancel rate = cancelled / gross. Flags: return or cancel rate above 1.5x overall, or delivered rate 10+ pts below zone.</p>
</main>
<script>
const D=__DATA__;let Z='ALL';
const L=v=>'Rs '+(v/1e5).toFixed(2)+' lakh',P=v=>(v*100).toFixed(1)+'%';
const sum=(a,k)=>a.reduce((t,x)=>t+x[k],0);
function agg(a){const g=sum(a,'gross_gmv'),b=sum(a,'booked_gmv'),d=sum(a,'delivered_gmv'),r=sum(a,'returned_gmv'),c=sum(a,'cancelled_gmv'),q=sum(a,'ready_to_ship_gmv');return{g,b,d,r,c,q,dr:b?d/b:0,rr:b?r/b:0,cr:g?c/g:0,n:a.length}}
function tile(l,v,s){return `<div class="tile"><b>${l}</b><span>${v}</span><small>${s}</small></div>`}
function render(){
 const S=D.sellers.filter(s=>Z=='ALL'||s.zone==Z),A=agg(S);
 document.getElementById('sub').textContent=`Period ${D.meta.period}. Region = seller zone. View: ${Z=='ALL'?'All regions':Z}, ${A.n} sellers.`;
 document.getElementById('tabs').innerHTML=['ALL',...D.zones.map(z=>z.name)].map(z=>`<button class="${z==Z?'on':''}" onclick="Z='${z}';render()">${z=='ALL'?'All regions':z}</button>`).join('');
 document.getElementById('tiles').innerHTML=tile('Booked GMV',L(A.b),'excl. cancelled')+tile('Delivered GMV',L(A.d),P(A.dr)+' of booked')+tile('Ready to ship',L(A.q),'booked, not yet delivered')+tile('Returned GMV',L(A.r),P(A.rr)+' of booked')+tile('Cancelled GMV',L(A.c),P(A.cr)+' of gross');
 const W=Z=='ALL'?D.weekly:D.zone_weekly[Z],mx=Math.max(...W.map(w=>w.booked_gmv));
 document.getElementById('trend').innerHTML=W.map(w=>`<div class="grp"><div class="pair"><i style="height:${w.booked_gmv/mx*120}px;background:var(--navy)" title="Booked ${L(w.booked_gmv)}"></i><i style="height:${w.delivered_gmv/mx*120}px;background:var(--teal)" title="Delivered ${L(w.delivered_gmv)}"></i></div><div class="lab">${w.label}<br>${(w.booked_gmv/1e5).toFixed(1)} / ${(w.delivered_gmv/1e5).toFixed(1)}</div></div>`).join('');
 const H='<tr><th>Name</th><th>Booked</th><th>Delivered</th><th>Returned</th><th>Cancelled</th><th>Deliv. rate</th></tr>';
 const row=(n,x)=>`<tr><td>${n}</td><td>${L(x.b)}</td><td>${L(x.d)}</td><td>${L(x.r)}</td><td>${L(x.c)}</td><td>${P(x.dr)}</td></tr>`;
 document.getElementById('zt').innerHTML=H+D.zones.filter(z=>Z=='ALL'||z.name==Z).map(z=>row(z.name+' ('+z.sellers+')',agg(D.sellers.filter(s=>s.zone==z.name)))).join('');
 const ms=[...new Set(S.map(s=>s.manager))].sort();
 document.getElementById('mt').innerHTML=H+ms.map(m=>row(m,agg(S.filter(s=>s.manager==m)))).join('');
 const SS=[...S].sort((a,b)=>b.flags.length-a.flags.length||b.delivered_gmv-a.delivered_gmv);
 document.getElementById('st').innerHTML='<tr><th>Seller</th><th>Zone</th><th>Booked</th><th>Delivered</th><th>Return rate</th><th>Cancel rate</th><th>Flags</th></tr>'+SS.map(s=>`<tr><td>${s.name}</td><td>${s.zone}</td><td>${L(s.booked_gmv)}</td><td>${L(s.delivered_gmv)}</td><td>${P(s.return_rate)}</td><td>${P(s.cancel_rate)}</td><td class="flag">${s.flags.join(', ')}</td></tr>`).join('');
 const T=D.totals;document.getElementById('rec').innerHTML=`<b>Reconciliation (all regions):</b> Booked ${L(T.booked_gmv)} + Cancelled ${L(T.cancelled_gmv)} = Gross ${L(T.gross_gmv)}. Delivered ${L(T.delivered_gmv)} + Ready to ship ${L(T.ready_to_ship_gmv)} + Returned ${L(T.returned_gmv)} = Booked. ${D.reconciliation.checks_passed} of ${D.reconciliation.checks_total} data checks passed.`}
render();
</script></body></html>'''
slim = {k:S[k] for k in ['meta','totals','reconciliation','weekly','zone_weekly']}
slim['zones']=[{k:z[k] for k in ['name','sellers']} for z in S['zones']]
slim['sellers']=S['sellers']
open(R/'outputs/regional_dashboard.html','w').write(html.replace('__DATA__', json.dumps(slim)))
print('saved html')
