#!/usr/bin/env node
/**
 * plan-comment.mjs — the write channel for Conductor Visual Plans.
 *
 * Appends a review comment to .harness/plan/comments.jsonl (tracked in git —
 * comments are telemetry: the improver can mine what humans keep asking about).
 * An unresolved comment BLOCKS every feature its block cites; the builder's
 * get-bearings step must surface it, and resolves it with --resolve + --answer
 * once the plan/code answers it.
 *
 * Usage:
 *   node plan-comment.mjs --block <block-id> "comment text"       # reviewer
 *   node plan-comment.mjs --feature F-001 "comment text"          # pin to a feature directly
 *   node plan-comment.mjs --list [--open]                         # read the queue
 *   node plan-comment.mjs --resolve <comment-id> --answer "text"  # builder
 *   Options: --repo <path> (default cwd) · --author <name> (default $USER)
 */
import { readFileSync, writeFileSync, appendFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';

const args = process.argv.slice(2);
const opt = (f, d) => (args.includes(f) ? args[args.indexOf(f) + 1] : d);
const flag = (f) => args.includes(f);
const REPO = opt('--repo', process.cwd());
const FILE = join(REPO, '.harness', 'plan', 'comments.jsonl');

const rows = existsSync(FILE)
  ? readFileSync(FILE, 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l))
  : [];

// Ids come from the HIGHEST id ever used, not the row count: deleting a row
// makes a count-based counter reissue a live id, and a duplicate id can never be
// resolved (lookup only ever finds the first), so its features stay blocked
// forever. Monotonic ids make that impossible.
const nextId = (all) => {
  const highest = all.reduce((max, r) => {
    const n = Number(/^c-(\d+)$/.exec(r.id ?? '')?.[1] ?? 0);
    return Number.isFinite(n) ? Math.max(max, n) : max;
  }, 0);
  return `c-${String(highest + 1).padStart(3, '0')}`;
};

if (flag('--list')) {
  const shown = flag('--open') ? rows.filter((r) => !r.resolved) : rows;
  for (const r of shown) {
    console.log(`${r.resolved ? '✓' : '●'} ${r.id}  [${r.block ?? r.features?.join(',') ?? '-'}]  ${r.author}: ${r.text}${r.answer ? `\n    ↳ ${r.answer}` : ''}`);
  }
  console.log(`${shown.length} comment(s)${flag('--open') ? ' open' : ''}`);
  process.exit(0);
}

if (flag('--resolve')) {
  const id = opt('--resolve');
  const answer = opt('--answer');
  if (!answer) { console.error('A resolution needs --answer "text" — close is FAIL, silence is worse.'); process.exit(1); }
  // Resolve EVERY row with this id, not just the first: files written by older
  // versions can contain duplicates, and leaving the second one open would block
  // its features with no way to clear it.
  const matches = rows.filter((r) => r.id === id);
  if (!matches.length) { console.error(`no comment ${id}`); process.exit(1); }
  if (matches.length > 1) console.warn(`warning: ${matches.length} comments share id ${id} (legacy count-based ids) — resolving all of them.`);
  for (const row of matches) {
    row.resolved = true;
    row.answer = answer;
    row.resolvedAt = new Date().toISOString().slice(0, 10);
  }
  writeFileSync(FILE, rows.map((r) => JSON.stringify(r)).join('\n') + '\n');
  console.log(`resolved ${id}. Re-render the plan; commit comments.jsonl with the change that answers it.`);
  process.exit(0);
}

// append a new comment.
// Walk the args skipping each flag AND its value, rather than filtering by
// value — otherwise a comment whose text happens to equal a flag's value
// ("b-flow") gets silently dropped.
const VALUED = new Set(['--block', '--feature', '--repo', '--author', '--resolve', '--answer']);
const positional = [];
for (let i = 0; i < args.length; i++) {
  if (VALUED.has(args[i])) { i++; continue; }
  if (args[i].startsWith('--')) continue;
  positional.push(args[i]);
}
const text = positional.pop();
if (!text) { console.error('usage: plan-comment.mjs --block <id> "text"  (see header)'); process.exit(1); }
const row = {
  id: nextId(rows),
  block: opt('--block', null) || undefined,
  features: opt('--feature', null) ? [opt('--feature')] : undefined,
  author: opt('--author', process.env.USER || 'reviewer'),
  text,
  created: new Date().toISOString().slice(0, 10),
  resolved: false,
};
mkdirSync(dirname(FILE), { recursive: true });
appendFileSync(FILE, JSON.stringify(row) + '\n');
console.log(`added ${row.id} → ${FILE}. It now blocks the features its target cites; commit it so the builder sees it.`);
