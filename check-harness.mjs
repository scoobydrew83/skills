#!/usr/bin/env node
/**
 * check-harness.mjs — the harness verified by its own pattern.
 *
 * Read-only verifier for HARNESS-FEATURES.json. Deterministic: every check is
 * a file/grep/version assertion against local clones of the three repos.
 *
 * Usage:
 *   node check-harness.mjs [--repos <dir>[,<dir>...]] [--json] [--update]
 *
 *   --repos  Comma-separated roots searched for clones of: sfdt, skills,
 *            sfdt-skills, agents, conductor-platform, studio-by-sfdt.
 *            Each root is searched at <root>/<repo> and <root>/repos/<repo>.
 *            Default: env HARNESS_REPOS or the checker's own directory.
 *   --json   Emit machine-readable results only.
 *   --update Flip passes/evidence in HARNESS-FEATURES.json to match observed
 *            reality (the ONLY writes this tool may make).
 *
 * A feature whose repo clone is absent reports SKIP and is never flipped.
 *
 * Exit codes: 0 = no drift; 1 = DRIFT (a feature marked passes:true failed);
 * 2 = setup error (no repos found at all).
 *
 * Verdict semantics (CONVENTIONS.md §5): a feature only counts as passing if
 * the check reproduces right now. "Close is FAIL."
 */
import { readFileSync, writeFileSync, existsSync, readdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const flag = (f) => args.includes(f);
const opt = (f, d) => (args.includes(f) ? args[args.indexOf(f) + 1] : d);

const ROOTS = opt('--repos', process.env.HARNESS_REPOS || HERE).split(',').map((s) => s.trim()).filter(Boolean);
const REPO_NAMES = ['sfdt', 'skills', 'sfdt-skills', 'agents', 'conductor-platform', 'studio-by-sfdt'];
const locate = (name) => {
  for (const root of ROOTS) for (const p of [join(root, name), join(root, 'repos', name)]) if (existsSync(p)) return p;
  return null;
};
const REPO = Object.fromEntries(REPO_NAMES.map((n) => [n, locate(n)]));
const SFDT = REPO['sfdt'], SKILLS = REPO['skills'], MIRROR = REPO['sfdt-skills'];
const AGENTS = REPO['agents'], PLATFORM = REPO['conductor-platform'], STUDIO = REPO['studio-by-sfdt'];

if (Object.values(REPO).every((p) => !p)) {
  console.error(`setup error: no repo clones found under roots: ${ROOTS.join(', ')} (use --repos)`);
  process.exit(2);
}
/** Which repo each feature needs; features whose repo is missing are SKIPped. */
const NEEDS = (id) => {
  const n = Number(id.slice(2));
  if ([1, 2, 3, 4, 11, 15].includes(n)) return SKILLS;
  if ([5, 6, 7, 8, 9, 10, 12, 13].includes(n)) return SFDT;
  if (n === 14) return MIRROR && SFDT;
  if (n >= 16 && n <= 20) return AGENTS;
  if (n >= 21 && n <= 25) return PLATFORM;
  if (n >= 26 && n <= 29) return STUDIO;
  return null;
};

const read = (p) => { try { return readFileSync(p, 'utf8'); } catch { return null; } };
const gitLs = (repo, path) => {
  try { return execFileSync('git', ['-C', repo, 'ls-files', path], { encoding: 'utf8' }).trim(); }
  catch { return ''; }
};
const grepRepo = (repo, needle) => {
  try {
    return execFileSync('grep', ['-rl', needle, repo, '--exclude-dir=.git'], { encoding: 'utf8' })
      .trim().split('\n').filter(Boolean);
  } catch { return []; } // grep exits 1 on no match
};
const findFile = (repo, name) => {
  const hits = [];
  const walk = (dir, depth) => {
    // Depth 5, not 3: skills live at plugins/<plugin>/skills/<name>/SKILL.md,
    // which is depth 4 — at depth 3 the H-015 SKILL.md clause was unreachable.
    if (depth > 5) return;
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      if (e.name === '.git' || e.name === 'node_modules') continue;
      const p = join(dir, e.name);
      if (e.isDirectory()) walk(p, depth + 1);
      else if (e.name === name) hits.push(p);
    }
  };
  walk(repo, 0);
  return hits;
};

/** Each check returns { pass: boolean, evidence: string } */
const BASELINE_LINTS = new Set([
  // sfdt tools/check-*.mjs present on the 2026-07-18 baseline read:
  'check-auth-docs.mjs', 'check-catalog-drift.mjs', 'check-license-consistency.mjs', 'check-node-version-consistency.mjs',
]);
const checks = {
  'H-001': () => {
    const f = gitLs(SKILLS, 'tests/');
    const pass = /run-all\.sh/.test(f);
    return { pass, evidence: pass ? 'tests/run-all.sh tracked by git' : 'tests/ not tracked (gitignored)' };
  },
  'H-002': () => {
    const hits = grepRepo(SKILLS, 'COORDINATION-STATUS');
    return { pass: hits.length === 0, evidence: hits.length ? `${hits.length} files still reference it` : 'no references remain' };
  },
  'H-003': () => {
    const tracked = gitLs(SKILLS, '.claude/scheduled_tasks.lock');
    return { pass: tracked === '', evidence: tracked ? 'lockfile still tracked' : 'lockfile untracked' };
  },
  'H-004': () => {
    const p = join(SKILLS, 'tools', 'validate-agents.sh');
    return { pass: existsSync(p), evidence: existsSync(p) ? p : 'tools/validate-agents.sh absent' };
  },
  'H-005': () => {
    const src = read(join(SFDT, 'src/lib/agent-loop.js')) || '';
    const pass = src.includes('recordRun') && src.includes('agent-fix');
    return { pass, evidence: pass ? 'agent-loop.js records agent-fix runs' : 'runFixLoop outcomes still evaporate' };
  },
  'H-006': () => {
    const p = join(SFDT, 'tools', 'record-verdict.mjs');
    return { pass: existsSync(p), evidence: existsSync(p) ? p : 'tools/record-verdict.mjs absent' };
  },
  'H-007': () => {
    const p = join(SFDT, 'FEATURES.json');
    return { pass: existsSync(p), evidence: existsSync(p) ? p : 'FEATURES.json absent' };
  },
  'H-008': () => {
    const src = read(join(SFDT, 'CLAUDE.md')) || '';
    const lines = src.split('\n').length;
    return { pass: lines <= 100, evidence: `CLAUDE.md is ${lines} lines (target <=100)` };
  },
  'H-009': () => {
    const p = join(SFDT, 'docs', 'golden-principles.md');
    return { pass: existsSync(p), evidence: existsSync(p) ? p : 'docs/golden-principles.md absent' };
  },
  'H-010': () => {
    const toolsDir = join(SFDT, 'tools');
    const lints = existsSync(toolsDir)
      ? readdirSync(toolsDir).filter((f) => /^check-.*\.mjs$/.test(f) && !BASELINE_LINTS.has(f))
      : [];
    const pkg = read(join(SFDT, 'package.json')) || '';
    const wired = lints.filter((l) => pkg.includes(l.replace(/\.mjs$/, '').replace(/^check-/, 'check:')) || pkg.includes(l));
    const pass = lints.length > 0 && wired.length > 0;
    return { pass, evidence: pass ? `new lint(s): ${wired.join(', ')}` : 'no new lint beyond 2026-07-18 baseline wired into package.json' };
  },
  'H-011': () => {
    const wanted = ['harness-improver.md', 'doc-gardener.md', 'slop-gc.md'];
    const found = wanted.filter((w) => findFile(SKILLS, w).length > 0);
    return { pass: found.length === 3, evidence: `found ${found.length}/3: ${found.join(', ') || 'none'}` };
  },
  'H-012': () => {
    const p = join(SFDT, '.github/workflows/harness-improver.yml');
    return { pass: existsSync(p), evidence: existsSync(p) ? p : 'workflow absent' };
  },
  'H-013': () => ({ pass: false, evidence: 'MANUAL: verify via `sfdt history --type gc --json` + the cited PR; this checker cannot see the db' }),
  'H-014': () => {
    const readme = read(join(MIRROR, 'README.md')) || '';
    const pkg = JSON.parse(read(join(SFDT, 'package.json')) || '{}');
    const m = readme.match(/Synced from `@sfdt\/cli` v(\d+\.\d+\.\d+)/);
    const pass = !!m && m[1] === pkg.version;
    return { pass, evidence: `mirror says v${m ? m[1] : '?'} vs cli v${pkg.version || '?'}` };
  },
  'H-015': () => {
    const hits = findFile(SKILLS, 'SKILL.md').filter((p) => p.includes('conductor-init'))
      .concat(findFile(SKILLS, 'conductor-init.md'));
    return { pass: hits.length > 0, evidence: hits[0] || 'no conductor-init in skills repo' };
  },
  // --- agents repo ---
  'H-016': () => {
    const ci = read(join(AGENTS, '.github/workflows/ci.yml')) || '';
    let branch = '';
    try { branch = execFileSync('git', ['-C', AGENTS, 'rev-parse', '--abbrev-ref', 'HEAD'], { encoding: 'utf8' }).trim(); } catch {}
    const pushBlock = ci.split(/pull_request/)[0];
    const pass = !!branch && pushBlock.includes(branch);
    return { pass, evidence: pass ? `push CI covers branch '${branch}'` : `branch '${branch || '?'}' not in ci.yml push triggers` };
  },
  'H-017': () => {
    const hits = grepRepo(AGENTS, '222 tests');
    return { pass: hits.length === 0, evidence: hits.length ? `stale '222 tests' in ${hits.length} file(s)` : 'stale count gone' };
  },
  'H-018': () => {
    const readme = read(join(AGENTS, 'README.md')) || '';
    const versions = read(join(AGENTS, 'agent-os/product/versions.yml')) || '';
    const rm = readme.match(/Salesforce API[^\d]*(\d+\.\d+)/);
    const vm = versions.match(/api_version:\s*"?(\d+\.\d+)"?/);
    const pass = !!rm && !!vm && rm[1] === vm[1];
    return { pass, evidence: `README says ${rm ? rm[1] : '?'}, versions.yml says ${vm ? vm[1] : '?'}` };
  },
  'H-019': () => {
    const hits = grepRepo(AGENTS, 'claude-opus-4-5-20251101');
    return { pass: hits.length === 0, evidence: hits.length ? `dead pinned model in ${hits.length} file(s)` : 'no dead model pins' };
  },
  'H-020': () => {
    const script = findFile(AGENTS, 'validate-agents.py').concat(findFile(AGENTS, 'validate-agents.sh'), findFile(AGENTS, 'validate-agents.mjs'));
    const ci = read(join(AGENTS, '.github/workflows/ci.yml')) || '';
    const pass = script.length > 0 && ci.includes('validate-agents');
    return { pass, evidence: pass ? `${script[0]} wired into CI` : 'no validate-agents script wired into ci.yml' };
  },
  // --- conductor-platform ---
  'H-021': () => {
    const src = read(join(PLATFORM, 'CLAUDE.md')) || '';
    const lines = src.split('\n').length;
    return { pass: lines <= 100, evidence: `CLAUDE.md is ${lines} lines (target <=100)` };
  },
  'H-022': () => {
    const bad = ['CLAUDE.md', 'README.md', 'MEMORY_BANK.md'].filter((f) => /celery/i.test(read(join(PLATFORM, f)) || ''));
    return { pass: bad.length === 0, evidence: bad.length ? `Celery still cited in ${bad.join(', ')}` : 'no stale Celery references' };
  },
  'H-023': () => {
    const p = join(PLATFORM, 'DATABASE_SCHEMA.sql');
    if (!existsSync(p)) return { pass: true, evidence: 'schema doc removed (models/migrations are source of truth)' };
    const pass = (read(p) || '').includes('workflow_runs');
    return { pass, evidence: pass ? 'schema doc includes migration-era tables' : 'DATABASE_SCHEMA.sql omits workflow_runs etc. (stale)' };
  },
  'H-024': () => {
    const hits = [...grepRepo(join(PLATFORM, 'apps/api/src'), '/home/drew'), ...grepRepo(join(PLATFORM, 'apps/api/tests'), '/home/drew')];
    return { pass: hits.length === 0, evidence: hits.length ? `hardcoded /home/drew in ${hits.length} backend src/test file(s)` : 'backend src+tests path-clean' };
  },
  'H-025': () => {
    const src = read(join(PLATFORM, 'MEMORY_BANK.md')) || '';
    const pass = /^- 20\d\d-\d\d-\d\d/m.test(src);
    return { pass, evidence: pass ? 'MEMORY_BANK has dated line entries' : 'MEMORY_BANK has no dated line-format entries (CONVENTIONS §4)' };
  },
  // --- studio-by-sfdt ---
  'H-026': () => {
    const lock = read(join(STUDIO, 'package-lock.json')) || '';
    const pass = /"node_modules\/(playwright|@playwright\/|puppeteer)/.test(lock);
    return { pass, evidence: pass ? 'browser automation dependency installed' : 'no Playwright/Puppeteer installed — jsdom only' };
  },
  'H-027': () => {
    const pass = !/\/home\/drew/.test(read(join(STUDIO, 'README.md')) || '');
    return { pass, evidence: pass ? 'README path-clean' : 'README still hardcodes /home/drew paths' };
  },
  'H-028': () => {
    const src = read(join(STUDIO, 'scripts/dev.mjs')) || '';
    const pass = src.includes('process.env');
    return { pass, evidence: pass ? 'dev.mjs reads env for config' : 'dev.mjs hardcodes ports 5174/4175 (worktrees collide)' };
  },
  'H-029': () => {
    const p = join(STUDIO, 'FEATURES.json');
    return { pass: existsSync(p), evidence: existsSync(p) ? p : 'FEATURES.json absent' };
  },
};

const featuresPath = join(HERE, 'HARNESS-FEATURES.json');
const doc = JSON.parse(readFileSync(featuresPath, 'utf8'));
let drift = 0;
const results = [];

for (const f of doc.features) {
  if (!NEEDS(f.id)) {
    results.push({ id: f.id, claimed: f.passes, observed: null, status: 'SKIP', evidence: 'repo clone not found under given roots', description: f.description });
    continue;
  }
  const check = checks[f.id];
  const r = check ? check() : { pass: false, evidence: 'no check implemented' };
  const status = r.pass ? 'PASS' : f.passes ? 'DRIFT' : 'FAIL';
  if (status === 'DRIFT') drift++;
  results.push({ id: f.id, claimed: f.passes, observed: r.pass, status, evidence: r.evidence, description: f.description });
  if (flag('--update')) {
    f.passes = r.pass;
    f.evidence = r.pass ? `${new Date().toISOString().slice(0, 10)}: ${r.evidence}` : null;
  }
}

if (flag('--update')) writeFileSync(featuresPath, JSON.stringify(doc, null, 2) + '\n');

if (flag('--json')) {
  console.log(JSON.stringify({ drift, passing: results.filter((r) => r.observed).length, total: results.length, results }, null, 2));
} else {
  for (const r of results) console.log(`${r.status.padEnd(5)} ${r.id}  ${r.evidence}`);
  const passing = results.filter((r) => r.observed).length;
  console.log(`\n${passing}/${results.length} passing · drift: ${drift}${flag('--update') ? ' · HARNESS-FEATURES.json updated' : ''}`);
}
process.exit(drift > 0 ? 1 : 0);
