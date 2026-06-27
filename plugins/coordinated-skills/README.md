# coordinated-skills

A coordinated library of Claude skills. Each skill declares its lifecycle phase
and the siblings it hands off to, so the set composes into a workflow rather than
a pile of independent prompts.

The skills under `skills/` are the source of truth. See the
[repository](https://github.com/scoobydrew83/skills) for the conventions contract and tooling.

## Install

```
/plugin marketplace add scoobydrew83/skills
/plugin install coordinated-skills@scoobydrew-skills
```
