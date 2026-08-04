---
name: setup-releases
description: Release contract for a repo — writes `docs/RELEASING.md`, the file a release run reads from. Use when someone wants their releases set up or standardised ("mets en place le process de release", "how do we release here"), when the workflow has changed and the contract is stale, or when a release run finds no contract.
---

# Set up releases

The **contract** is `docs/RELEASING.md`: one file that says how this repo releases, so the next release runs the same way whoever — or whatever — runs it.

You write it. Running it is the `/ship-release` skill's job.

A contract earns that authority by **never making a claim it cannot back**. Where something is unchecked, it says so — and steps 3 and 4 are largely that discipline.

## 1. Read the ground

Every fact below is in the repo. Find it — none of it is a question for the maintainer.

```bash
git rev-parse --show-toplevel
gh repo view --json nameWithOwner,defaultBranchRef,hasIssuesEnabled
git branch -r
git remote -v
```

- **The repo's own instructions** — `CLAUDE.md`, `AGENTS.md`, `docs/`, for what they already say about branches, releases and deployment.
- **Release material that already exists** — a versioning doc, a runbook, a `scripts/release*`, a project-local release skill under `.claude/skills/`. The most valuable thing you will find, and step 5 absorbs or points at it rather than recopying it.
- **The version line** — its tag pattern, and its last release read from the forge rather than from `git tag`.
- **Every home of the version number** — `package.json`, `Cargo.toml`, `tauri.conf.json`, `pubspec.yaml`, `Info.plist`, a constant in the source. Grep the current number; a home that disagrees with the line is a finding.
- **The conventional-commit rate** over the last 300 commits, and whether `!` / `BREAKING CHANGE` ever appears.
- **What already runs on its own** — CI workflows, what a tag triggers, how a deploy starts.
- **The language** its releases are written in.

**Done when you can state each of those and where you got it.**

## 2. Draft the whole contract

Its format is [CONTRACT.md](./CONTRACT.md) — read it now, then fill **every** field, including the ones you are unsure of. A field you cannot settle carries your best proposal and a mark that it needs confirming; it never carries a blank.

Classify the repo first — site, business app, mobile app, desktop tool, library — because the classification is what lets you propose rather than enquire.

**Done when the draft has no empty fields and every version level names a real release of this repo or a stated gap.**

## 3. Put the draft to the maintainer

Four things the repo cannot tell you, and they are the reason this skill talks to a human at all:

- **What counts as validation here** — who checks what before it reaches users, and on which environment. A release run will later ask for this to be *declared*, so the contract has to say what a truthful answer looks like.
- **The version-meaning table** — present it filled and ask for corrections. Ask whether `v1.4.0` was really a MINOR; never ask what MINOR should mean.
- **Rollback** — the procedure, and whether it has ever actually been run. An untested rollback is an intention, and an incident is a bad place to find that out.
- **The scars** — what has bitten someone here that no reading of the repo reveals. A build-time variable a redeploy will not pick up. A forge call that needs a REST fallback. A closing keyword the forge ignores in this language. These never survive in anyone's head, and they are what makes a contract worth more than a template.

Everything else you found goes past them as a summary to correct. Every question carries your proposed answer; the maintainer's job is to correct it, not to compose it — a setup that interrogates is a setup nobody runs twice.

**Done when all four are answered and the summary has been corrected or accepted.**

## 4. Fix what can be fixed

Propose each one, apply the confirmed ones:

- A version home that disagrees with the line — bring it back in step.
- A `version` field frozen at the scaffold's default, in a repo that tags — sync it, and whatever reads it (health endpoint, Docker label, error reporter, footer) becomes true for free.
- A health endpoint that answers without naming the version it serves — that field is what turns "the tag says 1.6.0" into "production says 1.6.0", and it is what a release's verify step interrogates.
- `0.y.z` on something a third party already depends on — `0.x` announces *unstable, build nothing on this*. Where that is not what the repo means, the next release is `1.0.0`.
- Upstream tags mixed into a fork's line — settle the pattern that belongs to this project and record it.

**A version that already shipped never gets a tag or a release now.** Reconstructed from old merge commits, it is the one claim nobody can check and everybody will believe. Where a repo has no tags, the line opens at the first release and the contract says what came before is untraced.

**Done when every proposal is applied or declined, and no shipped version has been tagged after the fact.**

## 5. Write it and wire it

- `docs/RELEASING.md`, in the format of [CONTRACT.md](./CONTRACT.md).
- Where good release material already exists, the contract carries the block and **links** to it. Two copies of a rule become two different rules.
- A pointer in `CLAUDE.md` / `AGENTS.md`. This is what makes the contract reachable by any agent working in the repo, not only by a release run — and it is most of what stops releases from varying.
- Retire what the contract supersedes. An absorbed project-local skill left in place is a second, drifting answer.
- **Verify the block against the repo**: every declared branch resolves, every version home exists. A contract written six months ago on a repo that has moved fails loudly rather than sending a release down a branch that is gone.

**Done when `docs/RELEASING.md` exists, its every declaration resolves, the pointer is in place, and superseded material is gone.**

Re-running on a repo that already has a contract updates it and keeps the deviations and scars already recorded. Those were paid for once.
