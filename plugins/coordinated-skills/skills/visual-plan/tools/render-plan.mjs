#!/usr/bin/env node
/**
 * render-plan.mjs — Conductor Visual Plans v2.
 *
 * Renders a repo's EXISTING ground truth into a single static plan.html:
 *   FEATURES.json             -> feature board (pass/fail + evidence + linked blocks)
 *   .harness/plan/blocks.json -> authored plan blocks, grouped by section
 *   .harness/plan/comments.jsonl -> the REVIEW CHANNEL: pinned comments, tracked in
 *                                git; unresolved comments block the features they cite
 *   .harness/telemetry.jsonl  -> verdict timeline (the recap, evidence-backed)
 *   git log                   -> what actually happened
 *
 * v2 adds the back-and-forth: stable block ids, sections + sticky nav, a status
 * header (blockers first), feature<->block cross-links, and inline comment
 * threads with resolution state. Comments are appended via plan-comment.mjs or
 * the sfdt ui Plan page (v2 roadmap); the builder reads unresolved ones at
 * get-bearings and may not flip a feature they cite.
 *
 * Output is DERIVED — editing plan.html by hand is the same sin as editing
 * generated/*. Zero deps; mermaid via CDN with <pre> fallback offline.
 *
 * Usage: node render-plan.mjs [--repo <path>] [--out <file>]
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join, dirname } from 'node:path';

const args = process.argv.slice(2);
const opt = (f, d) => (args.includes(f) ? args[args.indexOf(f) + 1] : d);
const REPO = opt('--repo', process.cwd());
const OUT = opt('--out', join(REPO, '.harness', 'plan', 'plan.html'));

const read = (p) => { try { return readFileSync(p, 'utf8'); } catch { return null; } };
const readJson = (p) => { try { return JSON.parse(readFileSync(p, 'utf8')); } catch { return null; } };
const readJsonl = (p) => (read(p) ?? '').split('\n').filter(Boolean)
  .map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// ---- gather ground truth -----------------------------------------------------
const features = readJson(join(REPO, 'FEATURES.json'));
const blocks = readJson(join(REPO, '.harness', 'plan', 'blocks.json'))?.blocks ?? [];
const comments = readJsonl(join(REPO, '.harness', 'plan', 'comments.jsonl'));
const telemetry = readJsonl(join(REPO, '.harness', 'telemetry.jsonl'));
let gitLog = [];
try {
  gitLog = execFileSync('git', ['-C', REPO, 'log', '--oneline', '--no-decorate', '-15'], { encoding: 'utf8' })
    .trim().split('\n').filter(Boolean);
} catch {}

// ---- indexes & lint ----------------------------------------------------------
const feats = features?.features ?? [];
const featIds = new Set(feats.map((f) => f.id));
const blockIds = new Set();
const commentsByBlock = {};
for (const c of comments) (commentsByBlock[c.block] ??= []).push(c);
const openComments = comments.filter((c) => !c.resolved);
const blocksByFeature = {}; // reverse index for the board

const warnings = [];
for (const b of blocks) {
  if (!b.id) warnings.push(`block "${b.title ?? b.type}" has no id — comments cannot pin to it`);
  else if (blockIds.has(b.id)) warnings.push(`duplicate block id: ${b.id}`);
  else blockIds.add(b.id);
  for (const fid of b.features ?? []) {
    if (!featIds.has(fid)) warnings.push(`block ${b.id ?? b.type} cites unknown feature ${fid}`);
    else (blocksByFeature[fid] ??= []).push(b.id);
  }
  if (b.type === 'question' && !b.answer) warnings.push(`unanswered question in block ${b.id ?? '?'}`);
}
for (const c of comments) {
  if (c.block && !blockIds.has(c.block)) warnings.push(`comment ${c.id ?? '?'} pins to unknown block ${c.block}`);
}

// Features blocked by review: cited by an unresolved comment's block, or by the comment directly.
const blockedFeatures = new Set();
for (const c of openComments) {
  for (const fid of c.features ?? []) blockedFeatures.add(fid);
  const b = blocks.find((x) => x.id === c.block);
  for (const fid of b?.features ?? []) blockedFeatures.add(fid);
}
for (const b of blocks) if (b.type === 'question' && !b.answer) for (const fid of b.features ?? []) blockedFeatures.add(fid);

// ---- render helpers ----------------------------------------------------------
const chip = (cls, txt) => `<span class="chip ${cls}">${txt}</span>`;
const featChip = (f) => blockedFeatures.has(f.id) ? chip('blk', 'BLOCKED') : f.passes ? chip('pass', 'PASS') : chip('fail', 'OPEN');
const featLinks = (ids) => (ids ?? []).map((f) => `<a class="flink" href="#${f}">${f}</a>`).join(' ');

const renderThread = (bid) => {
  const cs = commentsByBlock[bid] ?? [];
  if (!cs.length) return '';
  return `<div class="thread">` + cs.map((c) => `
    <div class="cmt ${c.resolved ? 'resolved' : 'open'}">
      <span class="cmeta">${esc(c.author ?? 'reviewer')} · ${esc((c.created ?? '').slice(0, 10))} · ${c.resolved ? '✓ resolved' : '● OPEN'}</span>
      <div>${esc(c.text)}</div>
      ${c.answer ? `<div class="cans">↳ ${esc(c.answer)}</div>` : ''}
      ${c.resolved ? '' : `<form class="live rform" data-id="${esc(c.id)}"><input placeholder="resolve with an answer (required)…"><button>Resolve</button></form>`}
    </div>`).join('') + `</div>`;
};

// Per-block comment form — functional only when the page is SERVED (plan-serve.mjs);
// on file:// the script below swaps forms for the CLI hint, since a static page can't write.
const commentForm = (bid) => bid
  ? `<form class="live cform" data-block="${esc(bid)}"><input placeholder="pin a comment to ${esc(bid)}…"><button>Comment</button></form>`
  : '';

const renderBlock = (b) => {
  const bid = b.id ?? '';
  const open = (commentsByBlock[bid] ?? []).some((c) => !c.resolved) || (b.type === 'question' && !b.answer);
  const head = `<div class="bhead"><a class="bid" id="${esc(bid)}" href="#${esc(bid)}">${esc(bid)}</a><span class="btype">${esc(b.type)}</span><strong>${esc(b.title ?? '')}</strong>${featLinks(b.features)}</div>`;
  let body;
  switch (b.type) {
    case 'note': body = `<p>${esc(b.text)}</p>`; break;
    case 'diagram': body = `<div class="mermaid">${esc(b.source)}</div>`; break;
    case 'wireframe': body = `<pre class="wire">${esc(b.sketch)}</pre>${b.caption ? `<p class="cap">${esc(b.caption)}</p>` : ''}`; break;
    case 'decision':
      body = `<p><strong>Decision:</strong> ${esc(b.choice)}</p><p><strong>Why:</strong> ${esc(b.rationale)}</p>${(b.rejected ?? []).length ? `<p class="cap">Rejected: ${esc(b.rejected.join(' · '))}</p>` : ''}`; break;
    case 'annotated-code': {
      const src = read(join(REPO, b.file));
      if (!src) { body = `<p class="warn">⚠ file not found: ${esc(b.file)}</p>`; break; }
      const lines = src.split('\n');
      const notes = Object.fromEntries((b.annotations ?? []).map((a) => [a.line, a.note]));
      const nums = Object.keys(notes).map(Number);
      const lo = Math.max(1, Math.min(...nums) - 2), hi = Math.min(lines.length, Math.max(...nums) + 2);
      body = `<p class="cap">${esc(b.file)}</p><pre class="code">` + lines.slice(lo - 1, hi).map((ln, i) => {
        const n = lo + i;
        const note = notes[n] ? `  <span class="note">◀ ${esc(notes[n])}</span>` : '';
        return `<span class="${notes[n] ? 'hl' : ''}"><span class="ln">${String(n).padStart(4)}</span> ${esc(ln)}${note}</span>`;
      }).join('\n') + '</pre>'; break;
    }
    case 'question':
      body = `<p><strong>Q:</strong> ${esc(b.text)}</p><p>${b.answer ? `<strong>A:</strong> ${esc(b.answer)}` : '<em class="warn">UNANSWERED — blocks the features it cites</em>'}</p>`; break;
    default: body = `<p class="warn">unknown block type</p>`;
  }
  return `<div class="block ${open ? 'open-q' : ''}">${head}${body}${renderThread(bid)}${commentForm(bid)}</div>`;
};

// Sections: preserve authoring order; blocks without a section go to "Plan".
const sections = [];
for (const b of blocks) {
  const name = b.section ?? 'Plan';
  let s = sections.find((x) => x.name === name);
  if (!s) sections.push(s = { name, blocks: [] });
  s.blocks.push(b);
}

const passCount = feats.filter((f) => f.passes).length;
const nextFeature = feats.find((f) => !f.passes && !blockedFeatures.has(f.id));
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-');

const featureRows = feats.map((f) => `
  <div class="feat" id="${esc(f.id)}">
    <div>${featChip(f)} <strong>${esc(f.id)}</strong> <span class="cat">${esc(f.category ?? '')}</span>
      ${(blocksByFeature[f.id] ?? []).map((bid) => `<a class="flink" href="#${bid}">${bid}</a>`).join(' ')}</div>
    <div class="fdesc">${esc(f.description)}</div>
    ${f.evidence ? `<div class="fev">evidence: ${esc(f.evidence)}</div>` : ''}
    ${blockedFeatures.has(f.id) ? `<div class="fev warn">blocked by open review — see linked blocks</div>` : ''}
  </div>`).join('');

const verdictRows = telemetry.slice(-25).reverse().map((t) => `
  <tr><td>${esc((t.timestamp ?? t.date ?? '').slice(0, 16))}</td><td>${chip(t.status === 'pass' ? 'pass' : 'fail', esc((t.status ?? t.verdict ?? '?').toUpperCase()))}</td>
  <td>${esc(t.type ?? '')}</td><td>${esc(t.summary?.phase ?? t.phase ?? '')}</td><td class="cap">${esc(typeof t.summary === 'string' ? t.summary : JSON.stringify(t.summary ?? '').slice(0, 90))}</td></tr>`).join('');

const navItems = ['status', ...sections.map((s) => slug(s.name)), 'board', 'recap', 'history'];
const html = `<!doctype html><html><head><meta charset="utf-8"><title>Plan — ${esc(features?.project ?? REPO)} · ${esc(features?.phase ?? '')}</title>
<style>
  :root{--bg:#0f1115;--card:#181b22;--ink:#e6e6e6;--dim:#9aa3b2;--pass:#2ea06c;--fail:#c05a4e;--blk:#b3862d;--acc:#7aa2f7}
  body{background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,Segoe UI,sans-serif;margin:0;padding:0 2rem 3rem;max-width:1000px;margin-inline:auto}
  nav{position:sticky;top:0;background:var(--bg);padding:.7rem 0;border-bottom:1px solid #2a2f3a;z-index:9;display:flex;gap:1rem;flex-wrap:wrap}
  nav a{color:var(--dim);text-decoration:none;font-size:.85em;text-transform:capitalize} nav a:hover{color:var(--acc)}
  h1{font-size:1.35rem;margin:1.2rem 0 .2rem} h2{font-size:1.05rem;color:var(--acc);margin-top:2.4rem;border-bottom:1px solid #2a2f3a;padding-bottom:.3rem;text-transform:capitalize}
  .meta{color:var(--dim)} .chip{font:600 11px/1 monospace;padding:3px 7px;border-radius:9px;vertical-align:1px}
  .pass{background:var(--pass);color:#fff}.fail{background:var(--fail);color:#fff}.blk{background:var(--blk);color:#fff}
  .status{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.8rem;margin:1rem 0}
  .stat{background:var(--card);border-radius:8px;padding:.7rem 1rem}.stat .n{font-size:1.4rem;font-weight:700}.stat.alert{outline:2px solid var(--blk)}
  .feat,.block{background:var(--card);border-radius:8px;padding:.75rem 1rem;margin:.6rem 0}
  .block.open-q{outline:2px solid var(--fail)}
  .bhead{display:flex;gap:.6rem;align-items:center;margin-bottom:.4rem;flex-wrap:wrap}
  .bid{font:600 11px monospace;color:var(--dim);text-decoration:none}.bid:hover{color:var(--acc)}
  .btype{font:600 10px/1 monospace;background:#2a2f3a;color:var(--dim);padding:3px 6px;border-radius:6px;text-transform:uppercase}
  .flink{color:var(--acc);font:600 11px monospace;text-decoration:none}
  .cat{color:var(--dim);font-size:.85em}.fdesc{margin-top:.25rem}.fev{color:var(--dim);font-size:.85em;margin-top:.2rem}
  pre{overflow-x:auto;background:#10131a;border-radius:6px;padding:.7rem;font-size:12.5px}
  pre.wire{line-height:1.15;color:#b8c4d8} .cap{color:var(--dim);font-size:.85em}
  .code .ln{color:#4b5563}.code .hl{background:#1f2937;display:inline-block;width:100%}.code .note{color:#f0b429}
  .warn{color:#f0b429} table{border-collapse:collapse;width:100%;font-size:.88em} td{border-top:1px solid #2a2f3a;padding:.35rem .5rem;vertical-align:top}
  .banner{background:#3a2b1a;border:1px solid #f0b429;border-radius:8px;padding:.6rem 1rem;margin:1rem 0}
  .bar{height:8px;background:#2a2f3a;border-radius:4px;overflow:hidden;margin:.6rem 0}.bar>div{height:100%;background:var(--pass)}
  .thread{margin-top:.6rem;border-top:1px dashed #2a2f3a;padding-top:.5rem}
  .cmt{border-left:3px solid var(--dim);padding:.3rem .7rem;margin:.4rem 0;font-size:.92em}
  .cmt.open{border-color:var(--fail)}.cmt.resolved{border-color:var(--pass);opacity:.85}
  .cmeta{color:var(--dim);font-size:.8em}.cans{color:#b8e6c9;margin-top:.2rem}
  form.live{display:flex;gap:.4rem;margin-top:.5rem}
  form.live input{flex:1;background:#10131a;border:1px solid #2a2f3a;border-radius:6px;color:var(--ink);padding:.35rem .6rem;font-size:.88em}
  form.live button{background:var(--acc);color:#0f1115;border:0;border-radius:6px;padding:.35rem .8rem;font-weight:600;cursor:pointer;font-size:.85em}
  form.rform button{background:var(--pass);color:#fff}
  .filehint{display:none;color:var(--dim);font-size:.85em}
</style></head><body>
<nav>${navItems.map((n) => `<a href="#${n}">${n.replace(/-/g, ' ')}</a>`).join('')}</nav>
<h1 id="status">${esc(features?.project ?? 'plan')} — ${esc(features?.phase ?? 'no phase')}</h1>
<p class="meta">Derived from FEATURES.json · blocks.json · comments.jsonl · telemetry.jsonl · git — rendered ${new Date().toISOString().slice(0, 16).replace('T', ' ')}Z. Generated file: edit the sources, not this.</p>
<div class="bar"><div style="width:${feats.length ? Math.round(passCount / feats.length * 100) : 0}%"></div></div>
<div class="status">
  <div class="stat"><div class="n">${passCount}/${feats.length}</div>features passing</div>
  <div class="stat ${blockedFeatures.size ? 'alert' : ''}"><div class="n">${blockedFeatures.size}</div>blocked by review</div>
  <div class="stat ${openComments.length ? 'alert' : ''}"><div class="n">${openComments.length}</div>open comments</div>
  <div class="stat"><div class="n">${telemetry.length}</div>verdict rows</div>
</div>
<p class="meta"><strong>Next action:</strong> ${openComments.length
    ? `answer the ${openComments.length} open comment(s) — they block ${blockedFeatures.size} feature(s)`
    : nextFeature ? `build ${esc(nextFeature.id)} — ${esc(nextFeature.description).slice(0, 110)}`
    : feats.length && passCount === feats.length ? 'phase complete — run the verifier, close out' : 'seed FEATURES.json for this phase'}</p>
${warnings.length ? `<div class="banner"><strong>⚠ Plan lint:</strong><br>${warnings.map(esc).join('<br>')}</div>` : ''}
${sections.map((s) => `<h2 id="${slug(s.name)}">${esc(s.name)}</h2>${s.blocks.map(renderBlock).join('')}`).join('')}
${blocks.length ? '' : '<h2>Plan</h2><p class="meta">No blocks.json yet — the board below is still the plan\'s ground truth.</p>'}
<h2 id="board">Board <span class="cap">(FEATURES.json — the verifier grades this, not the blocks)</span></h2>
${featureRows || '<p class="meta">No FEATURES.json found.</p>'}
<h2 id="recap">Recap <span class="cap">(persisted verdicts, newest first — this section cannot lie)</span></h2>
${verdictRows ? `<table>${verdictRows}</table>` : '<p class="meta">No telemetry rows yet.</p>'}
<h2 id="history">History <span class="cap">(git, last 15)</span></h2>
<pre>${esc(gitLog.join('\n'))}</pre>
<p class="filehint">Read-only copy (opened from disk). To review interactively: <code>node plan-serve.mjs --repo &lt;repo&gt;</code> → http://localhost:4747 — or use <code>plan-comment.mjs</code> from the CLI.</p>
<script type="module">
  try {
    const m = await import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs');
    m.default.initialize({ startOnLoad: true, theme: 'dark' });
  } catch { /* offline: mermaid stays readable source */ }
</script>
<script>
  // Live review: forms work only when served (plan-serve.mjs). A file:// page
  // cannot write to the repo, so forms hide and the CLI hint shows instead.
  (function () {
    const served = location.protocol.startsWith('http');
    if (!served) {
      document.querySelectorAll('form.live').forEach((f) => f.remove());
      document.querySelector('.filehint').style.display = 'block';
      return;
    }
    const post = async (url, payload) => {
      const r = await fetch(url, { method: 'POST', body: JSON.stringify(payload) });
      if (!r.ok) { alert(await r.text()); return false; }
      return true;
    };
    document.querySelectorAll('form.cform').forEach((f) => f.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = f.querySelector('input').value;
      if (text.trim() && await post('/api/comment', { block: f.dataset.block, text })) location.reload();
    }));
    document.querySelectorAll('form.rform').forEach((f) => f.addEventListener('submit', async (e) => {
      e.preventDefault();
      const answer = f.querySelector('input').value;
      if (answer.trim() && await post('/api/resolve', { id: f.dataset.id, answer })) location.reload();
    }));
  })();
</script>
</body></html>`;

mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(OUT, html);
console.log(`plan rendered: ${OUT}
  features: ${passCount}/${feats.length} passing (${blockedFeatures.size} review-blocked) · blocks: ${blocks.length} · comments: ${comments.length} (${openComments.length} open) · verdicts: ${telemetry.length} · lint warnings: ${warnings.length}`);
