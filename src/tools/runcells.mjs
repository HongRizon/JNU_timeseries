// 생성된 HTML의 모든 셀을 webR(Node)에서 화면과 같은 순서·방식으로 실행해 오류를 찾는다.
//
//   node src/tools/runcells.mjs timeseries_webr.html [--only u3_,u4_] [--verbose]
//
// 그림은 저장하지 않는다 (Node에는 캔버스가 없으므로 pdf 장치로 보낸다).
// 내려받지 못한 패키지(tseries·forecast·nlme)를 쓰는 셀은 '패키지 없음'으로 따로 센다.
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';

const require = createRequire(resolve(process.env.WEBR_DIR || '.', 'package.json'));
const { WebR } = require('webr');

const args = process.argv.slice(2);
const file = args.find(a => !a.startsWith('--'));
const only = (args.find(a => a.startsWith('--only=')) || '').slice(7).split(',').filter(Boolean);
const verbose = args.includes('--verbose');
const html = readFileSync(file, 'utf8');

const get = name => {
  const m = html.match(new RegExp('window\\.' + name + ' = ([\\s\\S]*?);\\n(?=window\\.|</script>)'));
  return JSON.parse(m[1]);
};
const CFG = get('DECK_CONFIG');
const CELLS = get('DECK_CELLS');
const RUN_R = get('DECK_RUN_R');
const SETUP_R = get('DECK_SETUP_R');
const dataText = name => {
  const m = html.match(new RegExp('<script type="text/plain" id="data-' + name.replace('.', '\\.') + '">([\\s\\S]*?)</script>'));
  return m[1];
};
const unesc = s => s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#x27;/g, "'").replace(/&#39;/g, "'").replace(/&amp;/g, '&');
const codes = {};
for (const m of html.matchAll(/<div class="cell" id="cell-([^"]+)"[\s\S]*?<textarea class="code"[^>]*>([\s\S]*?)<\/textarea>/g)) {
  codes[m[1]] = unesc(m[2]);
}
const order = Object.keys(CELLS);
const missing = order.filter(id => !(id in codes));
if (missing.length) { console.error('코드를 찾지 못한 셀:', missing); process.exit(2); }

const webR = new WebR();
await webR.init();
const HOME = '/home/web_user';
const enc = new TextEncoder();
for (const name of CFG.dataFiles) await webR.FS.writeFile(HOME + '/' + name, enc.encode(dataText(name)));
await webR.evalRVoid(`setwd("${HOME}")`);
await webR.evalRVoid(RUN_R);
await webR.evalRVoid(SETUP_R);
await webR.evalRVoid('options(width = 80, device = function(...) pdf(tempfile(fileext = ".pdf")))');
const installed = new Set(await (await webR.evalR('rownames(installed.packages())')).toArray());

// --only 로 고른 셀과, 그 셀이 필요로 하는 앞 셀(closure)을 화면 순서대로 돌린다
let toRun = new Set(order);
if (only.length) {
  toRun = new Set();
  for (const id of order) {
    if (!only.some(p => id.startsWith(p))) continue;
    for (const d of CELLS[id].closure) toRun.add(d);
    toRun.add(id);
  }
}
const summary = { ok: [], err: [], nopkg: [] };
for (const id of order) {
  if (!toRun.has(id)) continue;
  const m = CELLS[id];
  const pk = (m.pkgs || []).filter(p => !installed.has(p));
  if (pk.length) { summary.nopkg.push(`${id} (${pk.join(',')})`); continue; }
  const shelter = await new webR.Shelter();
  let ok = false, out = '';
  try {
    const res = await shelter.captureR(`.deck_run(${JSON.stringify(codes[id])})`, {
      captureStreams: true, captureConditions: false, withAutoprint: false, captureGraphics: false,
    });
    const val = await res.result.toJs();
    ok = !!(val && val.values && val.values[0] === true);
    out = res.output.map(o => (o.type === 'stderr' ? '! ' : '') + o.data).join('\n');
  } catch (e) {
    out = 'webR 오류: ' + e.message;
  } finally { await shelter.purge(); }
  for (const v of m.defs) { /* lastWriter 흉내는 생략: 화면 순서대로 돌린다 */ }
  const clean = out.replace(/\u0001|\u0002\n?/g, '');
  if (ok) {
    summary.ok.push(id);
    if (verbose) console.log(`\n===== ${id} OK\n${clean}`);
  } else {
    summary.err.push(id);
    console.log(`\n===== ${id} ERROR\n${clean.split('\n').slice(-25).join('\n')}`);
  }
}
console.log(`\n완료 ${summary.ok.length}, 오류 ${summary.err.length}, 패키지 없음 ${summary.nopkg.length}`);
if (summary.err.length) console.log('오류 셀:', summary.err.join(', '));
if (summary.nopkg.length) console.log('패키지 없음:', summary.nopkg.join(', '));
await webR.close();
process.exit(summary.err.length ? 1 : 0);
