# Verification Sources

Where to check what. The rule: match the source to the *claim type*. Existence claims go to registries; capability and config claims go to the project's own docs/repo; Anthropic-product claims go to the official docs maps. Treat blog posts, SEO listicles, and "MCP directory" aggregators as leads to chase down at the source — never as the source itself, since many of them are themselves AI-generated and propagate the same errors.

## By claim type

| Claim type | Authoritative source | How |
|---|---|---|
| Package/crate exists + current version | Language registry | Use `scripts/verify_artifacts.py`, or hit the JSON endpoints below |
| Repo exists / is maintained / archived | GitHub API | `https://api.github.com/repos/<owner>/<repo>` (set `GITHUB_TOKEN` to avoid rate limits) |
| Tool capability / does-it-actually-do-X | Project's own README + docs site | Fetch the real page; don't infer capability from the name |
| Config keys / CLI flags / env vars | Official docs or `--help` | A key that appears nowhere in official docs is almost always invented |
| Anthropic product (Claude Code / API / Claude.ai) | Anthropic docs maps | See the dedicated section below — training data is stale here |
| MCP server specifics | `modelcontextprotocol/servers` + the server's own repo | Reference servers live in the official monorepo; everything else is community |
| "Best-practice pattern" / architecture claim | Independent corroboration | If only the generated text asserts it, treat as suspect |
| Effort / timeline | The official quickstart's real step list | Count actual dependencies; estimates that ignore them are fiction |

## Registry endpoints (return JSON; 404 = does not exist)

- **npm:** `https://registry.npmjs.org/<name>` → `dist-tags.latest` is the current version. Scoped names like `@scope/pkg` are fine.
- **PyPI:** `https://pypi.org/pypi/<name>/json` → `info.version`. Watch for near-miss names (`mem0` 404s; the real package is `mem0ai`).
- **crates.io:** `https://crates.io/api/v1/crates/<name>` → `crate.max_version`.
- **GitHub:** `https://api.github.com/repos/<owner>/<repo>` → 200 with `archived` flag and star count; 404 = no such repo.
- **Docker Hub:** `https://hub.docker.com/v2/repositories/<namespace>/<image>/`.
- **Go:** `https://pkg.go.dev/<module>` (HTML; 404 page is explicit).

The bundled `scripts/verify_artifacts.py` wraps npm/PyPI/crates/GitHub and exits non-zero if anything fails — prefer it for batches.

## Anthropic product claims — use these, not memory

Claude-product details (Claude Code flags, Actions behavior, API features, plan limits) drift fast and are a common source of confident-but-stale errors. Always verify against:

- **Claude API + general:** `https://docs.claude.com/en/docs_site_map.md`
- **Claude Code:** `https://docs.anthropic.com/en/docs/claude-code/claude_code_docs_map.md`
- **Claude Code GitHub Action (MCP support, inputs):** the `anthropics/claude-code-action` repo, `docs/` directory
- **Claude.ai (plans/limits):** `https://support.claude.com`

For anything touching these, the `product-self-knowledge` skill is the routing source of truth — defer to it.

## Confidence calibration

- **Resolved against a registry/official doc** → mark ✅ and cite the source.
- **Couldn't reach an authoritative source** (private tool, undisclosed setup, paywalled) → mark ⚠️ and say what's needed to confirm. Do not upgrade ⚠️ to ✅ on vibes.
- **Resolved to something that contradicts the claim** → mark ❌ and give the correction.
- **Only the generated text supports it, nothing else** → ❌ for fabricated patterns, or ⚠️ pending corroboration if it's merely unusual.
