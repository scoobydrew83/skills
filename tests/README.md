# tests/

The structural test suite for the skill library. `run-all.sh` is the entry
point CI runs — real, deterministic checks over the committed tree, no network
or API keys required:

```sh
bash tests/run-all.sh
```

It aggregates the two enforcement validators (`tools/validate-skill.sh --all`
and `tools/validate-agents.sh`) plus repo-shape invariants (every skill has a
`SKILL.md`, the generated `skill-graph.md` exists, CONVENTIONS.md keeps its
load-bearing sections). A green run reports `run-all: N checks · PASS`.
Tombstone WARNs are non-blocking.

`.cache/` and `.results/` under this directory are scratch space and stay
gitignored.
