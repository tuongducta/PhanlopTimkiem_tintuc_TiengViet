const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
await p.goto('http://127.0.0.1:8501/');await p.waitForSelector('[data-testid="stSidebar"]',{state:'attached',timeout:90000});await p.waitForTimeout(2500);
await p.locator('[data-testid="stSidebar"] label[data-testid="stRadioOption"]').nth(1).click();await p.waitForTimeout(2500);
await p.locator('button',{hasText:'giá vàng tăng mạnh'}).click();await p.waitForTimeout(6000);
console.log(await p.evaluate(()=>{const t=document.querySelector('.t2v-table');const w=t.parentElement;const s=getComputedStyle(w);const r=w.getBoundingClientRect();const th=[...t.querySelectorAll('th')].pop().getBoundingClientRect();return {cls:w.className,ox:s.overflowX,wRight:r.right,lastThRight:th.right,sw:w.scrollWidth,cw:w.clientWidth}}));
await b.close();})();
