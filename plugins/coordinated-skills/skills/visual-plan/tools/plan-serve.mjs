#!/usr/bin/env node
/**
 * plan-serve.mjs — makes the plan page itself the review interface.
 *
 * A zero-dependency local server: every GET re-renders plan.html fresh from
 * ground truth (never stale), and the page's comment forms / resolve buttons
 * POST straight back here — landing in the SAME tracked
 * .harness/plan/comments.jsonl that plan-comment.mjs writes. Open a static
 * plan.html from disk and the forms hide themselves (file:// can't write);
 * serve it and the page is live. Commit comments.jsonl when you're done
 * reviewing — that commit is how the builder sees your review.
 *
 * Binds to 127.0.0.1 only and refuses cross-origin POSTs: this process writes
 * into your repo and renders your source, so it is not something to expose to
 * the network.
 *
 * Usage: node plan-serve.mjs [--repo <path>] [--port 4747]
 */
import { createServer } from 'node:http';
import { readFileSync, appendFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const opt = (f, d) => (args.includes(f) ? args[args.indexOf(f) + 1] : d);
const REPO = opt('--repo', process.cwd());
const PORT = Number(opt('--port', 4747));
const COMMENTS = join(REPO, '.harness', 'plan', 'comments.jsonl');
const TMP_OUT = join(REPO, '.harness', 'plan', '.plan-live.html');

const readRows = () => existsSync(COMMENTS)
  ? readFileSync(COMMENTS, 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l))
  : [];

// Same rule as plan-comment.mjs: ids come from the highest id ever used, never
// the row count, or deleting a row reissues a live id and the duplicate becomes
// unresolvable — blocking its features permanently.
const nextId = (all) => {
  const highest = all.reduce((max, r) => {
    const n = Number(/^c-(\d+)$/.exec(r.id ?? '')?.[1] ?? 0);
    return Number.isFinite(n) ? Math.max(max, n) : max;
  }, 0);
  return `c-${String(highest + 1).padStart(3, '0')}`;
};

// This server WRITES to a tracked file in the repo and serves a page containing
// live source excerpts, so it stays on the loopback interface and refuses
// cross-origin posts: without the Origin check any page open in the reviewer's
// browser could silently append comments (a JSON body sent as text/plain is a
// CORS "simple request" and is not preflighted).
const originOk = (req) => {
  const o = req.headers.origin;
  if (!o) return true; // curl / same-origin form posts send none
  return o === `http://localhost:${PORT}` || o === `http://127.0.0.1:${PORT}`;
};

const render = () => {
  execFileSync(process.execPath, [join(HERE, 'render-plan.mjs'), '--repo', REPO, '--out', TMP_OUT], { stdio: 'pipe' });
  return readFileSync(TMP_OUT, 'utf8');
};

const body = (req) => new Promise((res) => {
  let d = '';
  req.on('data', (c) => (d += c));
  req.on('end', () => { try { res(JSON.parse(d)); } catch { res({}); } });
});

createServer(async (req, res) => {
  try {
    if (req.method === 'GET') {
      res.writeHead(200, { 'content-type': 'text/html' });
      res.end(render());
      return;
    }
    if (req.method === 'POST' && !originOk(req)) {
      res.writeHead(403); res.end('cross-origin writes refused'); return;
    }
    if (req.method === 'POST' && req.url === '/api/comment') {
      const { block, feature, text, author } = await body(req);
      if (!text?.trim()) { res.writeHead(400); res.end('text required'); return; }
      const rows = readRows();
      const row = {
        id: nextId(rows),
        block: block || undefined,
        features: feature ? [feature] : undefined,
        author: (author || process.env.USER || 'reviewer').trim(),
        text: text.trim(),
        created: new Date().toISOString().slice(0, 10),
        resolved: false,
      };
      mkdirSync(dirname(COMMENTS), { recursive: true });
      appendFileSync(COMMENTS, JSON.stringify(row) + '\n');
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify(row));
      return;
    }
    if (req.method === 'POST' && req.url === '/api/resolve') {
      const { id, answer } = await body(req);
      if (!answer?.trim()) { res.writeHead(400); res.end('answer required — silent resolution is refused'); return; }
      const rows = readRows();
      // Resolve every row with this id — legacy files may hold duplicates.
      const matches = rows.filter((r) => r.id === id);
      if (!matches.length) { res.writeHead(404); res.end(`no comment ${id}`); return; }
      for (const row of matches) {
        row.resolved = true;
        row.answer = answer.trim();
        row.resolvedAt = new Date().toISOString().slice(0, 10);
      }
      writeFileSync(COMMENTS, rows.map((r) => JSON.stringify(r)).join('\n') + '\n');
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify(matches[0]));
      return;
    }
    res.writeHead(404); res.end();
  } catch (e) {
    res.writeHead(500); res.end(String(e?.message ?? e));
  }
}).listen(PORT, '127.0.0.1', () => {
  console.log(`plan live at http://localhost:${PORT} (repo: ${REPO}, loopback only)
  Comments and resolutions land in .harness/plan/comments.jsonl — commit it when done reviewing.`);
});
