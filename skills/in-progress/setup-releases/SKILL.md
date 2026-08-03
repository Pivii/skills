---
name: setup-releases
description: Write a repo's release contract — `docs/RELEASING.md`, the one document every release reads from. Use when someone wants their releases to stop varying run to run — "how do we release here?", "mets en place le process de release", "on n'a pas de doc de release", "standardise our releases" — or when a release run finds no contract. It reads the repo, drafts the whole contract, asks only what the repo cannot tell it, and fixes what it can safely fix.
---

# Set up releases

The **contract** is `docs/RELEASING.md`: one file that says how this repo releases, so the next release runs the same way whoever — or whatever — runs it.

You write it. Running it is the `/ship-release` skill's job.

Its format is [CONTRACT.md](./CONTRACT.md). Read that before drafting.

## 1. Read the ground

Every fact below is in the repo. Find it — none of it is a question for the maintainer.

```bash
git rev-parse --show-toplevel
gh repo view --json nameWithOwner,defaultBranchRef,hasIssuesEnabled
git branch -r
git remote -v
```

- **The repo's own instructions** — `CLAUDE.md`, `AGENTS.md`, `docs/`. What they already say about branches, releases and deployment.
- **Release material that already exists** — a versioning doc, a runbook, a `scripts/release*`, a project-local release skill under `.claude/skills/`. This is the most valuable thing you will find, and step 5 absorbs or points at it. Never recopy it.
- **The version line.** `git tag` is the wrong instrument: on a fork it returns the upstream's tags, and a diff computed from one of those is nonsense. Read the line from the forge's own releases, and confirm the tag pattern that belongs to *this* project.
- **Every home of the version number** — `package.json`, `Cargo.toml`, `tauri.conf.json`, `pubspec.yaml`, `Info.plist`, a constant in the source. Grep the current number; a home that disagrees with the tags is a finding, not a detail.
- **How reliably commits can be classified** — the conventional-commit rate over the last 300 commits, and whether `!` / `BREAKING CHANGE` is ever used. Both numbers go in the contract; they decide whether version derivation is trustworthy or merely indicative.
- **What already runs on its own** — CI workflows, what a tag triggers, how a deploy starts.
- **The language** its releases are written in.

**Done when you can state each of those and where you got it.**

## 2. Draft the whole contract

Classify the repo first — site, business app, mobile app, desktop tool, library — because the classification is what lets you propose rather than enquire.

Then fill **every** field of the contract, including the ones you are unsure of. A field you cannot settle carries your best proposal and a mark that it needs confirming; it never carries a blank.

The version-meaning table is the one to work hardest on. Go through the repo's own release history and attach **a real past release to each level** — `v1.4.0 — server rendering and per-URL i18n` says what MINOR means here in a way no definition can. Where a level has never happened (MAJOR, usually), say so and propose a plausible scenario for this repo.

**Done when the draft has no empty fields and every version level names a real release or a stated gap.**

## 3. Put the draft to the maintainer

Four things the repo cannot tell you, and they are the reason this skill talks to a human at all:

- **What counts as validation here** — who checks what before it reaches production, and on which environment. A release run will later ask for this to be *declared*, so the contract has to say what a truthful answer looks like.
- **The version-meaning table** — present it filled and ask for corrections. Ask whether `v1.4.0` was really a MINOR; never ask what MINOR should mean.
- **Rollback** — the procedure, and whether it has ever actually been run. If it has not, the contract says **untested** in as many words. A rollback nobody has performed is an intention, and finding that out during an incident is the whole cost.
- **The scars** — what has bitten someone here that no reading of the repo reveals. A build-time variable that needs a rebuild rather than a redeploy. A forge API call that fails and needs a REST fallback. A keyword the forge does not recognise. These never survive in anyone's head and they are what makes a contract worth more than a template.

Everything else you found goes past them as a summary to correct, not as questions.

**Ask nothing you could have looked up, and ask nothing blank.** Every question carries your proposed answer; the maintainer's job is to correct it, not to compose it. A setup that interrogates is a setup nobody runs twice.

**Done when all four are answered and the summary has been corrected or accepted.**

## 4. Fix what can be fixed

Propose each one, apply the confirmed ones:

- A version home that disagrees with the version line — bring it back in step.
- A `version` field frozen at the scaffold's default, in a repo that tags — it tells every reader something false. Sync it, and let whatever reads it (health endpoint, Docker label, error reporter, footer) become true for free.
- A health endpoint that answers without naming the version it serves — adding the field turns "the tag says 1.6.0" into "production says 1.6.0". It is what makes the verify step of a release mean anything.
- `0.y.z` on something a third party already depends on — `0.x` announces *unstable, build nothing on this*. If that is not what the repo means, the next release is `1.0.0`.
- Upstream tags mixed into a fork's line — settle the pattern that belongs to this project and record it.

**One thing you never do: create a tag or a release for a version that has already shipped.** Reconstructing a version history from old merge commits produces records that look exactly as authoritative as real ones and are not — nobody can now say what went out, when, or what was checked. On a repo with no tags, the line opens at the first release, and the contract says plainly that what came before is untraced.

**Done when every proposal is applied or declined, and nothing has been backdated.**

## 5. Write it and wire it

- `docs/RELEASING.md`, in the format of [CONTRACT.md](./CONTRACT.md).
- Where good release material already exists, the contract carries the structured block and **links** to it. Two copies of a rule become two different rules.
- A pointer in `CLAUDE.md` / `AGENTS.md`. This is what makes the contract reachable by any agent working in the repo, not only by a release run — and it is most of what stops releases from varying.
- Retire what the contract supersedes. A project-local release skill that has been absorbed stays behind as a second, drifting answer.
- **Verify the block against the repo**: every declared branch resolves, every version home exists. A contract written six months ago on a repo that has moved has to fail loudly rather than send a release down a branch that is gone.

**Done when `docs/RELEASING.md` exists, its every declaration resolves, the pointer is in place, and superseded material is gone.**

Re-running this skill on a repo that already has a contract updates it and keeps the deviations and scars already recorded. Those were paid for once.
