import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from 'file:///C:/Users/kunaa/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const data=JSON.parse(await fs.readFile(path.join(root,'support/tables.json'),'utf8'));
const wb=Workbook.create();
for(const [name,rows] of Object.entries(data)){
 const sh=wb.worksheets.add(name.slice(3)); const keys=Object.keys(rows[0]);
 const mat=[keys,...rows.map(r=>keys.map(k=>r[k]))];
 sh.getRangeByIndexes(0,0,mat.length,keys.length).values=mat;
 const used=sh.getRangeByIndexes(0,0,mat.length,keys.length);
 used.format.font={name:'Arial',size:10}; used.format.rowHeight=20; used.format.columnWidth=19;
 const header=sh.getRangeByIndexes(0,0,1,keys.length);
 header.format.fill='#203864'; header.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'}; header.format.wrapText=true; header.format.rowHeight=38;
 sh.showGridLines=false; sh.freezePanes.freezeRows(1);
 for(let c=0;c<keys.length;c++){
  const k=keys[c],col=sh.getRangeByIndexes(1,c,rows.length,1);
  if(k.endsWith('_inr')){col.setNumberFormat('#,##0.00');}
  else if(k.endsWith('_rate'))col.setNumberFormat('0.0%');
  else if(typeof rows[0][k]==='number')col.setNumberFormat('#,##0');
  if(k.includes('date')||['period_start','period_end'].includes(k)){
   if(!name.startsWith('10')){col.values=rows.map(r=>[new Date(r[k]+'T00:00:00Z')]); col.setNumberFormat('yyyy-mm-dd');}
  }
  if(['product_title','category','brand_segment','current_listing_status'].includes(k))sh.getRangeByIndexes(0,c,mat.length,1).format.columnWidth=27;
 }
 sh.tables.add(sh.getRangeByIndexes(0,0,mat.length,keys.length),true,'T'+name.replaceAll('_',''));
}
wb.recalculate();
console.log((await wb.inspect({kind:'sheet',include:'id,name',maxChars:2000})).ndjson);
const out=await SpreadsheetFile.exportXlsx(wb); await out.save(path.join(root,'Shopsy_AI_Analytics_Training.xlsx'));
for(const name of Object.keys(data)){
 const sheet=name.slice(3);
 try {const p=await wb.render({sheetName:sheet,range:'A1:F6',scale:1.4,format:'png'}); await fs.writeFile(path.join(root,'support',sheet+'.png'),new Uint8Array(await p.arrayBuffer()));}
 catch(e){console.log('Render issue '+sheet+': '+e.message);}
}
console.log('Workbook exported');
