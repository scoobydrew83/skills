# coordinated-skills

A coordinated library of portable, human-gated agent skills. The source of truth is the
repository's .agents/skills/ tree; this self-contained copy is generated for
Claude Marketplace compatibility.

The portable loop follows Orient → Frame → Authorize → Execute → Verify →
Review → Learn. Claude-specific commands are adapters; `AGENTS.md` and the
canonical skills remain the cross-runtime contract.

## Claude adapter commands

The plugin bundles `/coordinated-skills:conductor-loop`,
`/coordinated-skills:conductor-route`, and
`/coordinated-skills:conductor-doctor`. They use the installed plugin for
their scripts and operate on Claude's current project directory.

## Install

```
/plugin marketplace add scoobydrew83/skills
/plugin install coordinated-skills@scoobydrew-skills
```
