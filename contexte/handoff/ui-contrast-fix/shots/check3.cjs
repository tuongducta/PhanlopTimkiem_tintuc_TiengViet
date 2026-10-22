const { chromium } = require('playwright');
const wait = async (p) => { await p.waitForTimeout(800); await p.waitForFunction(() => document.querySelector('.stApp')?.getAttribute('data-test-script-state') === 'notRunning', null, {timeout: 180000}).catch(()=>{}); await p.waitForTimeout(1500); };
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto('http://127.0.0.1:8501/'); await p.waitForSelector('[data-testid="stSidebar"]',{state:'attached',timeout:90000}); await wait(p);
  await p.locator('button',{hasText:'Thể thao'}).click(); await wait(p);
  await p.locator('button',{hasText:'Xóa'}).first().focus(); await p.keyboard.press('Shift+Tab'); await p.waitForTimeout(300);
  console.log('focus', await p.evaluate(()=>{const e=document.activeElement; const s=getComputedStyle(e); return [e.innerText,e.matches(':focus-visible'),s.boxShadow,s.outlineStyle]}));
  await p.screenshot({path:`${process.argv[2]}/classify-btn-focus.png`, clip:{x:380,y:680,width:500,height:80}});
  await b.close();
})();
