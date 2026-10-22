const { chromium } = require('playwright');
const wait = async (p) => { await p.waitForTimeout(800); await p.waitForFunction(() => document.querySelector('.stApp')?.getAttribute('data-test-script-state') === 'notRunning', null, {timeout: 180000}).catch(()=>{}); await p.waitForTimeout(1500); };
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto('http://127.0.0.1:8501/'); await p.waitForSelector('[data-testid="stSidebar"]',{state:'attached',timeout:90000}); await wait(p);
  const go = p.locator('button',{hasText:'Phân loại ngay'});
  await p.locator('button',{hasText:'Xóa'}).first().focus();
  await p.keyboard.press('Shift+Tab'); await p.waitForTimeout(300);
  console.log('focus', await p.evaluate(()=>{const e=document.activeElement; const s=getComputedStyle(e); return [e.innerText,e.matches(':focus-visible'),s.outlineStyle,s.outlineColor,s.outlineWidth,s.boxShadow]}));
  await p.screenshot({path:`${process.argv[2]}/classify-btn-focus.png`, clip:{x:380,y:680,width:500,height:80}});
  await p.locator('[data-testid="stSidebar"] label[data-testid="stRadioOption"]').nth(1).click(); await wait(p);
  await p.locator('button',{hasText:'giá vàng tăng mạnh'}).click(); await wait(p);
  const h = () => p.evaluate(()=>({rows:[...document.querySelectorAll('.t2v-table tr')].slice(0,6).map(r=>Math.round(r.getBoundingClientRect().height)), fl:[...document.querySelectorAll('.t2v-table .fl')].slice(0,3).map(e=>Math.round(e.getBoundingClientRect().height)), sc3:Math.round(document.querySelector('.t2v-sc3').getBoundingClientRect().height), sc3w:[...document.querySelectorAll('.t2v-sc3 small')].map(e=>Math.round(e.getBoundingClientRect().height))}));
  console.log('after11', JSON.stringify(await h()));
  await p.addStyleTag({content:'.t2v-table .fl,.t2v-sc3 small{font-size:10px !important}'}); await p.waitForTimeout(500);
  console.log('as10px', JSON.stringify(await h()));
  await b.close();
})();
