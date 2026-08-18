#!/usr/bin/env node
/**
 * capture-plan.mjs — PostToolUse hook on ExitPlanMode.
 *
 * Claude Code's built-in plan mode emits its plan as markdown into the
 * terminal and forgets it. This hook catches every approved plan and lands it
 * in the visual-plan system: the raw markdown is preserved verbatim in
 * .harness/plan/captured/, and a `note` block referencing it is appended to
 * blocks.json tagged needs-structuring — so the next /vplan or /address-comments
 * session upgrades it to real blocks instead of the plan evaporating.
 *
 * Install (project .claude/settings.json):
 *   "hooks": { "PostToolUse": [ { "matcher": "ExitPlanMode",
 *     "hooks": [ { "type": "command", "command": "node tools/capture-plan.mjs" } ] } ] }
 *
 * Hook contract: JSON on stdin; { tool_name, tool_input: { plan } , cwd }.
 * Exit 0 always — a capture failure must never break planning (golden
 * principle #5: measurement never breaks the measured). "Never break planning"
 * is not "never say anything", though: failures print to stderr, because a hook
 * that silently no-ops makes the plan LOOK captured when it wasn't.
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';

try {
  const input = JSON.parse(readFileSync(0, 'utf8'));
  const plan = input?.tool_input?.plan;
  if (!plan) process.exit(0);

  const root = input?.cwd || process.cwd();
  const dir = join(root, '.harness', 'plan');
  const capDir = join(dir, 'captured');
  mkdirSync(capDir, { recursive: true });

  const stamp = new Date().toISOString().slice(0, 16).replace(/[:T]/g, '-');
  const mdFile = join(capDir, `plan-${stamp}.md`);
  writeFileSync(mdFile, plan);

  const blocksFile = join(dir, 'blocks.json');
  const doc = existsSync(blocksFile) ? JSON.parse(readFileSync(blocksFile, 'utf8')) : { blocks: [] };
  // Tolerate a blocks.json that predates this system (or has any other shape):
  // adding the key is non-destructive, and throwing here would strand a plan we
  // already wrote to disk.
  if (!Array.isArray(doc.blocks)) {
    console.error(`visual-plan: ${blocksFile} had no "blocks" array — adding one.`);
    doc.blocks = [];
  }
  const n = doc.blocks.filter((b) => b.id?.startsWith('b-captured-')).length + 1;
  doc.blocks.push({
    id: `b-captured-${String(n).padStart(2, '0')}`,
    type: 'note',
    section: 'Captured plans (needs structuring)',
    title: `Plan-mode capture ${stamp}`,
    features: [],
    text: `Approved via ExitPlanMode; full markdown preserved at .harness/plan/captured/plan-${stamp}.md. `
      + `First ~300 chars:\n\n${plan.slice(0, 300)}\n\n`
      + `TODO(next /vplan): structure this into real blocks — decisions, diagrams, questions — and delete this placeholder.`,
  });
  writeFileSync(blocksFile, JSON.stringify(doc, null, 2) + '\n');
  console.log(`visual-plan: captured approved plan → ${mdFile} (+ placeholder block b-captured-${String(n).padStart(2, '0')})`);
} catch (e) {
  // Never break planning — but never fail silently either.
  console.error(`visual-plan: plan capture FAILED — ${e?.message ?? e}`);
  console.error('  The approved plan was not recorded. Re-run /vplan to author it as blocks.');
}
process.exit(0);
