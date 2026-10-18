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

The maintainer has not read the contract and has no reason to know what one is. So every question opens by saying **what their answer becomes** — the section it lands in, and what goes wrong when it is missing. Asked bare, these four read as a checklist of chores being handed back, and get answered with a shrug.

**Contract**, **transition**, **home**, **baseline**, **scar** are words for you. Met cold, they are jargon, and a person who cannot tell what category of thing is being asked about answers nothing at all. Name each in the maintainer's own terms the first time — a scar is *something that went wrong on a past release and cost you an afternoon*. Introduce the subject before the question, in one sentence, every time.

Four things the repo cannot tell you, and they are the reason this skill talks to a human at all:

- **What counts as validation here** — who checks what before it reaches users, and on which environment. A release run will later ask for this to be *declared*, so the contract has to say what a truthful answer looks like.
- **The version-meaning table** — present it filled and ask for corrections. Ask whether `v1.4.0` was really a MINOR; never ask what MINOR should mean.
- **Rollback** — the procedure, and whether it has ever actually been run. An untested rollback is an intention, and an incident is a bad place to find that out.
- **The scars** — what has already gone wrong here, written down so it stops costing anything. Nobody recognises their own scars under that name, so never ask openly: you will have found candidates in the deployment docs, the commit history and any local release skill, so **put them up as a list to confirm and extend**, each one in the maintainer's own terms — *"a `NEXT_PUBLIC_*` variable set at runtime stays inert: is that right, and what else has caught you out?"* Say in the same breath that you are recording these, not offering to fix them, or the list reads as work being handed back.

Everything else you found goes past them as a summary to correct. Every question carries your proposed answer; the maintainer's job is to correct it, not to compose it — a setup that interrogates is a setup nobody runs twice.

**Done when all four are answered and the summary has been corrected or accepted.**

## 4. Fix what can be fixed

Propose each one, apply the confirmed ones:

- A version home that disagrees with the line — bring it back in step.
- A `version` field frozen at the scaffold's default, in a repo that tags — sync it, and whatever reads it (health endpoint, Docker label, error reporter, footer) becomes true for free.
- A health endpoint that answers without naming the version it serves — that field is what turns "the tag says 1.6.0" into "production says 1.6.0", and it is what a release's verify step interrogates.
- `0.y.z` on something a third party already depends on — `0.x` announces *unstable, build nothing on this*. Where that is not what the repo means, the next release is `1.0.0`.
- Upstream tags mixed into a fork's line — settle the pattern that belongs to this project and record it.

Some of those write code. Run the repo's own build and lint over what you added, and read the warnings rather than the exit code — a version endpoint that compiles with a deprecation notice is a correction that will need doing twice.

**A version that already shipped never gets a tag or a release now.** Reconstructed from old merge commits, it is the one claim nobody can check and everybody will believe. Where a repo has no tags, the line opens at the first release and the contract says what came before is untraced.

**Done when every proposal is applied or declined, every code correction builds and lints clean, and no shipped version has been tagged after the fact.**

## 5. Write it and wire it

- `docs/RELEASING.md`, in the format of [CONTRACT.md](./CONTRACT.md).
- Where good release material already exists, the contract carries the block and **links** to it. Two copies of a rule become two different rules.
- A pointer in `CLAUDE.md` / `AGENTS.md`. This is what makes the contract reachable by any agent working in the repo, not only by a release run — and it is most of what stops releases from varying.
- **Delete** what the contract absorbed — a project-local release skill, a runbook whose rules now live in the contract. Deleted, not hollowed out into a launcher: a launcher is a third name for the same thing, maintained once per repo, and it drifts. The entry points are the pointer in `CLAUDE.md` and `/ship-release`, which is the same command in every repo. Material the contract only **links** to stays exactly where it is.
- **Verify the block against the repo**: every declared branch resolves, every version home exists. A contract written six months ago on a repo that has moved fails loudly rather than sending a release down a branch that is gone.

**Done when `docs/RELEASING.md` exists, its every declaration resolves, the pointer is in place, and superseded material is gone.**

Re-running on a repo that already has a contract updates it and keeps the deviations and scars already recorded. Those were paid for once.
