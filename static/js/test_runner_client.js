// Minimal client runner
const cardsEl = document.getElementById('cards');
const pill = document.getElementById('pillState');
const meta = document.getElementById('summaryMeta');
const report = document.getElementById('report');
const timesEl = document.getElementById('times');

const CATS = ['health','security','chat','webrtc','db','admin','upload'];

function createCard(cat) {
  const card = document.createElement('div');
  card.className = 'card';
  card.id = `card-${cat}`;
  
  const h3 = document.createElement('h3');
  h3.textContent = cat.toUpperCase();
  card.appendChild(h3);
  
  const meta = document.createElement('div');
  meta.className = 'meta';
  const span = document.createElement('span');
  span.id = `m-${cat}`;
  span.textContent = '0 passed / 0 total';
  meta.appendChild(span);
  card.appendChild(meta);
  
  const bar = document.createElement('div');
  bar.className = 'bar';
  const fill = document.createElement('i');
  fill.id = `p-${cat}`;
  bar.appendChild(fill);
  card.appendChild(bar);
  
  const details = document.createElement('details');
  const summary = document.createElement('summary');
  summary.textContent = 'Details';
  details.appendChild(summary);
  const pre = document.createElement('pre');
  pre.id = `log-${cat}`;
  pre.textContent = 'waiting…';
  details.appendChild(pre);
  card.appendChild(details);
  
  return card;
}

function paintSkeleton() {
  cardsEl.innerHTML = '';
  CATS.forEach(cat => cardsEl.appendChild(createCard(cat)));
}
paintSkeleton();

function setHeaderState(okCount, totalCount) {
  if (totalCount === 0) return;
  const ratio = okCount / totalCount;
  pill.classList.remove('ok','bad','warn');
  if (ratio === 1) { pill.classList.add('ok'); pill.textContent = 'All Green'; }
  else if (ratio >= .7) { pill.classList.add('warn'); pill.textContent = 'Partial'; }
  else { pill.classList.add('bad'); pill.textContent = 'Failing'; }
  meta.textContent = `${okCount}/${totalCount} passed`;
}

async function runAll(retryFailed=false) {
  report.textContent = 'Running…';
  const body = retryFailed ? { retryFailed:true } : {};
  const res = await fetch('/api/test/run', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body) });
  const out = await res.json();

  let grandTotal = 0, grandPass = 0;

  for (const cat of Object.keys(out)) {
    const { total, passed, items } = out[cat];
    grandTotal += total; grandPass += passed;

    const m = document.getElementById(`m-${cat}`);
    const p = document.getElementById(`p-${cat}`);
    const lg = document.getElementById(`log-${cat}`);

    m.textContent = `${passed} passed / ${total} total`;
    p.style.width = total ? `${Math.round((passed/total)*100)}%` : '0%';
    lg.textContent = items.map(it => `${it.ok ? 'OK' : 'FAIL'} ${it.name} — ${it.msg || ''}`).join('\n') || 'no items';
  }
  setHeaderState(grandPass, grandTotal);
  report.innerHTML = '';
  const pre = document.createElement('pre');
  pre.textContent = JSON.stringify(out, null, 2);
  report.appendChild(pre);
}

async function repairSafe() {
  report.textContent = 'Repair (dry-run)…';
  let res = await fetch('/api/repair/run', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ mode:'safe', dryRun:true }) });
  let plan = await res.json();
  
  report.innerHTML = '';
  const metaDiv1 = document.createElement('div');
  metaDiv1.className = 'meta';
  metaDiv1.textContent = 'Plan (dry):';
  report.appendChild(metaDiv1);
  
  const pre1 = document.createElement('pre');
  pre1.textContent = JSON.stringify(plan, null, 2);
  report.appendChild(pre1);

  res = await fetch('/api/repair/run', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ mode:'safe', dryRun:false }) });
  const applied = await res.json();
  
  const metaDiv2 = document.createElement('div');
  metaDiv2.className = 'meta';
  metaDiv2.style.marginTop = '8px';
  metaDiv2.textContent = 'Applied:';
  report.appendChild(metaDiv2);
  
  const pre2 = document.createElement('pre');
  pre2.textContent = JSON.stringify(applied, null, 2);
  report.appendChild(pre2);

  await runAll();
}

async function loadSchedule() {
  const r = await fetch('/api/test/schedule');
  const out = await r.json();
  timesEl.innerHTML = '';
  (out.times || []).forEach(t => {
    const chip = document.createElement('span');
    chip.className = 'chip';
    
    const timeText = document.createTextNode(t + ' ');
    chip.appendChild(timeText);
    
    const btn = document.createElement('button');
    btn.textContent = 'x';
    btn.dataset.t = t;
    btn.onclick = async () => {
      await fetch('/api/test/schedule/' + encodeURIComponent(t), { method: 'DELETE' });
      loadSchedule();
    };
    chip.appendChild(btn);
    
    timesEl.appendChild(chip);
  });
}

document.getElementById('btnRun').onclick = ()=> runAll(false);
document.getElementById('btnFailed').onclick = ()=> runAll(true);
document.getElementById('btnRepair').onclick = repairSafe;
document.getElementById('btnAdd').onclick = async ()=>{
  const v = document.getElementById('timeInput').value;
  if(!v) return;
  await fetch('/api/test/schedule', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ time:v }) });
  loadSchedule();
};

loadSchedule();
