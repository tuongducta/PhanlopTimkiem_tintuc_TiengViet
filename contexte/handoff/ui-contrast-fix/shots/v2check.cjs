const { chromium } = require('playwright');
const out = __dirname;
const wait = async (p) => { await p.waitForTimeout(800);
  await p.waitForFunction(() => document.querySelector('.stApp')?.getAttribute('data-test-script-state') === 'notRunning' && !/Running/.test(document.body.innerText), null, {timeout: 180000}).catch(()=>{});
  await p.waitForTimeout(1500); };
const tall = async (p, f) => { const v = p.viewportSize(); await p.setViewportSize({width:v.width,height:3000}); await p.waitForTimeout(1200); await p.screenshot({path:`${out}/${f}.png`}); await p.setViewportSize(v); await p.waitForTimeout(400); };
const nav = async (p,i)=>{ await p.locator('[data-testid="stSidebar"] label[data-testid="stRadioOption"]').nth(i).click(); await wait(p); };
const measure = () => {
  const t=document.querySelector('.t2v-table'); const w=t.closest('div');
  const ths=[...t.querySelectorAll('th')].map(e=>[e.innerText.trim(),Math.round(e.getBoundingClientRect().width*10)/10]);
  const rows=[...t.querySelectorAll('tbody tr')].slice(0,3).map(r=>Math.round(r.getBoundingClientRect().height*10)/10);
  const paths=[...t.querySelectorAll('.fl.path')].map(e=>({t:e.innerText.length,ws:getComputedStyle(e).whiteSpace,to:getComputedStyle(e).textOverflow,h:e.getBoundingClientRect().height,trunc:e.scrollWidth>e.clientWidth,title:e.title===e.innerText,w:Math.round(e.getBoundingClientRect().width)}));
  const sc=[...t.querySelectorAll('td.r .fl')].map(e=>({txt:e.innerText,trunc:e.scrollWidth>e.clientWidth,h:e.getBoundingClientRect().height,col:getComputedStyle(e).color,fs:getComputedStyle(e).fontSize}));
  const tr=t.getBoundingClientRect();
  const par=t.parentElement.getBoundingClientRect();
  return {ths,rows,paths:paths.slice(0,5),npaths:paths.length,anyTrunc:paths.filter(x=>x.trunc).length,allTitle:paths.every(x=>x.title),sc:sc.slice(0,3),scTrunc:sc.filter(x=>x.trunc).length,tableW:tr.width,parentW:par.width,docOverflow:document.documentElement.scrollWidth>document.documentElement.clientWidth, tableScroll:t.parentElement.scrollWidth>t.parentElement.clientWidth};
};
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('http://127.0.0.1:8501/'); await p.waitForSelector('[data-testid="stSidebar"]',{state:'attached',timeout:90000}); await wait(p);
  await nav(p,0);
  console.log('sec', await p.evaluate(()=>{const e=document.querySelector('.t2v-sec'); const s=getComputedStyle(e); return [s.color,s.fontSize,e.getBoundingClientRect().height]}));
  await p.locator('button', {hasText:'Thể thao'}).click(); await wait(p);
  await p.locator('button', {hasText:'Phân loại ngay'}).click(); await wait(p);
  console.log('cfoot', await p.evaluate(()=>[...document.querySelectorAll('.t2v-cfoot')].map(e=>{const s=getComputedStyle(e);return [s.color,s.fontSize,e.getBoundingClientRect().height,s.whiteSpace]})));
  await tall(p,'v2-classify-result');
  await nav(p,1);
  await p.locator('button',{hasText:'giá vàng tăng mạnh'}).click(); await wait(p);
  console.log('V2', JSON.stringify(await p.evaluate(measure)));
  console.log('sc3', await p.evaluate(()=>[...document.querySelectorAll('.t2v-sc3 small')].map(e=>{const s=getComputedStyle(e);return [s.color,s.fontSize,e.getBoundingClientRect().height]})));
  console.log('fl all', await p.evaluate(()=>[...document.querySelectorAll('.t2v-table .fl')].slice(0,1).map(e=>[getComputedStyle(e).color,getComputedStyle(e).fontSize])));
  await tall(p,'v2-search-result');
  // mô phỏng vòng 1: bỏ nowrap/ellipsis/max-width
  await p.addStyleTag({content:'.t2v-table .fl.path{white-space:normal!important;overflow:visible!important;text-overflow:clip!important;max-width:none!important}'});
  await p.waitForTimeout(500);
  console.log('R1sim', JSON.stringify(await p.evaluate(measure)));
  await tall(p,'v2-search-result-r1sim');
  await b.close();
  const b2 = await chromium.launch(); const q = await b2.newPage({ viewport: { width: 1440, height: 900 } });
  q.on('pageerror',e=>errs.push(String(e)));
  await q.goto('http://127.0.0.1:8501/'); await q.waitForSelector('[data-testid="stSidebar"]',{state:'attached',timeout:90000}); await wait(q);
  for (const i of [0,1,2,3]) { await nav(q,i); console.log('page',i,'traceback',await q.evaluate(()=>/Traceback|Exception/.test(document.body.innerText))); }
  console.log('errs',errs);
  await b2.close();
})().catch(e=>{console.error(e);process.exit(1)});
