// ===== 시계열 webR 실습: runtime =====
const CFG = window.DECK_CONFIG;
const CELLS = window.DECK_CELLS;
const UNITS = window.DECK_UNITS;
const DECK_RUN_R = window.DECK_RUN_R;
const DECK_SETUP_R = window.DECK_SETUP_R;
const LS = 'tsdeck:' + CFG.version + ':';
const HOME = '/home/web_user';

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
function lsGet(k) { try { return localStorage.getItem(LS + k); } catch (e) { return null; } }
function lsSet(k, v) { try { localStorage.setItem(LS + k, v); } catch (e) { /* storage off */ } }
function escH(s) { return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
function cellEl(id) { return document.getElementById('cell-' + id); }
function cellTitle(id) {
  const m = CELLS[id];
  const el = cellEl(id);
  const t = el ? $('.ctitle', el).innerHTML : escH(m.title);
  return `<span class="nu">[${m.unit}]</span> ` + t;
}

// ---------------------------------------------------------------- slides
const deckEl = $('#deck');
const slides = $$('.slide');
let cur = -1;

function unitFirst(u) { return slides.findIndex(s => s.dataset.unit === u); }
function keyIndex(key) { return slides.findIndex(s => s.dataset.key === key); }

function show(i, opts = {}) {
  i = Math.max(0, Math.min(slides.length - 1, i));
  if (cur >= 0 && slides[cur]) slides[cur].hidden = true;
  cur = i;
  const s = slides[cur];
  s.hidden = false;
  const u = s.dataset.unit;
  $$('[data-unit-tab]').forEach(b => b.setAttribute('aria-current', b.dataset.unitTab === u ? 'true' : 'false'));
  const tab = $(`[data-unit-tab="${u}"]`);
  if (tab && tab.scrollIntoView) tab.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  const inUnit = slides.filter(x => x.dataset.unit === u);
  $('#pos').textContent = `${u === 'U0' ? '시작' : u} · ${inUnit.indexOf(s) + 1} / ${inUnit.length}`;
  $('#bar').style.width = ((cur + 1) / slides.length * 100).toFixed(2) + '%';
  $('#btn-prev').disabled = cur === 0;
  $('#btn-next').disabled = cur === slides.length - 1;
  if (!opts.keepScroll) deckEl.scrollTop = 0;
  const hash = '#' + s.dataset.key;
  if (location.hash !== hash) { try { history.replaceState(null, '', hash); } catch (e) { /* ignore */ } }
  lsSet('slide', s.dataset.key);
  $$('.cell', s).forEach(initEditor);
}

function startIndex() {
  const h = decodeURIComponent(location.hash.replace(/^#/, ''));
  let i = h ? keyIndex(h) : -1;
  if (i < 0 && /^U\d$/.test(h)) i = unitFirst(h);
  if (i < 0) { const k = lsGet('slide'); if (k) i = keyIndex(k); }
  return i < 0 ? 0 : i;
}

function goToCell(id) {
  const el = cellEl(id);
  if (!el) return;
  const s = el.closest('.slide');
  const i = slides.indexOf(s);
  if (i !== cur) show(i);
  const det = el.closest('details');
  if (det && !det.open) det.open = true;
  initEditor(el);
  el.scrollIntoView({ block: 'center' });
  el.classList.add('flash');
  setTimeout(() => el.classList.remove('flash'), 1600);
}

window.addEventListener('hashchange', () => {
  const i = keyIndex(decodeURIComponent(location.hash.replace(/^#/, '')));
  if (i >= 0 && i !== cur) show(i);
});

function anyDialogOpen() { return !$('#toc').hidden || !$('#help').hidden; }
function closeDialogs() { $('#toc').hidden = true; $('#help').hidden = true; }

document.addEventListener('keydown', e => {
  if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
  if (anyDialogOpen()) { if (e.key === 'Escape') closeDialogs(); return; }
  const t = e.target;
  if (t && t.closest && t.closest('input, textarea, select, [contenteditable="true"]')) return;
  if (e.key === 'ArrowRight') { show(cur + 1); e.preventDefault(); }
  else if (e.key === 'ArrowLeft') { show(cur - 1); e.preventDefault(); }
});

function openToc() {
  const body = $('#toc-body');
  const parts = [];
  for (const u of UNITS) {
    const items = slides.map((s, i) => ({ s, i })).filter(x => x.s.dataset.unit === u.id);
    parts.push(`<h3>${escH(u.id === 'U0' ? '시작' : u.id + ' ' + u.title)}</h3><ol>` +
      items.map(x => `<li data-toc="${x.i}"${x.i === cur ? ' class="cur"' : ''}>${escH(x.s.dataset.title)}</li>`).join('') + '</ol>');
  }
  body.innerHTML = parts.join('');
  $('#help').hidden = true;
  $('#toc').hidden = false;
  const c = $('li.cur', body);
  if (c) c.scrollIntoView({ block: 'center' });
}

// ---------------------------------------------------------------- editors
const R_KW = new Set(['function', 'for', 'in', 'if', 'else', 'while', 'repeat', 'break', 'next', 'return',
  'TRUE', 'FALSE', 'NULL', 'NA', 'Inf', 'NaN', 'T', 'F']);

function highlightR(code) {
  let out = '';
  let i = 0;
  const n = code.length;
  while (i < n) {
    const ch = code[i];
    if (ch === '#') {
      let j = code.indexOf('\n', i);
      if (j < 0) j = n;
      const c = code.slice(i, j);
      const cls = c.includes('바꿔 보기') ? 'tk-knob' : 'tk-com';
      out += `<span class="${cls}">${escH(c)}</span>`;
      i = j;
      continue;
    }
    if (ch === '"' || ch === "'") {
      let j = i + 1;
      while (j < n && code[j] !== ch && code[j] !== '\n') j += code[j] === '\\' ? 2 : 1;
      j = Math.min(n, j + 1);
      out += `<span class="tk-str">${escH(code.slice(i, j))}</span>`;
      i = j;
      continue;
    }
    const prev = i > 0 ? code[i - 1] : '';
    if (/[0-9.]/.test(ch) && !/[A-Za-z0-9._]/.test(prev)) {
      const m = /^(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?L?/.exec(code.slice(i, i + 32));
      if (m) { out += `<span class="tk-num">${m[0]}</span>`; i += m[0].length; continue; }
    }
    if (/[A-Za-z.]/.test(ch)) {
      const m = /^[A-Za-z.][A-Za-z0-9._]*/.exec(code.slice(i, i + 64));
      const w = m[0];
      const rest = code.slice(i + w.length, i + w.length + 8);
      if (R_KW.has(w)) out += `<span class="tk-kw">${w}</span>`;
      else if (/^\s*\(/.test(rest)) out += `<span class="tk-fn">${escH(w)}</span>`;
      else out += escH(w);
      i += w.length;
      continue;
    }
    out += escH(ch);
    i += 1;
  }
  return out + '\n';
}

const editorDone = new WeakSet();
function initEditor(el) {
  const ta = $('textarea.code', el);
  const pre = $('pre.hl', el);
  if (!ta || !pre) return;
  if (!editorDone.has(el)) {
    editorDone.add(el);
    ta.addEventListener('input', () => { pre.innerHTML = highlightR(ta.value); sizeEditor(el); });
    ta.addEventListener('scroll', () => { pre.scrollLeft = ta.scrollLeft; pre.scrollTop = ta.scrollTop; });
    ta.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); requestRun(el.dataset.cell); }
    });
    pre.innerHTML = highlightR(ta.value);
  }
  sizeEditor(el);
}
function sizeEditor(el) {
  const ta = $('textarea.code', el);
  if (!ta || !ta.offsetParent) return;
  ta.style.height = 'auto';
  const extra = ta.offsetHeight - ta.clientHeight;
  ta.style.height = (ta.scrollHeight + extra) + 'px';
}
document.addEventListener('toggle', e => {
  if (e.target.tagName === 'DETAILS' && e.target.open) $$('.cell', e.target).forEach(initEditor);
}, true);
window.addEventListener('resize', () => { if (slides[cur]) $$('.cell', slides[cur]).forEach(sizeEditor); });

// ---------------------------------------------------------------- notes (빈칸 표·기록)
for (const el of $$('.note-input')) {
  const v = lsGet('note:' + el.dataset.key);
  if (v !== null) el.value = v;
  el.addEventListener('input', () => lsSet('note:' + el.dataset.key, el.value));
}
function exportNotes() {
  const lines = ['시계열분석 webR 실습 기록', '저장한 때: ' + new Date().toLocaleString('ko-KR'), ''];
  for (const s of slides) {
    const inputs = $$('.note-input', s).filter(x => x.value.trim());
    if (!inputs.length) continue;
    lines.push(`■ ${s.dataset.unit === 'U0' ? '시작' : s.dataset.unit} · ${s.dataset.title}`);
    for (const x of inputs) lines.push(`- ${x.dataset.label}: ${x.value.trim().replace(/\n/g, '\n  ')}`);
    lines.push('');
  }
  if (lines.length <= 3) lines.push('(아직 쓴 내용이 없습니다)');
  saveText('시계열_실습_기록.txt', '﻿' + lines.join('\n'));
}

// ---------------------------------------------------------------- downloads
function dataText(name) { const el = document.getElementById('data-' + name); return el ? el.textContent : ''; }
function saveText(name, text) {
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
}
function downloadData(name) {
  if (name === 'trd_dates.csv' || name === 'qqq_dates.csv') {
    const [dates, vals, head] = name === 'trd_dates.csv'
      ? [dataText('trd_dates.txt'), dataText('trd.txt'), 'date,trades']
      : [dataText('qqq_months.txt'), dataText('qqq.txt'), 'month,qqq'];
    const d = dates.trim().split('\n');
    const v = vals.trim().split('\n').slice(1);
    saveText(name, head + '\n' + d.map((x, i) => x + ',' + v[i]).join('\n') + '\n');
  } else {
    saveText(name, dataText(name));
  }
}

// ---------------------------------------------------------------- R status
const statusEl = $('#rstatus');
function setStatus(st, text, retry = false) {
  statusEl.dataset.state = st;
  $('.txt', statusEl).textContent = text;
  const old = $('button', statusEl);
  if (old) old.remove();
  if (retry) {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = '다시 시도';
    b.addEventListener('click', () => { rReadyPromise = startR(); rReadyPromise.catch(() => {}); });
    statusEl.appendChild(b);
  }
}

// ---------------------------------------------------------------- webR
let webR = null;
let rReady = false;
let rReadyPromise = null;

function withTimeout(p, ms, what) {
  return Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error(what + ' 시간 초과')), ms))]);
}

async function startR() {
  rReady = false;
  setStatus('loading', 'R 준비 중…');
  let lastErr = null;
  for (const src of CFG.webr) {
    const t0 = performance.now();
    const tick = setInterval(() => setStatus('loading', `R 준비 중… ${Math.round((performance.now() - t0) / 1000)}초`), 1000);
    try {
      const mod = await withTimeout(import(src.mod), 30000, 'webR 불러오기');
      const { WebR, ChannelType } = mod;
      webR = new WebR({ baseUrl: src.base, channelType: ChannelType.PostMessage });
      await webR.init();
      await setupSession();
      clearInterval(tick);
      rReady = true;
      setStatus('ready', 'R 준비됨');
      return;
    } catch (e) {
      clearInterval(tick);
      lastErr = e;
      console.error('webR start failed from', src.mod, e);
      try { if (webR) webR.close(); } catch (_) { /* ignore */ }
      webR = null;
    }
  }
  setStatus('error', 'R을 불러오지 못함 · 인터넷 연결 확인', true);
  throw lastErr || new Error('webR');
}

async function setupSession() {
  const enc = new TextEncoder();
  for (const name of CFG.dataFiles) {
    await webR.FS.writeFile(HOME + '/' + name, enc.encode(dataText(name)));
  }
  await webR.evalRVoid(`setwd("${HOME}")`);
  await webR.evalRVoid(DECK_RUN_R);
  await webR.evalRVoid(DECK_SETUP_R);
  await webR.evalRVoid('options(width = 80)');
}

// ---------------------------------------------------------------- packages
const pkgOK = new Set();
async function hasPkg(p) {
  return await webR.evalRBoolean(`nzchar(system.file(package = ${JSON.stringify(p)}))`);
}
async function ensurePackages(pkgs, onStatus) {
  for (const p of pkgs) {
    if (CFG.basePkgs.includes(p) || pkgOK.has(p)) continue;
    if (await hasPkg(p)) { pkgOK.add(p); continue; }
    const t0 = performance.now();
    const say = () => onStatus(`패키지 ${p} 내려받는 중… ${Math.round((performance.now() - t0) / 1000)}초 (처음 한 번만, 수십 초 걸릴 수 있음)`);
    say();
    const tick = setInterval(say, 1000);
    try {
      for (const repos of CFG.repoAttempts) {
        try { await webR.installPackages([p], { repos, quiet: true }); } catch (e) { console.warn('install', p, repos, e); }
        if (await hasPkg(p)) break;
      }
    } finally { clearInterval(tick); }
    if (await hasPkg(p)) pkgOK.add(p);
    else { const err = new Error('package ' + p); err.pkg = p; throw err; }
  }
}
function pkgsIn(code) {
  const out = [];
  const re = /\b(?:library|require)\(\s*["']?([A-Za-z][\w.]*)["']?\s*\)/g;
  let m;
  while ((m = re.exec(code))) if (!out.includes(m[1])) out.push(m[1]);
  return out;
}

// ---------------------------------------------------------------- run state
const state = { ok: {}, ranAt: {}, lastWriter: {}, writeAt: {}, seq: 0 };

function planFor(C) {
  const planned = new Set();
  const outdated = P => CELLS[P].imports.some(v => {
    const Q = CELLS[P].prov[v];
    return Q && state.lastWriter[v] === Q && (state.writeAt[v] || 0) > (state.ranAt[P] || 0);
  });
  const want = X => {
    const m = CELLS[X];
    for (const v of m.imports) {
      const P = m.prov[v];
      if (!P || planned.has(P)) continue;
      if (!state.ok[P] || state.lastWriter[v] !== P || outdated(P)) { planned.add(P); want(P); }
    }
    for (const D of m.needs) if (!state.ok[D] && !planned.has(D)) { planned.add(D); want(D); }
  };
  want(C);
  const order = CELLS[C].closure;
  let changed = true;
  while (changed) {
    changed = false;
    for (const X of order) {
      if (planned.has(X)) continue;
      const consumers = [C, ...planned];
      const provides = consumers.some(Y => Object.entries(CELLS[Y].prov).some(([, P]) => P === X));
      if (!provides) continue;
      if (CELLS[X].imports.some(v => planned.has(CELLS[X].prov[v]))) { planned.add(X); want(X); changed = true; }
    }
  }
  return order.filter(x => planned.has(x));
}

// ---------------------------------------------------------------- running cells
let queue = Promise.resolve();
function enqueue(fn) {
  const p = queue.then(fn);
  queue = p.catch(e => console.error(e));
  return p;
}
function setCellStatus(id, html) { const el = cellEl(id); if (el) $('.cstatus', el).innerHTML = html; }

function requestRun(id) {
  const el = cellEl(id);
  if (!el) return;
  const btn = $('.run', el);
  if (btn.disabled) return;
  btn.disabled = true;
  setCellStatus(id, '대기 중…');
  enqueue(() => runWithDeps(id)).finally(() => { btn.disabled = false; });
}

async function runWithDeps(id) {
  if (!rReady) {
    setCellStatus(id, 'R 준비를 기다리는 중… (오른쪽 위 표시)');
    try { await rReadyPromise; } catch (e) {
      setCellStatus(id, '<span class="err">R을 불러오지 못했습니다.</span> 인터넷 연결을 확인하고 오른쪽 위의 ‘다시 시도’를 누르세요.');
      return false;
    }
  }
  const plan = planFor(id);
  const done = [];
  for (const d of plan) {
    setCellStatus(id, `앞 셀 실행 중: ${cellTitle(d)}`);
    const ok = await runOne(d, { autoFor: id });
    if (!ok) {
      const out = $('.out', cellEl(id));
      out.innerHTML = `<div class="pre-note">앞 셀 <a data-goto-cell="${d}">${cellTitle(d)}</a>에서 오류가 나서 멈췄습니다. 그 셀의 출력을 확인하세요.</div>`;
      setCellStatus(id, '<span class="err">앞 셀 오류</span>');
      return false;
    }
    done.push(d);
  }
  return await runOne(id, { before: done });
}

async function runOne(id, opts = {}) {
  const m = CELLS[id];
  const el = cellEl(id);
  const code = $('textarea.code', el).value;
  const out = $('.out', el);
  out.innerHTML = '';
  if (opts.before && opts.before.length) {
    out.insertAdjacentHTML('beforeend', '<div class="pre-note">먼저 실행한 앞 셀: ' +
      opts.before.map(d => `<a data-goto-cell="${d}">${cellTitle(d)}</a>`).join(' → ') + '</div>');
  }
  if (opts.autoFor) {
    out.insertAdjacentHTML('beforeend', `<div class="pre-note">자동 실행: <a data-goto-cell="${opts.autoFor}">${cellTitle(opts.autoFor)}</a>에 필요해서 실행함</div>`);
  }
  let pkgFail = null;
  try { await ensurePackages(pkgsIn(code), t => setCellStatus(id, escH(t))); }
  catch (e) { pkgFail = e.pkg || 'package'; }

  const t0 = performance.now();
  const timer = setInterval(() => setCellStatus(id, `실행 중… ${((performance.now() - t0) / 1000).toFixed(1)}초`), 200);
  setCellStatus(id, '실행 중…');
  setStatus('busy', 'R 실행 중…');
  let ok = false;
  let items = [];
  let images = [];
  let shelter = null;
  try {
    shelter = await new webR.Shelter();
    const res = await shelter.captureR(`.deck_run(${JSON.stringify(code)})`, {
      captureStreams: true,
      captureConditions: false,
      withAutoprint: false,
      captureGraphics: { width: m.gw, height: m.gh, bg: 'white', capture: true },
    });
    const val = await res.result.toJs();
    ok = !!(val && val.values && val.values[0] === true);
    items = res.output || [];
    images = res.images || [];
  } catch (e) {
    items = [{ type: 'stderr', data: 'webR 오류: ' + ((e && e.message) || String(e)) }];
  } finally {
    clearInterval(timer);
    if (shelter) { try { await shelter.purge(); } catch (_) { /* ignore */ } }
    setStatus('ready', 'R 준비됨');
  }
  const text = renderOutput(out, items, images, m);
  const secs = ((performance.now() - t0) / 1000).toFixed(1);
  setCellStatus(id, ok ? `<span class="okmark">✓</span> 완료 · ${secs}초` : `<span class="err">오류</span> · ${secs}초`);
  if (!ok) addHints(id, out, text, pkgFail);

  state.seq += 1;
  for (const v of m.defs) { state.lastWriter[v] = id; state.writeAt[v] = state.seq; }
  state.ok[id] = ok;
  state.ranAt[id] = state.seq;
  return ok;
}

function bitmapImg(bmp, m) {
  const c = document.createElement('canvas');
  c.width = bmp.width;
  c.height = bmp.height;
  c.getContext('2d').drawImage(bmp, 0, 0);
  const img = document.createElement('img');
  img.className = 'plot';
  img.alt = 'R 그림';
  img.src = c.toDataURL('image/png');
  img.width = Math.min(m.gw, bmp.width);
  try { bmp.close(); } catch (_) { /* ignore */ }
  return img;
}

function renderOutput(out, items, images, m) {
  // 그림은 그 페이지가 끝나는 자리에 놓는다: 다음 페이지가 시작될 때(앞 식에서 시작된 페이지면
  // 새 식의 echo 앞) 또는 출력 끝.
  let pre = null;
  let mode = null;
  let k = 0;
  let anchor = null;          // 현재 식의 첫 echo 줄
  let inEcho = false;
  let expr = 0;
  let pageOpen = false;
  let pageExpr = 0;
  const all = [];
  const add = (text, cls) => {
    if (!pre) { pre = document.createElement('pre'); pre.className = 'console'; out.appendChild(pre); }
    const span = document.createElement('span');
    if (cls) span.className = cls;
    span.textContent = text + '\n';
    pre.appendChild(span);
    all.push(text);
    return span;
  };
  const placeImage = beforeAnchor => {
    if (k >= images.length) return;
    const img = bitmapImg(images[k++], m);
    if (beforeAnchor && anchor && anchor.isConnected) {
      const host = anchor.parentNode;
      if (host.firstChild === anchor) {
        out.insertBefore(img, host);
      } else {
        const tail = document.createElement('pre');
        tail.className = 'console';
        while (anchor.nextSibling) tail.appendChild(anchor.nextSibling);
        tail.insertBefore(anchor, tail.firstChild);
        host.after(img);
        img.after(tail);
        if (pre === host) pre = tail;
      }
    } else {
      out.appendChild(img);
      pre = null;
    }
  };
  for (const it of items) {
    if (it.type !== 'stdout' && it.type !== 'stderr') continue;
    let data = String(it.data);
    if (data.endsWith('\n')) data = data.slice(0, -1);
    for (const line of data.split('\n')) {
      if (it.type === 'stdout' && line === '\u0002') {
        if (pageOpen) placeImage(pageExpr < expr);
        pageOpen = true;
        pageExpr = expr;
        inEcho = false;
        continue;
      }
      if (it.type === 'stdout' && line.startsWith('\u0001')) {
        const span = add(line.slice(1), 'echo');
        if (!inEcho) { anchor = span; expr += 1; inEcho = true; }
        mode = null;
        continue;
      }
      inEcho = false;
      if (it.type === 'stdout') { mode = null; add(line, null); continue; }
      if (/^Error/.test(line)) mode = 'err';
      else if (/^(Warning message|In addition)/.test(line)) mode = 'warn';
      else if (!mode) mode = 'msg';
      add(line, mode);
    }
  }
  if (pageOpen) placeImage(false);
  while (k < images.length) placeImage(false);
  return all.join('\n');
}

function addHints(id, out, text, pkgFail) {
  const hint = html => out.insertAdjacentHTML('beforeend', `<div class="hint">${html}</div>`);
  const noPkg = /there is no package called ‘?'?([A-Za-z][\w.]*)/.exec(text);
  if (pkgFail || noPkg) {
    const p = pkgFail || (noPkg && noPkg[1]);
    let extra = '';
    if (p === 'forecast') extra = ' 계속 안 되면 <code>tsdisplay(r)</code> 대신 <code>layout(1:3); plot(r, type="l"); acf(r); pacf(r)</code>로 같은 그림을 그릴 수 있다.';
    hint(`패키지 <code>${escH(p)}</code>를 내려받지 못했습니다. 인터넷 연결을 확인하고 다시 실행하세요.${extra}`);
  }
  if (/variable lengths differ/.test(text) && CFG.seasonCell) {
    hint('<code>time_st</code>, <code>SIN</code>, <code>COS</code>의 길이가 자료와 다릅니다 (예측 셀이 새 시점의 값으로 덮어씀). ' +
      `<button type="button" class="btn small" data-run-chain="${CFG.seasonCell},${id}">계절 항을 다시 만든 뒤 다시 실행</button>`);
  }
  const nf = /object '([^']+)' not found/.exec(text);
  if (nf) hint(`<code>${escH(nf[1])}</code>이(가) 없습니다. 이 셀이 쓰는 앞 셀을 먼저 실행하세요. 결과가 이상하면 위쪽의 ‘R 초기화’ 뒤 다시 실행하세요.`);
}

async function resetSession() {
  if (!rReady) return;
  if (!window.confirm('R 세션의 변수를 모두 지우고 (TRD·QQQ는 다시 읽음) 셀 출력을 비웁니다. 계속할까요?')) return;
  await enqueue(async () => {
    try {
      await webR.evalRVoid('rm(list = ls(envir = globalenv(), all.names = FALSE), envir = globalenv()); graphics.off()');
      await webR.evalRVoid(DECK_SETUP_R);
    } catch (e) { console.error(e); }
    state.ok = {}; state.ranAt = {}; state.lastWriter = {}; state.writeAt = {};
    for (const el of $$('.cell')) { $('.out', el).innerHTML = ''; $('.cstatus', el).innerHTML = ''; }
  });
}

async function preloadPackages(btn) {
  const note = $('[data-preload-status]');
  btn.disabled = true;
  const say = t => { if (note) note.textContent = t; };
  try {
    if (!rReady) { say('R 준비를 기다리는 중…'); await rReadyPromise; }
    await enqueue(async () => {
      for (const p of ['tseries', 'forecast', 'nlme']) {
        await ensurePackages([p], t => say(t));
      }
    });
    say('완료: tseries · forecast · nlme');
  } catch (e) {
    say(`내려받지 못함${e && e.pkg ? ': ' + e.pkg : ''} · 인터넷 연결을 확인하세요`);
  } finally { btn.disabled = false; }
}

// ---------------------------------------------------------------- clicks
document.addEventListener('click', e => {
  const t = e.target.closest('button, a, li[data-toc]');
  if (!t) return;
  if (t.id === 'btn-prev') return show(cur - 1);
  if (t.id === 'btn-next') return show(cur + 1);
  if (t.id === 'btn-toc') return openToc();
  if (t.id === 'btn-toc-close') { $('#toc').hidden = true; return; }
  if (t.id === 'btn-help') { $('#toc').hidden = true; $('#help').hidden = false; return; }
  if (t.id === 'btn-help-close') { $('#help').hidden = true; return; }
  if (t.id === 'btn-reset') return resetSession();
  if (t.dataset.toc !== undefined) { $('#toc').hidden = true; return show(+t.dataset.toc); }
  if (t.dataset.unitTab) return show(unitFirst(t.dataset.unitTab));
  if (t.dataset.goto) return show(unitFirst(t.dataset.goto));
  if (t.dataset.gotoCell) { e.preventDefault(); return goToCell(t.dataset.gotoCell); }
  if (t.dataset.download) return downloadData(t.dataset.download);
  if (t.dataset.action === 'export-notes') return exportNotes();
  if (t.dataset.action === 'preload') return preloadPackages(t);
  if (t.dataset.runChain) {
    const [first, then] = t.dataset.runChain.split(',');
    t.disabled = true;
    enqueue(async () => { if (await runWithDeps(first)) await runWithDeps(then); });
    return;
  }
  const cell = t.closest('.cell');
  if (cell && t.classList.contains('run')) return requestRun(cell.dataset.cell);
  if (cell && t.classList.contains('reset')) {
    const ta = $('textarea.code', cell);
    ta.value = ta.defaultValue;
    ta.dispatchEvent(new Event('input'));
  }
});
$('#toc').addEventListener('click', e => { if (e.target.id === 'toc') e.target.hidden = true; });
$('#help').addEventListener('click', e => { if (e.target.id === 'help') e.target.hidden = true; });

// ---------------------------------------------------------------- start
show(startIndex());
rReadyPromise = startR();
rReadyPromise.catch(() => {});
window.__deck = { show, state, planFor, runWithDeps, ensurePackages, get webR() { return webR; }, get ready() { return rReady; } };
