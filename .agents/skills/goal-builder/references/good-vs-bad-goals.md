# Good vs bad goals — worked examples

The recurring mistake: writing a **prompt** (open-ended, a human decides if it's good enough) when
`/goal` needs a **condition** (resolves to yes/no from the transcript). Use these to calibrate the
interview and to show the user the shape of a fixed goal.

## Prompt → condition

**Bad (a prompt):** `/goal clean up the code in src/`
Why it fails: "clean" isn't observable. The evaluator has no command to run, no output that flips
no→yes. The loop churns or quietly stops.

**Good (a condition):**
`/goal npx eslint src/ reports 0 errors and 0 warnings, and npm test exits 0, without adding any eslint-disable comments — or stop after 15 turns`
Why it works: two concrete checks whose output prints to the transcript, a cheat-closing
constraint, and a cap.

---

**Bad:** `/goal make the API faster`
**Good:** `/goal the benchmark script ./bench.sh prints "p95 < 200ms" on its final line, without lowering the request count in bench.sh — or stop after 20 turns`

---

**Bad:** `/goal finish the migration`
**Good:** `/goal rg "from 'old-sdk'" src has zero matches and npm run build exits 0, without editing files under src/vendor — or stop after 30 turns`

## The cheat door (reward hacking)

A check alone isn't enough; name what would game it. From the article's worked example, the goal
that survived was effectively:

`/goal running "javac Zoo.java ZooTest.java && java ZooTest" exits 0, without modifying ZooTest.java and without hardcoding the printed lines — the output must come from the Zoo constructor's distribution logic`

The constraints are doing real work: without them, the cheapest way to "pass" is to print the five
expected lines and skip the actual logic. Every goal that touches tests or fixed output needs this
kind of guard:
- "without modifying the test file"
- "without hardcoding / stubbing the expected values"
- "no test is skipped, disabled, or deleted"
- "without weakening assertions"

## Compound → sequential

**Bad (one overloaded goal):**
`/goal redesign auth, add OAuth, write tests, and update the docs`
The evaluator can't get a clean yes/no on four different things at once; it flip-flops.

**Good (run one at a time, each its own goal):**
1. `/goal the new auth module exposes login()/logout()/refresh() and npm test -- auth exits 0, without touching the existing session schema — or stop after 25 turns`
2. `/goal the OAuth flow test tests/oauth.test.ts passes and npm test exits 0, without modifying tests/oauth.test.ts — or stop after 25 turns`
3. `/goal npm run docs:check exits 0 with the auth section present — or stop after 10 turns`

## Quick checklist the interview is driving toward

- [ ] End state is observable, not an adjective.
- [ ] There's a named check whose output Claude will print to the transcript.
- [ ] Constraints close the obvious cheat paths.
- [ ] It's a single end state (compound work is split into sequential goals).
- [ ] There's a turn/time cap.
- [ ] Under 4,000 characters.

## When /goal is the wrong tool

If there's genuinely no transcript-checkable finish line — "make the design feel modern," "improve
readability" — don't force a goal. Say so, and point to the alternative: a normal prompt with human
review, or a deterministic Stop hook if there's a fixed per-turn command to run.
